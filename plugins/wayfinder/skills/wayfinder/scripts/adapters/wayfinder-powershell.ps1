#!/usr/bin/env pwsh
# Wayfinder executable-contract adapter for PowerShell 7.4+.
# This implementation intentionally uses only PowerShell and .NET standard facilities.

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'

$script:AdapterId = 'powershell-v1'
$script:AdapterRelativePath = 'scripts/adapters/wayfinder-powershell.ps1'
$script:SkillRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($PSScriptRoot))
$script:ContractRoot = [IO.Path]::Combine($script:SkillRoot,'assets/contract-v1')
$script:Utf8Strict = [System.Text.UTF8Encoding]::new($false, $true)
$script:Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$script:JsonStringOptions = [System.Text.Json.JsonSerializerOptions]::new()
$script:JsonStringOptions.Encoder = [System.Text.Encodings.Web.JavaScriptEncoder]::UnsafeRelaxedJsonEscaping
$script:ExitCode = 0

class WayfinderFailure : System.Exception {
    [int]$ExitClass
    [string]$StableCode
    [System.Collections.IDictionary]$Details
    WayfinderFailure([int]$exitClass, [string]$stableCode, [string]$message, [System.Collections.IDictionary]$details) : base($message) {
        $this.ExitClass = $exitClass
        $this.StableCode = $stableCode
        $this.Details = $details
    }
}

function Throw-Wf {
    param([int]$ExitClass, [string]$Code, [string]$Message, [System.Collections.IDictionary]$Details = $null)
    if ($null -eq $Details) { $Details = [ordered]@{} }
    throw [WayfinderFailure]::new($ExitClass, $Code, $Message, $Details)
}

function New-WfObject { [ordered]@{} }

function Get-WfPropertyNames {
    param($Value)
    if ($Value -is [System.Collections.IDictionary]) { return @($Value.Keys | ForEach-Object { [string]$_ }) }
    return @()
}

function Test-WfHas {
    param($Value, [string]$Name)
    return ($Value -is [System.Collections.IDictionary]) -and $Value.Contains($Name)
}

function Assert-WfClosedObject {
    param($Value, [string[]]$Required, [string[]]$Allowed = $Required, [int]$ExitClass = 2)
    if ($Value -isnot [System.Collections.IDictionary]) { Throw-Wf $ExitClass 'json.type' 'Expected a JSON object.' }
    foreach ($name in $Required) {
        if (-not $Value.Contains($name)) { Throw-Wf $ExitClass 'json.missing-field' "Missing required field: $name" ([ordered]@{ field = $name }) }
    }
    foreach ($name in @($Value.Keys)) {
        if ($Allowed -notcontains [string]$name) { Throw-Wf $ExitClass 'json.unknown-field' "Unknown field: $name" ([ordered]@{ field = [string]$name }) }
    }
}

function Assert-WfArray {
    param($Value, [int]$ExitClass = 2)
    if ($Value -is [string] -or $Value -is [System.Collections.IDictionary] -or $Value -isnot [System.Collections.IList]) {
        Throw-Wf $ExitClass 'json.type' 'Expected a JSON array.'
    }
}

function ConvertFrom-WfElement {
    param([System.Text.Json.JsonElement]$Element, [int]$ExitClass)
    switch ($Element.ValueKind) {
        'Object' {
            $result = [ordered]@{}
            foreach ($property in $Element.EnumerateObject()) {
                if ($result.Contains($property.Name)) { Throw-Wf $ExitClass 'json.duplicate-key' "Duplicate JSON object name: $($property.Name)" ([ordered]@{ field = $property.Name }) }
                $result[$property.Name] = ConvertFrom-WfElement $property.Value $ExitClass
            }
            return $result
        }
        'Array' {
            $items = [System.Collections.ArrayList]::new()
            foreach ($item in $Element.EnumerateArray()) { [void]$items.Add((ConvertFrom-WfElement $item $ExitClass)) }
            return ,$items
        }
        'String' {
            $value = $Element.GetString()
            if (-not $value.IsNormalized([System.Text.NormalizationForm]::FormC)) { Throw-Wf $ExitClass 'text.non-nfc' 'JSON strings must use NFC normalization.' }
            return $value
        }
        'Number' {
            $raw = $Element.GetRawText()
            if ($raw -notmatch '^(?:0|-[1-9][0-9]*|[1-9][0-9]*)$' -or $raw -eq '-0') { Throw-Wf $ExitClass 'json.number' 'JSON numbers must be version-1 integers.' }
            [Int64]$value = 0
            if (-not [Int64]::TryParse($raw, [Globalization.NumberStyles]::AllowLeadingSign, [Globalization.CultureInfo]::InvariantCulture, [ref]$value) -or [Math]::Abs([decimal]$value) -gt 9007199254740991) {
                Throw-Wf $ExitClass 'json.number' 'JSON integer is outside the exact version-1 range.'
            }
            return $value
        }
        'True' { return $true }
        'False' { return $false }
        'Null' { return $null }
        default { Throw-Wf $ExitClass 'json.invalid' 'Unsupported JSON token.' }
    }
}

function Read-WfJsonBytes {
    param([byte[]]$Bytes, [int]$ExitClass = 2, [switch]$ManifestText)
    if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) { Throw-Wf $ExitClass 'text.bom' 'UTF-8 BOM is forbidden.' }
    try { $text = $script:Utf8Strict.GetString($Bytes) } catch { Throw-Wf $ExitClass 'text.invalid-utf8' 'Input is not strict UTF-8.' }
    if ($text.Contains("`r")) { Throw-Wf $ExitClass 'text.newline' 'CR and CRLF newlines are forbidden.' }
    for ($index = 0; $index -lt $text.Length; $index++) {
        if ($text[$index] -ne '\') { continue }
        $runEnd = $index
        while ($runEnd -lt $text.Length -and $text[$runEnd] -eq '\') { $runEnd++ }
        $runLength = $runEnd - $index
        if (($runLength % 2) -eq 1 -and $runEnd + 4 -lt $text.Length -and $text[$runEnd] -eq 'u') {
            $hex = $text.Substring($runEnd + 1, 4)
            [uint16]$codeUnit = 0
            if ([uint16]::TryParse($hex, [Globalization.NumberStyles]::AllowHexSpecifier, [Globalization.CultureInfo]::InvariantCulture, [ref]$codeUnit)) {
                if ($codeUnit -ge 0xD800 -and $codeUnit -le 0xDBFF) {
                    $lowSlash = $runEnd + 5
                    if ($lowSlash + 5 -ge $text.Length -or $text[$lowSlash] -ne '\' -or $text[$lowSlash + 1] -ne 'u') {
                        Throw-Wf $ExitClass 'text.invalid-unicode' 'JSON contains malformed Unicode.'
                    }
                    [uint16]$lowUnit = 0
                    $lowHex = $text.Substring($lowSlash + 2, 4)
                    if (-not [uint16]::TryParse($lowHex, [Globalization.NumberStyles]::AllowHexSpecifier, [Globalization.CultureInfo]::InvariantCulture, [ref]$lowUnit) -or $lowUnit -lt 0xDC00 -or $lowUnit -gt 0xDFFF) {
                        Throw-Wf $ExitClass 'text.invalid-unicode' 'JSON contains malformed Unicode.'
                    }
                    $index = $lowSlash + 5
                    continue
                }
                if ($codeUnit -ge 0xDC00 -and $codeUnit -le 0xDFFF) {
                    Throw-Wf $ExitClass 'text.invalid-unicode' 'JSON contains malformed Unicode.'
                }
            }
        }
        $index = $runEnd - 1
    }
    try {
        $options = [System.Text.Json.JsonDocumentOptions]::new()
        $options.AllowTrailingCommas = $false
        $options.CommentHandling = [System.Text.Json.JsonCommentHandling]::Disallow
        $memory = [ReadOnlyMemory[byte]]::new($Bytes)
        $document = [System.Text.Json.JsonDocument]::Parse($memory, $options)
    } catch [System.Text.Json.JsonException] {
        $message = $_.Exception.Message
        if ($message -match 'surrogate|Unicode|UTF-16') { Throw-Wf $ExitClass 'text.invalid-unicode' 'JSON contains malformed Unicode.' }
        Throw-Wf $ExitClass 'json.invalid' 'Malformed JSON.'
    }
    try { return ConvertFrom-WfElement $document.RootElement $ExitClass } finally { $document.Dispose() }
}

function Read-WfJsonFile {
    param([string]$Path, [int]$ExitClass = 2, [switch]$ManifestText)
    if (-not [IO.File]::Exists($Path)) { Throw-Wf $ExitClass 'file.missing' "Required file is missing: $Path" ([ordered]@{ path = $Path }) }
    return Read-WfJsonBytes ([IO.File]::ReadAllBytes($Path)) $ExitClass -ManifestText:$ManifestText
}

function ConvertTo-WfJsonInternal {
    param($Value, [bool]$SortKeys)
    if ($null -eq $Value) { return 'null' }
    if ($Value -is [bool]) { if ($Value) { return 'true' } else { return 'false' } }
    if ($Value -is [string]) { return [System.Text.Json.JsonSerializer]::Serialize([string]$Value, $script:JsonStringOptions) }
    if ($Value -is [char]) { return [System.Text.Json.JsonSerializer]::Serialize([string]$Value, $script:JsonStringOptions) }
    if ($Value -is [byte] -or $Value -is [sbyte] -or $Value -is [int16] -or $Value -is [uint16] -or $Value -is [int32] -or $Value -is [uint32] -or $Value -is [int64]) {
        return [Convert]::ToString($Value, [Globalization.CultureInfo]::InvariantCulture)
    }
    if ($Value -is [System.Collections.IDictionary]) {
        $keys = @($Value.Keys | ForEach-Object { [string]$_ })
        if ($SortKeys) { [Array]::Sort($keys, [StringComparer]::Ordinal) }
        $parts = foreach ($key in $keys) {
            (ConvertTo-WfJsonInternal $key $SortKeys) + ':' + (ConvertTo-WfJsonInternal $Value[$key] $SortKeys)
        }
        return '{' + ($parts -join ',') + '}'
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        $parts = foreach ($item in $Value) { ConvertTo-WfJsonInternal $item $SortKeys }
        return '[' + ($parts -join ',') + ']'
    }
    Throw-Wf 70 'internal.unexpected' "Cannot serialize value of type $($Value.GetType().FullName)."
}

function ConvertTo-WfCanonicalJson { param($Value) ConvertTo-WfJsonInternal $Value $true }
function ConvertTo-WfDisplayJson { param($Value) ConvertTo-WfJsonInternal $Value $false }

function Get-WfSha256Bytes {
    param([byte[]]$Bytes)
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant()
}
function Get-WfSha256Text { param([string]$Text) Get-WfSha256Bytes $script:Utf8NoBom.GetBytes($Text) }
function Get-WfSha256File { param([string]$Path) Get-WfSha256Bytes ([IO.File]::ReadAllBytes($Path)) }

function Write-WfBytesExclusive {
    param([string]$Path, [byte[]]$Bytes)
    $stream = [IO.FileStream]::new($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($Bytes); $stream.Flush($true) } finally { $stream.Dispose() }
}

function Write-WfBytesReplace {
    param([string]$Path, [byte[]]$Bytes)
    $parent = Split-Path $Path -Parent
    $temporary = Join-Path $parent ('.wayfinder-tmp-' + [Guid]::NewGuid().ToString('N'))
    try {
        Write-WfBytesExclusive $temporary $Bytes
        [IO.File]::Move($temporary, $Path, $true)
    } finally {
        if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }
    }
}

function New-WfDiagnostic {
    param([WayfinderFailure]$Failure)
    $diagnostic = [ordered]@{ code = $Failure.StableCode; message = $Failure.Message }
    foreach ($name in @('path','field','expected','actual','remediation')) {
        if ($Failure.Details.Contains($name)) { $diagnostic[$name] = $Failure.Details[$name] }
    }
    return $diagnostic
}

function Write-WfResult {
    param([string]$Command, [bool]$Ok, [string]$Code, [System.Collections.IDictionary]$Data, [object[]]$Diagnostics, [int]$ExitClass)
    $result = [ordered]@{
        format = 'wayfinder-command-result'
        schemaVersion = 1
        ok = $Ok
        command = $Command
        code = $Code
        data = $Data
        diagnostics = [System.Collections.ArrayList]@($Diagnostics)
    }
    [Console]::Out.Write((ConvertTo-WfDisplayJson $result) + "`n")
    if (-not $Ok) { [Console]::Error.WriteLine("$Code`: $($Diagnostics[0].message)") }
    $script:ExitCode = $ExitClass
}

function Resolve-WfPhysicalPath {
    param([string]$Path)
    try {
        $full = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path)
        $root = [IO.Path]::GetPathRoot($full)
        $cursor = $root
        foreach ($segment in $full.Substring($root.Length).Split([IO.Path]::DirectorySeparatorChar, [StringSplitOptions]::RemoveEmptyEntries)) {
            $candidate = Join-Path $cursor $segment
            $item = if ([IO.Directory]::Exists($candidate)) { [IO.DirectoryInfo]::new($candidate) } else { [IO.FileInfo]::new($candidate) }
            if ($null -ne $item.LinkTarget) { $cursor = $item.ResolveLinkTarget($true).FullName } else { $cursor = $candidate }
        }
        return [IO.Path]::GetFullPath($cursor)
    } catch { Throw-Wf 3 'path.missing' "Path does not exist: $Path" ([ordered]@{ path = $Path }) }
}

function Test-WfSymlink {
    param([string]$Path)
    try {
        $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        return $null -ne $item.LinkTarget
    } catch { return $false }
}

function Assert-WfNoSymlinkComponents {
    param([string]$Owner, [string]$Relative, [int]$ExitClass = 4)
    $cursor = [IO.Path]::GetFullPath($Owner)
    if ($Relative -eq '.') { return }
    foreach ($segment in $Relative.Split('/')) {
        $cursor = Join-Path $cursor $segment
        if ([IO.File]::Exists($cursor) -or [IO.Directory]::Exists($cursor) -or (Test-WfSymlink $cursor)) {
            if (Test-WfSymlink $cursor) { Throw-Wf $ExitClass 'path.symlink' 'Managed paths may not contain symbolic links.' ([ordered]@{ path = $Relative }) }
        } else { break }
    }
}

function Test-WfPortablePath {
    param([string]$Value, [switch]$AllowDot, [int]$ExitClass = 4)
    if ($Value -eq '.' -and $AllowDot) { return $true }
    if ([string]::IsNullOrEmpty($Value)) { Throw-Wf $ExitClass 'path.empty-segment' 'Path must not be empty.' }
    if ($Value.Contains('\')) { Throw-Wf $ExitClass 'path.backslash' 'Backslashes are forbidden in managed paths.' }
    if ($Value.Contains([char]0)) { Throw-Wf $ExitClass 'path.nul' 'NUL is forbidden in paths.' }
    if ($Value.StartsWith('/') -or $Value.StartsWith('//') -or $Value -match '^[A-Za-z]:') { Throw-Wf $ExitClass 'path.absolute' 'Absolute and drive paths are forbidden.' }
    $segments = $Value.Split('/')
    foreach ($segment in $segments) {
        if ($segment.Length -eq 0) { Throw-Wf $ExitClass 'path.empty-segment' 'Empty path segments are forbidden.' }
        if ($segment -eq '.') { Throw-Wf $ExitClass 'path.dot-segment' 'Dot path segments are forbidden.' }
        if ($segment -eq '..') { Throw-Wf $ExitClass 'path.traversal' 'Parent traversal is forbidden.' }
        if ($segment -notmatch '^[A-Za-z0-9._-]+$') { Throw-Wf $ExitClass 'path.character' 'Path contains a non-portable character.' }
        if ($segment.EndsWith('.') -or $segment.EndsWith(' ')) { Throw-Wf $ExitClass 'path.nonportable' 'Trailing dot or space is forbidden.' }
        $stem = $segment.Split('.')[0]
        if ($stem -match '^(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$') { Throw-Wf $ExitClass 'path.reserved-name' 'Windows device names are forbidden.' }
    }
    return $true
}

function Test-WfRelativeSourcePath {
    param([string]$Value, [int]$ExitClass = 2)
    if ([string]::IsNullOrEmpty($Value)) { Throw-Wf $ExitClass 'path.empty-segment' 'Source path must not be empty.' }
    if ($Value.Contains('\')) { Throw-Wf $ExitClass 'path.backslash' 'Backslashes are forbidden.' }
    if ($Value.StartsWith('/') -or $Value.StartsWith('//') -or $Value -match '^[A-Za-z]:') { Throw-Wf $ExitClass 'path.absolute' 'Absolute paths are forbidden.' }
    foreach ($segment in $Value.Split('/')) {
        if ($segment -eq '..') { Throw-Wf $ExitClass 'path.traversal' 'Parent traversal is forbidden.' }
        if ($segment -eq '.') { Throw-Wf $ExitClass 'path.dot-segment' 'Dot segments are forbidden.' }
        if ($segment.Length -eq 0) { Throw-Wf $ExitClass 'path.empty-segment' 'Empty segments are forbidden.' }
    }
    return $true
}

function Test-WfContained {
    param([string]$Child, [string]$Parent)
    $childFull = [IO.Path]::GetFullPath($Child).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $parentFull = [IO.Path]::GetFullPath($Parent).TrimEnd([IO.Path]::DirectorySeparatorChar)
    return $childFull.Equals($parentFull, [StringComparison]::Ordinal) -or $childFull.StartsWith($parentFull + [IO.Path]::DirectorySeparatorChar, [StringComparison]::Ordinal)
}

function Test-WfDate {
    param([string]$Value)
    [datetime]$date = [datetime]::MinValue
    return [datetime]::TryParseExact($Value, 'yyyy-MM-dd', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::None, [ref]$date)
}

function Get-WfManifestModel {
    param($Manifest, [string]$WorkspaceRoot, [switch]$Live, [int]$ExitClass = 4)
    Assert-WfClosedObject $Manifest @('format','schemaVersion','recordRoot','entrypoint','canonicalBaseline','modules','generatedArtifacts') @('format','schemaVersion','recordRoot','entrypoint','canonicalBaseline','modules','generatedArtifacts') $ExitClass
    if ($Manifest.format -ne 'wayfinder-project-record') { Throw-Wf $ExitClass 'manifest.format' 'Manifest format is not wayfinder-project-record.' }
    if ($Manifest.schemaVersion -is [bool] -or $Manifest.schemaVersion -ne 1) { Throw-Wf $ExitClass 'manifest.unsupported-version' 'Manifest schema version is unsupported.' }
    if ($Manifest.recordRoot -isnot [string] -or $Manifest.entrypoint -isnot [string]) { Throw-Wf $ExitClass 'json.type' 'Manifest paths must be strings.' }
    [void](Test-WfPortablePath $Manifest.recordRoot -AllowDot -ExitClass $ExitClass)
    [void](Test-WfPortablePath $Manifest.entrypoint -ExitClass $ExitClass)
    if (-not $Manifest.entrypoint.EndsWith('.md', [StringComparison]::OrdinalIgnoreCase)) { Throw-Wf $ExitClass 'manifest.entrypoint-extension' 'Entrypoints must end in .md.' }
    $recordRoot = if ($Manifest.recordRoot -eq '.') { $WorkspaceRoot } else { Join-Path $WorkspaceRoot ($Manifest.recordRoot.Replace('/', [IO.Path]::DirectorySeparatorChar)) }
    Assert-WfNoSymlinkComponents $WorkspaceRoot $Manifest.recordRoot $ExitClass
    Assert-WfNoSymlinkComponents $recordRoot $Manifest.entrypoint $ExitClass
    $baselineAllowed = if ($Manifest.canonicalBaseline.kind -eq 'git-ref') { @('kind','ref') } else { @('kind','path','sha256') }
    Assert-WfClosedObject $Manifest.canonicalBaseline @('kind') $baselineAllowed $ExitClass
    if ($Manifest.canonicalBaseline.kind -eq 'git-ref') {
        if (-not (Test-WfHas $Manifest.canonicalBaseline 'ref')) { Throw-Wf $ExitClass 'json.missing-field' 'Git baseline requires ref.' }
        if ($Manifest.canonicalBaseline.ref -isnot [string] -or -not $Manifest.canonicalBaseline.ref.StartsWith('refs/')) { Throw-Wf $ExitClass 'manifest.git-ref' 'Baseline ref must be fully qualified.' }
    } elseif ($Manifest.canonicalBaseline.kind -eq 'snapshot') {
        foreach ($name in @('path','sha256')) { if (-not (Test-WfHas $Manifest.canonicalBaseline $name)) { Throw-Wf $ExitClass 'json.missing-field' "Snapshot baseline requires $name." } }
        [void](Test-WfPortablePath $Manifest.canonicalBaseline.path -ExitClass $ExitClass)
        if (-not $Manifest.canonicalBaseline.path.StartsWith('.wayfinder/baselines/', [StringComparison]::Ordinal)) { Throw-Wf $ExitClass 'manifest.snapshot-path' 'Snapshot must be beneath .wayfinder/baselines/.' }
    } else { Throw-Wf $ExitClass 'manifest.baseline-kind' 'Unknown baseline kind.' }
    Assert-WfArray $Manifest.modules $ExitClass
    Assert-WfArray $Manifest.generatedArtifacts $ExitClass
    $moduleIds = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $moduleRoots = [Collections.Generic.List[string]]::new()
    $entrypoints = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    [void]$entrypoints.Add($Manifest.entrypoint)
    $hasDecisions = $false
    foreach ($module in $Manifest.modules) {
        Assert-WfClosedObject $module @('id','root','entrypoint','subjects') @('id','root','entrypoint','subjects') $ExitClass
        if ($module.id -isnot [string] -or ($module.id -notmatch '^(decisions|research|product|architecture|development|local-[a-z0-9]+(?:-[a-z0-9]+)*)$')) { Throw-Wf $ExitClass 'manifest.module-id' 'Invalid module ID.' }
        if (-not $moduleIds.Add($module.id)) { Throw-Wf $ExitClass 'manifest.duplicate-module-id' 'Duplicate module ID.' }
        if ($module.id -eq 'decisions') { $hasDecisions = $true }
        foreach ($field in @('root','entrypoint')) { if ($module[$field] -isnot [string]) { Throw-Wf $ExitClass 'json.type' "Module $field must be a string." }; [void](Test-WfPortablePath $module[$field] -ExitClass $ExitClass) }
        $rootIdentity = $module.root.ToLowerInvariant()
        foreach ($existing in $moduleRoots) {
            if ($rootIdentity -eq $existing -or $rootIdentity.StartsWith($existing + '/') -or $existing.StartsWith($rootIdentity + '/')) { Throw-Wf $ExitClass 'manifest.module-root-overlap' 'Module roots overlap or nest.' }
        }
        $moduleRoots.Add($rootIdentity)
        if (-not ($module.entrypoint -eq $module.root -or $module.entrypoint.StartsWith($module.root + '/', [StringComparison]::OrdinalIgnoreCase))) { Throw-Wf $ExitClass 'manifest.entrypoint-outside-owner' 'Module entrypoint is outside its root.' }
        if (-not $entrypoints.Add($module.entrypoint)) { Throw-Wf $ExitClass 'manifest.duplicate-entrypoint' 'Entrypoints collide.' }
        Assert-WfArray $module.subjects $ExitClass
        $subjectIds = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        $collectionRoots = [Collections.Generic.List[string]]::new()
        foreach ($subject in $module.subjects) {
            if ($subject -isnot [System.Collections.IDictionary]) { Throw-Wf $ExitClass 'json.type' 'Subject must be an object.' }
            $allowed = if ($subject.kind -eq 'collection') { @('id','kind','root','entrypoint') } else { @('id','kind','entrypoint') }
            Assert-WfClosedObject $subject $allowed $allowed $ExitClass
            if ($subject.id -isnot [string] -or $subject.id -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') { Throw-Wf $ExitClass 'manifest.subject-id' 'Invalid subject ID.' }
            if (-not $subjectIds.Add($subject.id)) { Throw-Wf $ExitClass 'manifest.duplicate-subject-id' 'Duplicate subject ID.' }
            if ($subject.kind -notin @('document','collection')) { Throw-Wf $ExitClass 'manifest.subject-kind' 'Unknown subject kind.' }
            [void](Test-WfPortablePath $subject.entrypoint -ExitClass $ExitClass)
            if (-not ($subject.entrypoint -eq $module.root -or $subject.entrypoint.StartsWith($module.root + '/', [StringComparison]::OrdinalIgnoreCase))) { Throw-Wf $ExitClass 'manifest.entrypoint-outside-owner' 'Subject entrypoint is outside module root.' }
            if (-not $entrypoints.Add($subject.entrypoint)) { Throw-Wf $ExitClass 'manifest.duplicate-entrypoint' 'Entrypoints collide.' }
            if ($subject.kind -eq 'collection') {
                [void](Test-WfPortablePath $subject.root -ExitClass $ExitClass)
                if (-not $subject.root.StartsWith($module.root + '/', [StringComparison]::OrdinalIgnoreCase)) { Throw-Wf $ExitClass 'manifest.entrypoint-outside-owner' 'Collection root is outside module root.' }
                foreach ($existing in $collectionRoots) {
                    $identity = $subject.root.ToLowerInvariant()
                    if ($identity -eq $existing -or $identity.StartsWith($existing + '/') -or $existing.StartsWith($identity + '/')) { Throw-Wf $ExitClass 'manifest.subject-root-overlap' 'Collection roots overlap or nest.' }
                }
                $collectionRoots.Add($subject.root.ToLowerInvariant())
                if (-not ($subject.entrypoint -eq $subject.root -or $subject.entrypoint.StartsWith($subject.root + '/', [StringComparison]::OrdinalIgnoreCase))) { Throw-Wf $ExitClass 'manifest.entrypoint-outside-owner' 'Collection entrypoint is outside collection root.' }
            }
        }
        foreach ($subject in $module.subjects) {
            if ($subject.kind -eq 'document') {
                foreach ($root in $collectionRoots) { if ($subject.entrypoint.ToLowerInvariant().StartsWith($root + '/')) { Throw-Wf $ExitClass 'manifest.document-in-collection' 'Document subject is inside collection root.' } }
            }
        }
    }
    if (-not $hasDecisions) { Throw-Wf $ExitClass 'manifest.decisions-required' 'The decisions module is required.' }
    foreach ($artifact in $Manifest.generatedArtifacts) {
        Assert-WfClosedObject $artifact @('path','generator') @('path','generator') $ExitClass
        [void](Test-WfPortablePath $artifact.path -ExitClass $ExitClass)
        if ($artifact.generator -ne 'document-catalog-v1') { Throw-Wf $ExitClass 'manifest.unknown-generator' 'Unknown generated artifact generator.' }
        if ($entrypoints.Contains($artifact.path)) { Throw-Wf $ExitClass 'manifest.artifact-entrypoint-conflict' 'Generated artifact collides with authored entrypoint.' }
    }
    if ($Live) {
        if (-not [IO.Directory]::Exists($recordRoot)) { Throw-Wf $ExitClass 'manifest.path-missing' 'Record root is missing.' }
        $paths = [Collections.Generic.List[object]]::new()
        $paths.Add(@($Manifest.entrypoint, $false))
        foreach ($module in $Manifest.modules) {
            $paths.Add(@($module.root, $true)); $paths.Add(@($module.entrypoint, $false))
            foreach ($subject in $module.subjects) { if ($subject.kind -eq 'collection') { $paths.Add(@($subject.root, $true)) }; $paths.Add(@($subject.entrypoint, $false)) }
        }
        foreach ($artifact in $Manifest.generatedArtifacts) { $paths.Add(@($artifact.path, $false)) }
        foreach ($pair in $paths) {
            $relative = [string]$pair[0]; $directory = [bool]$pair[1]
            Assert-WfNoSymlinkComponents $recordRoot $relative $ExitClass
            $full = Join-Path $recordRoot ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
            if (($directory -and -not [IO.Directory]::Exists($full)) -or (-not $directory -and -not [IO.File]::Exists($full))) { Throw-Wf $ExitClass 'manifest.path-missing' "Declared managed path is missing: $relative" ([ordered]@{ path = $relative }) }
        }
        if ($Manifest.canonicalBaseline.kind -eq 'snapshot') {
            Assert-WfNoSymlinkComponents $WorkspaceRoot $Manifest.canonicalBaseline.path $ExitClass
            if (-not [IO.File]::Exists((Join-Path $WorkspaceRoot $Manifest.canonicalBaseline.path))) { Throw-Wf $ExitClass 'manifest.path-missing' 'Snapshot baseline is missing.' }
        }
    }
    return [ordered]@{ manifest = $Manifest; workspaceRoot = $WorkspaceRoot; recordRoot = [IO.Path]::GetFullPath($recordRoot) }
}

function Find-WfManifest {
    param([string]$WorkspaceRoot, [string]$Start)
    if ($WorkspaceRoot) {
        $root = Resolve-WfPhysicalPath $WorkspaceRoot
        if (-not [IO.Directory]::Exists($root)) { Throw-Wf 3 'discover.workspace-not-directory' 'Workspace root must be a directory.' }
        $control = Join-Path $root '.wayfinder'
        if (Test-WfSymlink $control) { Throw-Wf 4 'discover.control-symlink' 'The .wayfinder control directory may not be a symbolic link.' }
        $manifestPath = Join-Path $control 'manifest.json'
        if (Test-WfSymlink $manifestPath) { Throw-Wf 4 'discover.manifest-symlink' 'The manifest may not be a symbolic link.' }
        if (-not [IO.File]::Exists($manifestPath)) { Throw-Wf 3 'discover.manifest-not-found' 'No Wayfinder manifest exists at the exact workspace root.' }
        return @($root, $manifestPath)
    }
    $startPath = if ($Start) { Resolve-WfPhysicalPath $Start } else { [IO.Path]::GetFullPath((Get-Location).Path) }
    if ([IO.File]::Exists($startPath)) { $cursor = [IO.Directory]::GetParent($startPath) } else { $cursor = [IO.DirectoryInfo]::new($startPath) }
    $probe = $cursor
    $boundary = $null
    while ($null -ne $probe) {
        $git = Join-Path $probe.FullName '.git'
        if ([IO.Directory]::Exists($git) -or [IO.File]::Exists($git) -or (Test-WfSymlink $git)) { $boundary = $probe.FullName; break }
        $probe = $probe.Parent
    }
    while ($null -ne $cursor) {
        $control = Join-Path $cursor.FullName '.wayfinder'
        $manifestPath = Join-Path $control 'manifest.json'
        if ((Test-WfSymlink $control)) { Throw-Wf 4 'discover.control-symlink' 'The .wayfinder control directory may not be a symbolic link.' }
        if (Test-WfSymlink $manifestPath) { Throw-Wf 4 'discover.manifest-symlink' 'The manifest may not be a symbolic link.' }
        if ([IO.File]::Exists($manifestPath)) { return @($cursor.FullName, $manifestPath) }
        if ($boundary -and $cursor.FullName -eq $boundary) { break }
        $cursor = $cursor.Parent
    }
    Throw-Wf 3 'discover.manifest-not-found' 'No Wayfinder manifest was found within the search boundary.'
}

function Invoke-WfDiscover {
    param([System.Collections.IDictionary]$Options)
    $found = Find-WfManifest $Options['workspace-root'] $Options['start']
    $workspace = [string]$found[0]; $manifestPath = [string]$found[1]
    $manifest = Read-WfJsonFile $manifestPath 4 -ManifestText
    $model = Get-WfManifestModel $manifest $workspace -Live -ExitClass 4
    return [ordered]@{
        workspace = [ordered]@{ workspaceRoot = $workspace; manifest = $manifestPath; recordRoot = $model.recordRoot }
        manifest = $manifest
    }
}

function Get-WfFileType {
    param([string]$Path)
    try {
        $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            if ($null -ne $item.LinkTarget) { return 'symlink' }
            return 'unsupported-file'
        }
        $unixStat = $item.PSObject.Properties['UnixStat']
        if ($null -ne $unixStat -and $null -ne $unixStat.Value) {
            switch ($unixStat.Value.ItemType.ToString()) {
                'File' { return 'regular-file' }
                'Directory' { return 'directory' }
                'SymbolicLink' { return 'symlink' }
                default { return 'unsupported-file' }
            }
        }
        if ($item -is [IO.DirectoryInfo]) { return 'directory' }
        if ($item -is [IO.FileInfo]) { return 'regular-file' }
        return 'unsupported-file'
    } catch {
        if ([IO.Directory]::Exists($Path)) { return 'directory' }
        if ([IO.File]::Exists($Path)) { return 'regular-file' }
        return $null
    }
}

function Get-WfMarkdownCues {
    param([string]$Text)
    if (-not $Text.IsNormalized([Text.NormalizationForm]::FormC)) { return [ordered]@{ accepted = $false; reason = 'non-nfc-text'; h1 = $null; outline = [Collections.ArrayList]::new() } }
    $outline = [Collections.ArrayList]::new(); $h1 = $null; $fence = $null
    $lines = $Text.Split("`n")
    for ($index = 0; $index -lt $lines.Count; $index++) {
        $line = $lines[$index]
        if ($line -match '^ {0,3}(`{3,}|~{3,})') {
            $marker = $Matches[1][0]
            if ($null -eq $fence) { $fence = $marker } elseif ($marker -eq $fence) { $fence = $null }
            continue
        }
        if ($null -ne $fence) { continue }
        if ($line -match '^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*$') {
            $level = $Matches[1].Length; $heading = $Matches[2]
            $heading = [regex]::Replace($heading, '[ \t]+#+[ \t]*$', '')
            if (-not [string]::IsNullOrWhiteSpace($heading)) {
                $entry = [ordered]@{ level = $level; text = $heading; line = $index + 1 }
                [void]$outline.Add($entry)
                if ($level -eq 1 -and $null -eq $h1) { $h1 = $heading }
            }
        }
    }
    return [ordered]@{ accepted = $true; h1 = $h1; outline = $outline }
}

function Get-WfExclusion {
    param([string]$Relative, [string]$Type, [string[]]$TargetRoots, [bool]$ExplicitFile)
    $segments = $Relative.Split('/')
    foreach ($target in $TargetRoots) { if ($Relative -eq $target -or $Relative.StartsWith($target + '/')) { return 'declared-target-root' } }
    if ($segments | Where-Object { $_ -in @('.git','.hg','.svn') }) { return 'vcs-administration' }
    if ($segments | Where-Object { $_ -eq '.wayfinder' }) { return 'wayfinder-state' }
    $name = $segments[-1]
    if ($name -eq '.env' -or $name.StartsWith('.env.') -or $name -match '(?i)(private[-_]?key|credentials?|id_rsa|id_ed25519|\.pem$|\.p12$|\.pfx$)') { return 'secret-safety' }
    if ($Type -eq 'symlink') { return 'symbolic-link' }
    if ($Type -eq 'unsupported-file') { return 'unsupported-special-file' }
    if (-not $ExplicitFile) {
        if ($segments | Where-Object { $_ -in @('node_modules','vendor','.venv','venv') }) { return 'dependency-directory' }
        if ($segments | Where-Object { $_ -in @('build','dist','out','target','coverage','.cache') }) { return 'build-output-directory' }
        if ($name -match '(?i)\.(zip|tar|tgz|gz|bz2|xz|7z|rar|jar|war)$') { return 'archive-file' }
    }
    return $null
}

function Invoke-WfInventory {
    param([System.Collections.IDictionary]$Options)
    if (-not $Options.Contains('workspace-root') -or -not $Options.Contains('request')) { Throw-Wf 2 'command.arguments' 'inventory requires --workspace-root and --request.' }
    $workspace = Resolve-WfPhysicalPath $Options['workspace-root']
    if (-not [IO.Directory]::Exists($workspace)) { Throw-Wf 3 'inventory.workspace-not-directory' 'Workspace root must be a directory.' }
    $requestPath = Resolve-WfPhysicalPath $Options['request']
    if (Test-WfSymlink $requestPath -or -not [IO.File]::Exists($requestPath)) { Throw-Wf 2 'inventory.request-file' 'Request must be a non-symbolic regular file.' }
    $request = Read-WfJsonFile $requestPath 2
    Assert-WfClosedObject $request @('format','schemaVersion','selections','targetRoots','limits') @('format','schemaVersion','selections','targetRoots','limits') 2
    if ($request.format -ne 'wayfinder-source-inventory-request') { Throw-Wf 2 'inventory.format' 'Inventory request format differs.' }
    if ($request.schemaVersion -is [bool] -or $request.schemaVersion -ne 1) { Throw-Wf 2 'inventory.unsupported-version' 'Inventory request version differs.' }
    Assert-WfArray $request.selections 2; Assert-WfArray $request.targetRoots 2
    if ($request.selections.Count -eq 0) { Throw-Wf 2 'inventory.selections' 'At least one source selection is required.' }
    Assert-WfClosedObject $request.limits @('maxEntries','maxFileBytes','maxTotalBytes','maxDepth') @('maxEntries','maxFileBytes','maxTotalBytes','maxDepth') 2
    foreach ($name in @('maxEntries','maxFileBytes','maxTotalBytes','maxDepth')) {
        $value = $request.limits[$name]
        if ($value -is [bool] -or $value -isnot [ValueType] -or [int64]$value -lt 1) { Throw-Wf 2 'json.type' "Inventory limit $name must be a positive integer." }
    }
    $selectionSet = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($selection in $request.selections) {
        if ($selection -isnot [string]) { Throw-Wf 2 'json.type' 'Selections must be strings.' }
        [void](Test-WfRelativeSourcePath $selection 2)
        if (-not $selectionSet.Add($selection)) { Throw-Wf 2 'inventory.duplicate-selection' 'Inventory selections must be unique.' }
    }
    $targetSet = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($target in $request.targetRoots) { if ($target -isnot [string]) { Throw-Wf 2 'json.type' 'Target roots must be strings.' }; [void](Test-WfRelativeSourcePath $target 2); if (-not $targetSet.Add($target)) { Throw-Wf 2 'inventory.duplicate-target-root' 'Target roots must be unique.' } }
    $selectionObjects = [Collections.ArrayList]::new(); $entryByPath = [ordered]@{}; $totalBytes = [int64]0
    $sortedSelections = @($request.selections); [Array]::Sort($sortedSelections, [StringComparer]::Ordinal)
    foreach ($selection in $sortedSelections) {
        $segments = $selection.Split('/'); $cursor = $workspace
        for ($i=0; $i -lt $segments.Count - 1; $i++) {
            $cursor = Join-Path $cursor $segments[$i]
            if (Test-WfSymlink $cursor) { Throw-Wf 3 'inventory.selection-symlink-component' 'Selection contains a symbolic-link component.' ([ordered]@{ path = $selection }) }
        }
        $full = Join-Path $workspace ($selection.Replace('/', [IO.Path]::DirectorySeparatorChar))
        $type = Get-WfFileType $full
        if ($null -eq $type) { Throw-Wf 3 'inventory.selection-missing' 'Selected source is missing.' ([ordered]@{ path = $selection }) }
        [void]$selectionObjects.Add([ordered]@{ path = $selection; type = $type })
        $stack = [Collections.Generic.Stack[object]]::new(); $stack.Push(@($selection,$full,0,$type,($type -eq 'regular-file')))
        while ($stack.Count -gt 0) {
            $node = $stack.Pop(); $relative=[string]$node[0]; $path=[string]$node[1]; $depth=[int]$node[2]; $nodeType=[string]$node[3]; $explicit=[bool]$node[4]
            if ($entryByPath.Contains($relative)) { continue }
            if ($depth -gt [int]$request.limits.maxDepth) { Throw-Wf 3 'inventory.limit-depth' 'Inventory traversal depth limit exceeded.' }
            if ($entryByPath.Count + 1 -gt [int]$request.limits.maxEntries) { Throw-Wf 3 'inventory.limit-entries' 'Inventory entry limit exceeded.' }
            $exclusion = Get-WfExclusion $relative $nodeType @($request.targetRoots) $explicit
            $entry = [ordered]@{ path=$relative; type=$nodeType; included=$false; exclusion=$exclusion; byteLength=$null; sha256=$null; content=$null; markdown=$null }
            if ($nodeType -eq 'regular-file') {
                try { $length = [IO.FileInfo]::new($path).Length } catch { Throw-Wf 3 'inventory.source-race' 'Could not stat source file.' }
                $entry.byteLength = $length
                if ($null -eq $exclusion) {
                    if ($length -gt [int64]$request.limits.maxFileBytes) { Throw-Wf 3 'inventory.limit-file-bytes' 'Per-file inventory byte limit exceeded.' }
                    if ($totalBytes + $length -gt [int64]$request.limits.maxTotalBytes) { Throw-Wf 3 'inventory.limit-total-bytes' 'Cumulative inventory byte limit exceeded.' }
                    if (Test-WfSymlink $path) { Throw-Wf 3 'inventory.source-race' 'Source changed to symbolic link.' }
                    try { $bytes = [IO.File]::ReadAllBytes($path) } catch { Throw-Wf 3 'inventory.source-race' 'Could not safely read source file.' }
                    if ($bytes.Length -ne $length -or (Test-WfSymlink $path)) { Throw-Wf 3 'inventory.source-race' 'Source changed while reading.' }
                    $entry.included=$true; $entry.sha256=Get-WfSha256Bytes $bytes; $totalBytes += $bytes.Length
                    try { $text=$script:Utf8Strict.GetString($bytes); $entry.content='strict-utf8'; if ($relative.EndsWith('.md',[StringComparison]::OrdinalIgnoreCase)) { $entry.markdown=Get-WfMarkdownCues $text } } catch { $entry.content='opaque-bytes' }
                }
            } elseif ($nodeType -eq 'directory' -and $null -eq $exclusion) {
                $entry.included=$false
            }
            $entryByPath[$relative]=$entry
            if ($nodeType -eq 'directory' -and $null -eq $exclusion) {
                $children = @(Get-ChildItem -LiteralPath $path -Force)
                [Array]::Sort($children, [Comparison[object]]{ param($a,$b) [StringComparer]::Ordinal.Compare($a.Name,$b.Name) })
                for ($ci=$children.Count-1; $ci -ge 0; $ci--) {
                    $child=$children[$ci]; $childRel=$relative+'/'+$child.Name; $childType=Get-WfFileType $child.FullName
                    $stack.Push(@($childRel,$child.FullName,($depth+1),$childType,$false))
                }
            }
        }
    }
    $entryNames=@($entryByPath.Keys); [Array]::Sort($entryNames,[StringComparer]::Ordinal)
    $entries=[Collections.ArrayList]::new(); foreach($name in $entryNames){[void]$entries.Add($entryByPath[$name])}
    $groups=[ordered]@{}; foreach($entry in $entries){ if($entry.included){ if(-not $groups.Contains($entry.sha256)){$groups[$entry.sha256]=[Collections.ArrayList]::new()};[void]$groups[$entry.sha256].Add($entry.path)}}
    $duplicates=[Collections.ArrayList]::new(); $digests=@($groups.Keys); [Array]::Sort($digests,[StringComparer]::Ordinal); foreach($digest in $digests){if($groups[$digest].Count-ge 2){$paths=@($groups[$digest]);[Array]::Sort($paths,[StringComparer]::Ordinal);[void]$duplicates.Add([ordered]@{sha256=$digest;paths=[Collections.ArrayList]@($paths)})}}
    $byType=[ordered]@{'regular-file'=0;directory=0;symlink=0;'unsupported-file'=0}; $included=0;$excluded=0
    foreach($entry in $entries){$byType[$entry.type]++;if($entry.included){$included++};if($null-ne$entry.exclusion){$excluded++}}
    $inventory=[ordered]@{format='wayfinder-source-inventory';schemaVersion=1;selections=$selectionObjects;targetRoots=[Collections.ArrayList]@($request.targetRoots);limits=$request.limits;entries=$entries;duplicateGroups=$duplicates;summary=[ordered]@{entries=$entries.Count;includedRegularFiles=$included;excluded=$excluded;totalIncludedBytes=$totalBytes;byType=$byType;duplicateGroups=$duplicates.Count}}
    $inventoryCanonical=ConvertTo-WfCanonicalJson $inventory; $inventoryDigest=Get-WfSha256Text $inventoryCanonical
    $data=[ordered]@{inventory=$inventory;inventorySha256=$inventoryDigest;environment=[ordered]@{workspaceRoot=$workspace}}
    if($Options.Contains('ledger')){$data['intake']=Test-WfIntake $Options['ledger'] $workspace $inventory $inventoryDigest}
    return $data
}

function Test-WfIdentifier {
    param([string]$Value,[string]$Kind)
    if($Kind-eq'document'){$pattern='^wf-([0-9]{4,})-([a-z0-9]+(?:-[a-z0-9]+)*)$'}elseif($Kind-eq'question'){$pattern='^wfq-([0-9]{4,})-([a-z0-9]+(?:-[a-z0-9]+)*)$'}else{return $Value-cmatch'^src-[0-9]{2,}$' -and [int64]($Value.Substring(4))-ge1}
    if($Value-cnotmatch$pattern){return $false}
    $ordinalText=$Matches[1];$mnemonic=$Matches[2];$ordinal=[int64]$ordinalText
    return $ordinal-ge1-and$mnemonic.Length-le48-and($ordinal-ge1000-or$ordinalText.Length-eq4)
}

function Test-WfIntake {
    param([string]$LedgerPath,[string]$Workspace,$Inventory,[string]$InventoryDigest)
    $physical=Resolve-WfPhysicalPath $LedgerPath;if(Test-WfSymlink $physical -or -not[IO.File]::Exists($physical)){Throw-Wf 2 'intake.file' 'Ledger must be a non-symbolic regular file.'}
    $ledger=Read-WfJsonFile $physical 2
    Assert-WfClosedObject $ledger @('format','schemaVersion','inventorySha256','sources') @('format','schemaVersion','inventorySha256','sources') 2
    if($ledger.format-ne'wayfinder-intake-ledger'){Throw-Wf 2 'intake.format' 'Intake ledger format differs.'};if($ledger.schemaVersion-is[bool]-or$ledger.schemaVersion-ne1){Throw-Wf 2 'intake.unsupported-version' 'Intake version differs.'};Assert-WfArray $ledger.sources 2
    $included=[ordered]@{};foreach($entry in $Inventory.entries){if($entry.included){$included[$entry.path]=$entry}}
    if($ledger.inventorySha256-ne$InventoryDigest){
        foreach($source in $ledger.sources){
            if($source-isnot[Collections.IDictionary]-or-not$source.Contains('path')-or$source.path-isnot[string]){continue}
            if(-not$included.Contains($source.path)){Throw-Wf 3 'intake.source-stale' 'Intake source is missing, excluded, or replaced.'}
            $entry=$included[$source.path]
            if(($source.Contains('byteLength')-and$source.byteLength-ne$entry.byteLength)-or($source.Contains('sha256')-and$source.sha256-ne$entry.sha256)){Throw-Wf 3 'intake.source-stale' 'Intake source bytes have changed.'}
        }
        Throw-Wf 3 'intake.inventory-digest' 'Intake ledger does not bind the current canonical inventory.'
    }
    $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$counts=[ordered]@{incorporate=0;reference=0;'preserve-out-of-scope'=0;unresolved=0}
    foreach($source in $ledger.sources){
        Assert-WfClosedObject $source @('path','sha256','byteLength','disposition','reason','targetIds','transformationNote','evidenceKeys','questionIds') @('path','sha256','byteLength','disposition','reason','targetIds','transformationNote','evidenceKeys','questionIds') 2
        foreach($a in @('targetIds','evidenceKeys','questionIds')){Assert-WfArray $source[$a] 2}
        if($source.path-isnot[string]-or-not$seen.Add($source.path)-or-not$included.Contains($source.path)){Throw-Wf 2 'intake.source' 'Ledger source must uniquely name an included regular file.'}
        if($source.reason-isnot[string]-or[string]::IsNullOrWhiteSpace($source.reason)){Throw-Wf 2 'intake.reason' 'Review reason is required.'}
        if($source.disposition-notin@('incorporate','reference','preserve-out-of-scope','unresolved')){Throw-Wf 2 'intake.disposition' 'Invalid intake disposition.'}
        foreach($id in $source.targetIds){if(-not(Test-WfIdentifier $id document)){Throw-Wf 2 'intake.identifier' 'Invalid document ID.'}}
        foreach($id in $source.evidenceKeys){if(-not(Test-WfIdentifier $id source)){Throw-Wf 2 'intake.identifier' 'Invalid evidence key.'}}
        foreach($id in $source.questionIds){if(-not(Test-WfIdentifier $id question)){Throw-Wf 2 'intake.identifier' 'Invalid question ID.'}}
        switch($source.disposition){
            incorporate{if($source.targetIds.Count-eq0-or$source.transformationNote-isnot[string]-or[string]::IsNullOrWhiteSpace($source.transformationNote)-or$source.evidenceKeys.Count-or$source.questionIds.Count){Throw-Wf 2 'intake.incorporate-fields' 'Incorporate fields do not satisfy the contract.'}}
            reference{if($source.evidenceKeys.Count-eq0-or$source.targetIds.Count-or$null-ne$source.transformationNote-or$source.questionIds.Count){Throw-Wf 2 'intake.reference-fields' 'Reference fields do not satisfy the contract.'}}
            'preserve-out-of-scope'{if($source.targetIds.Count-or$source.evidenceKeys.Count-or$source.questionIds.Count-or$null-ne$source.transformationNote){Throw-Wf 2 'intake.preserve-fields' 'Preserve fields do not satisfy the contract.'}}
            unresolved{if($source.questionIds.Count-eq0-or$source.targetIds.Count-or$source.evidenceKeys.Count-or$null-ne$source.transformationNote){Throw-Wf 2 'intake.unresolved-fields' 'Unresolved fields do not satisfy the contract.'}}
        }
        $entry=$included[$source.path];$file=Join-Path $Workspace ($source.path.Replace('/',[IO.Path]::DirectorySeparatorChar))
        if((Test-WfSymlink $file)-or-not[IO.File]::Exists($file)){Throw-Wf 3 'intake.source-stale' 'Intake source is missing or symbolic.'}
        $bytes=[IO.File]::ReadAllBytes($file);if($bytes.Length-ne[int64]$source.byteLength-or(Get-WfSha256Bytes $bytes)-ne$source.sha256-or$source.sha256-ne$entry.sha256){Throw-Wf 3 'intake.source-stale' 'Intake source bytes have changed.'}
        $counts[$source.disposition]++
    }
    $canonical=ConvertTo-WfCanonicalJson $ledger
    return [ordered]@{ledger=$ledger;ledgerSha256=Get-WfSha256Text $canonical;dispositionCounts=$counts;sourceDigestsRechecked=$ledger.sources.Count}
}

function Read-WfTextFile {
    param([string]$Path,[int]$ExitClass=4)
    $bytes=[IO.File]::ReadAllBytes($Path)
    if($bytes.Length-ge3-and$bytes[0]-eq0xEF-and$bytes[1]-eq0xBB-and$bytes[2]-eq0xBF){Throw-Wf $ExitClass 'text.bom' 'UTF-8 BOM is forbidden.'}
    try{$text=$script:Utf8Strict.GetString($bytes)}catch{Throw-Wf $ExitClass 'text.invalid-utf8' 'Text is not strict UTF-8.'}
    if($text.Contains("`r")){Throw-Wf $ExitClass 'text.newline' 'CR and CRLF are forbidden.'}
    if(-not$text.IsNormalized([Text.NormalizationForm]::FormC)){Throw-Wf $ExitClass 'text.non-nfc' 'Text must use NFC normalization.'}
    return $text
}

function Get-WfOrdinal { param([string]$Id) if($Id.StartsWith('wfq-')){return [int64]($Id.Split('-')[1])};return [int64]($Id.Split('-')[1]) }

function Resolve-WfDocumentLink {
    param([string]$OwnerRelative,[string]$Target,[string]$RecordRoot,[int]$ExitClass=4)
    if($Target.Contains('\')-or$Target.StartsWith('/')-or$Target-match'^[A-Za-z]:'){Throw-Wf $ExitClass 'path.absolute' 'Link target must be relative.'}
    $targetFile=$Target.Split('#')[0]
    $ownerDirectory=[IO.Path]::GetDirectoryName($OwnerRelative.Replace('/',[IO.Path]::DirectorySeparatorChar))
    $base=if([string]::IsNullOrEmpty($ownerDirectory)){$RecordRoot}else{Join-Path $RecordRoot $ownerDirectory}
    $full=[IO.Path]::GetFullPath((Join-Path $base ($targetFile.Replace('/',[IO.Path]::DirectorySeparatorChar))))
    if(-not(Test-WfContained $full $RecordRoot)){Throw-Wf $ExitClass 'path.traversal' 'Typed link escapes the record root.'}
    return [IO.Path]::GetRelativePath($RecordRoot,$full).Replace([IO.Path]::DirectorySeparatorChar,'/')
}

function Parse-WfLinks {
    param([string]$Value,[string]$OwnerPath,[string]$RecordRoot,[int]$ExitClass=4,[string]$FailureCode='relationship.link')
    $links=[Collections.ArrayList]::new()
    foreach($piece in $Value.Split(', ')){
        if($piece-notmatch'^\[(wf-[0-9]+-[a-z0-9-]+)\]\(([^)]+)\)$'){Throw-Wf $ExitClass $FailureCode 'Malformed typed Markdown link.'}
        $id=$Matches[1];$target=$Matches[2];$relative=Resolve-WfDocumentLink $OwnerPath $target $RecordRoot $ExitClass
        [void]$links.Add([ordered]@{id=$id;target=$target;path=$relative})
    }
    return ,$links
}

function Parse-WfQuestionBlocks {
    param([string]$Text,[string]$OwnerPath,[string]$RecordRoot,[string]$Kind)
    $questions=[Collections.ArrayList]::new()
    $opens=([regex]::Matches($Text,'<!-- wayfinder:question -->')).Count;$closes=([regex]::Matches($Text,'<!-- /wayfinder:question -->')).Count
    if($opens-ne$closes){Throw-Wf 4 'question.delimiter' 'Question block delimiters are unbalanced.'}
    if($opens-gt0-and$Kind-ne'register'){Throw-Wf 4 'question.owner-kind' 'Question blocks belong only in register documents.'}
    $matches=[regex]::Matches($Text,'(?ms)^<!-- wayfinder:question -->\n(.*?)^<!-- /wayfinder:question -->$')
    if($matches.Count-ne$opens){Throw-Wf 4 'question.delimiter' 'Question blocks must use exact delimiters.'}
    foreach($match in $matches){
        $body=$match.Groups[1].Value;$lines=$body.Split("`n")
        if($lines.Count-lt7-or$lines[0]-notmatch'^<a id="([^"]+)"></a>$'){Throw-Wf 4 'question.anchor' 'Question anchor is malformed.'};$anchor=$Matches[1]
        if($lines[1]-notmatch'^### (.+)$'){Throw-Wf 4 'question.title' 'Question title is malformed.'};$title=$Matches[1]
        $fields=[ordered]@{};$index=2
        while($index-lt$lines.Count-and$lines[$index]-ne''){
            if($lines[$index]-notmatch'^- \*\*([A-Za-z-]+):\*\* (.+)$'){Throw-Wf 4 'question.field-syntax' 'Question field is malformed.'}
            $name=$Matches[1];$value=$Matches[2];if($fields.Contains($name)){Throw-Wf 4 'question.duplicate-field' 'Question field is duplicated.'};$fields[$name]=$value;$index++
        }
        foreach($name in @('ID','State','Raised')){if(-not$fields.Contains($name)){Throw-Wf 4 'question.missing-field' "Question field $name is required."}}
        if($anchor-ne$fields.ID){Throw-Wf 4 'question.anchor' 'Question anchor and ID differ.'}
        if(-not(Test-WfIdentifier $fields.ID question)){Throw-Wf 4 'record.question-id' 'Question ID is invalid.'}
        if($fields.State-notin@('Open','Investigating','Deferred','Resolved','Retired')){Throw-Wf 4 'question.state' 'Question state is invalid.'}
        if(-not(Test-WfDate $fields.Raised)){Throw-Wf 4 'record.date' 'Question raised date is invalid.'}
        $applies=[Collections.ArrayList]::new();if($fields.Contains('Applies-To')){$applies=Parse-WfLinks $fields['Applies-To'] $OwnerPath $RecordRoot 4 'question.link'}
        if((-not$fields.Contains('Scope')-or$fields.Scope-ne'Record-Wide')-and$applies.Count-eq0){Throw-Wf 4 'question.scope' 'Question requires Applies-To links or Record-Wide scope.'}
        if($fields.Contains('Scope')-and$fields.Scope-ne'Record-Wide'){Throw-Wf 4 'question.scope' 'Question scope is invalid.'}
        $addressed=[Collections.ArrayList]::new();if($fields.Contains('Addressed-By')){$addressed=Parse-WfLinks $fields['Addressed-By'] $OwnerPath $RecordRoot 4 'question.link'}
        $resolved=[Collections.ArrayList]::new();if($fields.Contains('Resolved-By')){$resolved=Parse-WfLinks $fields['Resolved-By'] $OwnerPath $RecordRoot 4 'question.link'}
        if($fields.State-eq'Resolved'){
            if(-not$fields.Contains('Resolution-Date')-or$resolved.Count-eq0){Throw-Wf 4 'question.conditional-content' 'Resolved questions require Resolution-Date and Resolved-By.'}
            if(-not(Test-WfDate $fields['Resolution-Date'])){Throw-Wf 4 'record.date' 'Resolution date is invalid.'}
        }elseif($fields.Contains('Resolution-Date')-or$resolved.Count){Throw-Wf 4 'question.conditional-content' 'Only resolved questions permit resolution fields.'}
        $sections=[ordered]@{};$sectionOrder=[Collections.ArrayList]::new()
        while($index-lt$lines.Count){
            while($index-lt$lines.Count-and$lines[$index]-eq''){$index++};if($index-ge$lines.Count){break}
            if($lines[$index]-notmatch'^#### (.+)$'){Throw-Wf 4 'question.conditional-content' 'Question section heading is malformed.'};$heading=$Matches[1];$index++
            if($index-ge$lines.Count-or$lines[$index]-ne''){Throw-Wf 4 'question.conditional-content' 'Question sections require one blank line.'};$index++
            $content=[Collections.ArrayList]::new();while($index-lt$lines.Count-and$lines[$index]-notmatch'^#### '){[void]$content.Add($lines[$index]);$index++}
            while($content.Count-and$content[$content.Count-1]-eq''){$content.RemoveAt($content.Count-1)}
            $sections[$heading]=$content-join"`n";[void]$sectionOrder.Add($heading)
        }
        $expected=switch($fields.State){Open{@('Why it matters','Next step','History')}Investigating{@('Why it matters','Current activity','History')}Deferred{@('Why it matters','Deferral reason','Revisit trigger','History')}Resolved{@('Why it matters','Resolution','History')}Retired{@('Why it matters','Retirement reason','History')}}
        if(($sectionOrder-join'|')-ne($expected-join'|')){Throw-Wf 4 'question.conditional-content' 'Question sections do not match its lifecycle state.'}
        $historyLines=@($sections.History.Split("`n")|Where-Object{$_-ne''});$current='None';$first=$true
        foreach($line in $historyLines){
            if($line-notmatch'^- ([0-9]{4}-[0-9]{2}-[0-9]{2}): (None|Open|Investigating|Deferred|Resolved|Retired) -> (Open|Investigating|Deferred|Resolved|Retired) - (.+)$'){Throw-Wf 4 'question.history-state' 'Question history line is malformed.'}
            $date=$Matches[1];$from=$Matches[2];$to=$Matches[3];$reason=$Matches[4]
            if($first-and($from-ne'None'-or$date-ne$fields.Raised)){Throw-Wf 4 'question.history-state' 'Question history must begin at None on the raised date.'}
            if($from-ne$current){Throw-Wf 4 'question.history-state' 'Question history is not continuous.'}
            if($from-eq$to-or$from-eq'Retired'){Throw-Wf 4 'question.transition' 'Question transition is invalid.'}
            if($from-eq'Resolved'-and$to-eq'Open'-and$reason-notmatch'(?i)reopen'){Throw-Wf 4 'question.reopen-reason' 'Reopening requires an explicit reopen reason.'}
            $current=$to;$first=$false
        }
        if($current-ne$fields.State){Throw-Wf 4 'question.history-state' 'Question history does not end at current state.'}
        $resumption = if($fields.State-eq'Open'){$sections['Next step']}elseif($fields.State-eq'Investigating'){$sections['Current activity']}elseif($fields.State-eq'Deferred'){$sections['Revisit trigger']}else{$sections[($expected|Select-Object -SkipLast 1)[-1]]}
        [void]$questions.Add([ordered]@{id=$fields.ID;anchor=$anchor;title=$title;state=$fields.State;raised=$fields.Raised;appliesTo=$applies;addressedBy=$addressed;resolvedBy=$resolved;resumption=$resumption})
    }
    return ,$questions
}

function Parse-WfSourceBlocks {
    param([string]$Text,[string]$OwnerPath,[string]$WorkspaceRoot,[string]$Kind)
    $sources=[Collections.ArrayList]::new();$opens=([regex]::Matches($Text,'<!-- wayfinder:source -->')).Count;$closes=([regex]::Matches($Text,'<!-- /wayfinder:source -->')).Count
    if($opens-ne$closes){Throw-Wf 4 'source.delimiter' 'Source delimiters are unbalanced.'};if($opens-gt0-and$Kind-ne'evidence'){Throw-Wf 4 'source.owner-kind' 'Sources belong only in evidence documents.'}
    $matches=[regex]::Matches($Text,'(?ms)^<!-- wayfinder:source -->\n(.*?)^<!-- /wayfinder:source -->$');if($matches.Count-ne$opens){Throw-Wf 4 'source.delimiter' 'Source block grammar differs.'}
    foreach($match in $matches){
        $lines=$match.Groups[1].Value.Split("`n");if($lines[0]-notmatch'^<a id="(src-[0-9]+)"></a>$'){Throw-Wf 4 'source.anchor' 'Source anchor is malformed.'};$anchor=$Matches[1]
        if($lines[1]-notmatch'^### (src-[0-9]+) — (.+)$'){Throw-Wf 4 'source.anchor' 'Source heading is malformed.'};$key=$Matches[1];$title=$Matches[2];if($key-ne$anchor){Throw-Wf 4 'source.anchor' 'Source anchor and key differ.'};if(-not(Test-WfIdentifier $key source)){Throw-Wf 4 'source.key' 'Source key is invalid.'}
        $fields=[ordered]@{};$index=2;while($index-lt$lines.Count-and$lines[$index]-ne''){if($lines[$index]-notmatch'^- \*\*([A-Za-z]+):\*\* (.+)$'){Throw-Wf 4 'source.field-syntax' 'Source field is malformed.'};$name=$Matches[1];if($fields.Contains($name)){Throw-Wf 4 'source.duplicate-field' 'Source field is duplicated.'};$fields[$name]=$Matches[2];$index++}
        foreach($name in @('Citation','Original','Accessed','Applicability')){if(-not$fields.Contains($name)){Throw-Wf 4 'source.missing-field' "Source field $name is required."}}
        if($fields.Applicability-notin@('Direct','Adjacent','General')){Throw-Wf 4 'source.applicability' 'Source applicability is invalid.'};if(-not(Test-WfDate $fields.Accessed)){Throw-Wf 4 'record.date' 'Source accessed date is invalid.'};if($fields.Contains('Published')-and-not(Test-WfDate $fields.Published)){Throw-Wf 4 'record.date' 'Source published date is invalid.'}
        if(-not$fields.Original.StartsWith('https://',[StringComparison]::OrdinalIgnoreCase)){
            [void](Test-WfRelativeSourcePath $fields.Original 4);Assert-WfNoSymlinkComponents $WorkspaceRoot $fields.Original 4;$full=Join-Path $WorkspaceRoot $fields.Original
            if(-not[IO.File]::Exists($full)){Throw-Wf 4 'manifest.path-missing' 'Local source path is missing.'}
        }
        $tail=$match.Groups[1].Value.Substring(($lines[0]+"`n"+$lines[1]+"`n"+($lines[2..($index-1)]-join"`n")).Length)
        if($match.Groups[1].Value-notmatch'(?ms)\n#### Used for\n\n(.+?)\n\n#### Limitations\n\n(.+?)\n?$'){Throw-Wf 4 'source.sections' 'Source sections are incomplete.'}
        $published = if($fields.Contains('Published')){$fields.Published}else{$null}
        [void]$sources.Add([ordered]@{key=$key;title=$title;citation=$fields.Citation;original=$fields.Original;published=$published;accessed=$fields.Accessed;applicability=$fields.Applicability;usedFor=$Matches[1];limitations=$Matches[2]})
    }
    return ,$sources
}

function Parse-WfDocument {
    param([string]$Path,[string]$Relative,[string]$RecordRoot,[string]$WorkspaceRoot)
    $text=Read-WfTextFile $Path 4
    if(-not$text.EndsWith("`n")-or$text.EndsWith("`n`n")){Throw-Wf 4 'text.terminal-newline' 'Authored text requires exactly one terminal LF.'}
    foreach($line in $text.Split("`n")){if($line.EndsWith(' ')-or$line.EndsWith("`t")){Throw-Wf 4 'text.trailing-whitespace' 'Trailing whitespace is forbidden.'}}
    $lines=$text.Split("`n");if($lines.Count-lt9-or$lines[0]-notmatch'^# (.+)$'){Throw-Wf 4 'document.h1' 'Document must begin with exactly one H1.'};$title=$Matches[1]
    if($lines[1]-ne''-or$lines[2]-ne'<!-- wayfinder:metadata -->'){if($text.Contains('<!-- wayfinder:metadata -->')){Throw-Wf 4 'metadata.location' 'Metadata must immediately follow H1 and one blank line.'}else{Throw-Wf 4 'metadata.delimiter' 'Metadata delimiter is missing.'}}
    $close=[Array]::IndexOf($lines,'<!-- /wayfinder:metadata -->');if($close-lt0){Throw-Wf 4 'metadata.delimiter' 'Metadata closing delimiter is missing.'}
    $metadata=[ordered]@{};$metadataOrder=[Collections.ArrayList]::new()
    for($i=3;$i-lt$close;$i++){
        if($lines[$i]-notmatch'^- \*\*([A-Za-z-]+):\*\* (.+)$'){Throw-Wf 4 'metadata.field-syntax' 'Metadata field syntax is invalid.'};$name=$Matches[1];$value=$Matches[2]
        if($metadata.Contains($name)){Throw-Wf 4 'metadata.duplicate-field' 'Metadata field is duplicated.'};if($name-notin@('ID','Kind','Status','Updated','Summary','Decision-Date','Supersedes','Superseded-By')){Throw-Wf 4 'metadata.unknown-field' 'Unknown metadata field.'};$metadata[$name]=$value;[void]$metadataOrder.Add($name)
    }
    foreach($name in @('ID','Kind','Status','Updated','Summary')){if(-not$metadata.Contains($name)){Throw-Wf 4 'metadata.missing-field' "Required metadata field $name is missing."}}
    $expectedOrder=@('ID','Kind','Status','Updated','Summary');foreach($name in @('Decision-Date','Supersedes','Superseded-By')){if($metadata.Contains($name)){$expectedOrder+=$name}}
    if(($metadataOrder-join'|')-ne($expectedOrder-join'|')){Throw-Wf 4 'metadata.field-order' 'Metadata fields are out of order.'}
    if(-not(Test-WfIdentifier $metadata.ID document)){Throw-Wf 4 'record.document-id' 'Document ID is invalid.'}
    if($metadata.Kind-notin@('map','brief','register','evidence','decision','guide','index')){Throw-Wf 4 'document.kind' 'Document kind is invalid.'}
    $allowedStatus=if($metadata.Kind-eq'decision'){@('Proposed','Accepted','Rejected','Superseded')}else{@('Draft','Active','Superseded','Retired')};if($metadata.Status-notin$allowedStatus){Throw-Wf 4 'document.status' 'Document status is invalid for its kind.'}
    if(-not(Test-WfDate $metadata.Updated)){Throw-Wf 4 'record.date' 'Updated date is invalid.'}
    if($metadata.Kind-eq'decision'-and$metadata.Status-in@('Accepted','Rejected','Superseded')){if(-not$metadata.Contains('Decision-Date')){Throw-Wf 4 'decision.date-required' 'Decision date is required.'}}elseif($metadata.Contains('Decision-Date')){Throw-Wf 4 'decision.date-forbidden' 'Decision date is forbidden.'}
    if($metadata.Contains('Decision-Date')-and-not(Test-WfDate $metadata['Decision-Date'])){Throw-Wf 4 'record.date' 'Decision date is invalid.'}
    if($metadata.Status-eq'Superseded'-and-not$metadata.Contains('Superseded-By')){Throw-Wf 4 'supersession.required' 'Superseded document requires Superseded-By.'}
    $supersedes=[Collections.ArrayList]::new();$supersededBy=[Collections.ArrayList]::new()
    foreach($pair in @(@('Supersedes',$supersedes),@('Superseded-By',$supersededBy))){if($metadata.Contains($pair[0])){foreach($id in $metadata[$pair[0]].Split(', ')){if(-not(Test-WfIdentifier $id document)){Throw-Wf 4 'record.document-id' 'Supersession ID is invalid.'};[void]$pair[1].Add($id)};$sorted=@($pair[1]|Sort-Object{Get-WfOrdinal $_});if(($sorted-join', ')-ne$metadata[$pair[0]]){Throw-Wf 4 'supersession.order' 'Supersession IDs must be unique and numerically ordered.'}}}
    if(@([regex]::Matches($text,'(?m)^# .+$')).Count-ne1){Throw-Wf 4 'document.h1' 'Document must contain exactly one H1.'}
    $relationships=[Collections.ArrayList]::new();$bodyStart=$close+1
    if($bodyStart-lt$lines.Count-and$lines[$bodyStart]-eq''){$bodyStart++}
    if($bodyStart-lt$lines.Count-and$lines[$bodyStart]-eq'<!-- wayfinder:relationships -->'){
        $ri=$bodyStart+1;while($ri-lt$lines.Count-and$lines[$ri]-ne'<!-- /wayfinder:relationships -->'){
            if($lines[$ri]-notmatch'^- \*\*(Governed-By|Supported-By):\*\* (.+)$'){Throw-Wf 4 'relationship.link' 'Relationship line is malformed.'};$relation=$Matches[1];$links=Parse-WfLinks $Matches[2] $Relative $RecordRoot 4 'relationship.link';foreach($link in $links){[void]$relationships.Add([ordered]@{relation=$relation;id=$link.id;target=$link.target;path=$link.path})};$ri++
        };if($ri-ge$lines.Count){Throw-Wf 4 'relationship.delimiter' 'Relationship closing delimiter missing.'};$bodyStart=$ri+1;if($bodyStart-lt$lines.Count-and$lines[$bodyStart]-eq''){$bodyStart++}
    }
    $relationshipKeys=@();foreach($r in $relationships){$relationshipKeys+=$r.relation+'|'+('{0:D20}'-f(Get-WfOrdinal $r.id))}
    if(@($relationshipKeys|Select-Object -Unique).Count-ne$relationshipKeys.Count){Throw-Wf 4 'relationship.duplicate-edge' 'Relationship edge is duplicated.'};$sortedRel=@($relationshipKeys|Sort-Object);if(($sortedRel-join'|')-ne($relationshipKeys-join'|')){Throw-Wf 4 'relationship.order' 'Relationships are out of order.'}
    $body=($lines[$bodyStart..($lines.Count-2)]-join"`n")
    $h2=@([regex]::Matches($body,'(?m)^## (.+)$')|ForEach-Object{$_.Groups[1].Value})
    if($metadata.Kind-eq'decision'-and($h2-join'|')-ne('Context|Options considered|Decision|Rationale|Consequences|References|Supersession')){Throw-Wf 4 'decision.sections' 'Decision sections differ.'}
    if($metadata.Kind-eq'evidence'-and($h2-join'|')-ne('Question and scope|Method|Findings|Applicability and limitations|Evidence, inference, and hypothesis|Implications|Unknowns|Next validation|Sources')){Throw-Wf 4 'evidence.sections' 'Evidence sections differ.'}
    $questions=Parse-WfQuestionBlocks $body $Relative $RecordRoot $metadata.Kind;$sources=Parse-WfSourceBlocks $body $Relative $WorkspaceRoot $metadata.Kind
    $sourceKeys=@($sources|ForEach-Object{$_.key});if(@($sourceKeys|Select-Object -Unique).Count-ne$sourceKeys.Count){Throw-Wf 4 'source.duplicate-key' 'Source key is duplicated.'}
    foreach($claim in [regex]::Matches($body,'(?m)^- \*\*Material claim:\*\* (.+)$')){if($claim.Groups[1].Value-notmatch'\[src-[0-9]+\]\(#src-[0-9]+\)'){Throw-Wf 4 'source.material-claim' 'Material claim lacks a local source citation.'}}
    foreach($citation in [regex]::Matches($body,'\[(src-[0-9]+)\]\(#(src-[0-9]+)\)')){if($citation.Groups[1].Value-ne$citation.Groups[2].Value-or$sourceKeys-notcontains$citation.Groups[1].Value){Throw-Wf 4 'source.citation-missing' 'Local citation does not resolve.'}}
    $regions=[Collections.ArrayList]::new();$markerMatches=[regex]::Matches($body,'(?m)^<!-- wayfinder:generated[^\n]*-->$');foreach($marker in $markerMatches){if($marker.Value-notmatch'^<!-- wayfinder:generated name="([a-z0-9]+(?:-[a-z0-9]+)*)" generator="document-index-v1" input-sha256="([0-9a-f]{64})" -->$'){Throw-Wf 4 'generated.marker' 'Generated marker is malformed or unknown.'};[void]$regions.Add([ordered]@{name=$Matches[1];digest=$Matches[2];start=$marker.Index})}
    if($regions.Count-and$metadata.Kind-notin@('map','index')){Throw-Wf 4 'generated.owner-kind' 'Generated regions require map or index owner.'};$names=@($regions|ForEach-Object{$_.name});if(@($names|Select-Object -Unique).Count-ne$names.Count){Throw-Wf 4 'generated.duplicate-name' 'Generated region name is duplicated.'}
    foreach($region in $regions){$closeIndex=$body.IndexOf('<!-- /wayfinder:generated -->',$region.start,[StringComparison]::Ordinal);if($closeIndex-lt0){Throw-Wf 4 'generated.marker' 'Generated region close marker is missing.'};$nested=$body.IndexOf('<!-- wayfinder:generated',$region.start+1,[StringComparison]::Ordinal);if($nested-ge0-and$nested-lt$closeIndex){Throw-Wf 4 'generated.nested' 'Generated regions may not nest.'};$region['close']=$closeIndex+'<!-- /wayfinder:generated -->'.Length}
    return [ordered]@{path=$Relative;fullPath=$Path;text=$text;title=$title;id=$metadata.ID;kind=$metadata.Kind;status=$metadata.Status;updated=$metadata.Updated;summary=$metadata.Summary;supersedes=$supersedes;supersededBy=$supersededBy;relationships=$relationships;questions=$questions;sources=$sources;regions=$regions;module=$null;subject=$null}
}

function Get-WfIndexMembers {
    param($Owner,$Documents,$Manifest)
    if($Owner.path-eq$Manifest.entrypoint){return @($Manifest.modules|ForEach-Object{$ep=$_.entrypoint;$Documents|Where-Object{$_.path-eq$ep}})}
    $module=$Manifest.modules|Where-Object{$_.entrypoint-eq$Owner.path}|Select-Object -First 1
    if($null-ne$module){return @($Documents|Where-Object{$_.module-eq$module.id-and$_.path-ne$Owner.path})}
    foreach($m in $Manifest.modules){foreach($s in $m.subjects){if($s.entrypoint-eq$Owner.path){return @($Documents|Where-Object{$_.subject-eq($m.id+'/'+$s.id)-and$_.path-ne$Owner.path})}}}
    return @()
}

function Get-WfRegionBytes {
    param($Owner,$Documents,$Manifest,[string]$Name)
    $members=@(Get-WfIndexMembers $Owner $Documents $Manifest|Sort-Object{Get-WfOrdinal $_.id})
    $basis=[Collections.ArrayList]::new();foreach($d in $members){[void]$basis.Add([ordered]@{id=$d.id;path=$d.path;title=$d.title;kind=$d.kind;status=$d.status;summary=$d.summary})}
    $digest=Get-WfSha256Text (ConvertTo-WfCanonicalJson $basis)
    $lines=[Collections.ArrayList]::new();[void]$lines.Add("<!-- wayfinder:generated name=`"$Name`" generator=`"document-index-v1`" input-sha256=`"$digest`" -->");[void]$lines.Add('| ID | Title | Kind | Status | Summary |');[void]$lines.Add('| --- | --- | --- | --- | --- |')
    $ownerDir=[IO.Path]::GetDirectoryName($Owner.path.Replace('/',[IO.Path]::DirectorySeparatorChar));foreach($d in $members){$target=if([string]::IsNullOrEmpty($ownerDir)){$d.path}else{[IO.Path]::GetRelativePath((Join-Path '/x' $ownerDir),(Join-Path '/x' $d.path)).Replace([IO.Path]::DirectorySeparatorChar,'/')};[void]$lines.Add("| [$($d.id)]($target) | $($d.title) | $($d.kind) | $($d.status) | $($d.summary) |")};[void]$lines.Add('<!-- /wayfinder:generated -->');return $lines-join"`n"
}

function Get-WfCatalog {
    param($Documents,$Manifest)
    $docRows=[Collections.ArrayList]::new();$questionRows=[Collections.ArrayList]::new()
    foreach($d in @($Documents|Sort-Object{Get-WfOrdinal $_.id})){
        $governed=[Collections.ArrayList]::new();$supported=[Collections.ArrayList]::new();foreach($r in $d.relationships){if($r.relation-eq'Governed-By'){[void]$governed.Add($r.id)}else{[void]$supported.Add($r.id)}}
        [void]$docRows.Add([ordered]@{id=$d.id;path=$d.path;title=$d.title;kind=$d.kind;status=$d.status;updated=$d.updated;summary=$d.summary;module=$d.module;subject=$d.subject;supersedes=$d.supersedes;supersededBy=$d.supersededBy;governedBy=$governed;supportedBy=$supported})
        foreach($q in $d.questions){$a=[Collections.ArrayList]::new();foreach($x in $q.appliesTo){[void]$a.Add($x.id)};$b=[Collections.ArrayList]::new();foreach($x in $q.addressedBy){[void]$b.Add($x.id)};$c=[Collections.ArrayList]::new();foreach($x in $q.resolvedBy){[void]$c.Add($x.id)};[void]$questionRows.Add([ordered]@{id=$q.id;path=$d.path;anchor=$q.anchor;title=$q.title;state=$q.state;raised=$q.raised;appliesTo=$a;addressedBy=$b;resolvedBy=$c;resumption=$q.resumption})}
    }
    $questionRows=[Collections.ArrayList]@($questionRows|Sort-Object{Get-WfOrdinal $_.id})
    $basis=[ordered]@{manifest=$Manifest;documents=$docRows;questions=$questionRows};$digest=Get-WfSha256Text (ConvertTo-WfCanonicalJson $basis)
    return [ordered]@{format='wayfinder-document-catalog';schemaVersion=1;generator='document-catalog-v1';inputSha256=$digest;documents=$docRows;questions=$questionRows}
}

function ConvertTo-WfPrettyJsonBytes {
    param($Value)
    function ConvertTo-WfPrettyJsonInternal {
        param($Item,[int]$Depth)
        if($null-eq$Item){return 'null'}
        if($Item-is[bool]){if($Item){return 'true'}else{return 'false'}}
        if($Item-is[string]-or$Item-is[char]){return [Text.Json.JsonSerializer]::Serialize([string]$Item,$script:JsonStringOptions)}
        if($Item-is[byte]-or$Item-is[sbyte]-or$Item-is[int16]-or$Item-is[uint16]-or$Item-is[int32]-or$Item-is[uint32]-or$Item-is[int64]){return [Convert]::ToString($Item,[Globalization.CultureInfo]::InvariantCulture)}
        $indent='  '*$Depth;$childIndent='  '*($Depth+1)
        if($Item-is[Collections.IDictionary]){
            $keys=@($Item.Keys|ForEach-Object{[string]$_});if($keys.Count-eq0){return '{}'}
            $parts=[Collections.ArrayList]::new();foreach($key in $keys){[void]$parts.Add($childIndent+(ConvertTo-WfJsonInternal $key $false)+': '+(ConvertTo-WfPrettyJsonInternal $Item[$key] ($Depth+1)))}
            return "{`n"+($parts-join",`n")+"`n$indent}"
        }
        if($Item-is[Collections.IEnumerable]){
            $values=@($Item);if($values.Count-eq0){return '[]'}
            $parts=[Collections.ArrayList]::new();foreach($value in $values){[void]$parts.Add($childIndent+(ConvertTo-WfPrettyJsonInternal $value ($Depth+1)))}
            return "[`n"+($parts-join",`n")+"`n$indent]"
        }
        Throw-Wf 70 'internal.unexpected' "Cannot serialize value of type $($Item.GetType().FullName)."
    }
    $json=ConvertTo-WfPrettyJsonInternal $Value 0
    return $script:Utf8NoBom.GetBytes($json+"`n")
}

function Get-WfRecordModel {
    param([string]$WorkspaceRoot,[switch]$ValidateGenerated=$true)
    $found=Find-WfManifest $WorkspaceRoot $null;$workspace=[string]$found[0];$manifest=Read-WfJsonFile ([string]$found[1]) 4 -ManifestText;$manifestModel=Get-WfManifestModel $manifest $workspace -Live -ExitClass 4;$recordRoot=$manifestModel.recordRoot
    $documents=[Collections.ArrayList]::new();foreach($file in Get-ChildItem -LiteralPath $recordRoot -Recurse -File -Filter '*.md'|Sort-Object FullName){$rel=[IO.Path]::GetRelativePath($recordRoot,$file.FullName).Replace([IO.Path]::DirectorySeparatorChar,'/');[void]$documents.Add((Parse-WfDocument $file.FullName $rel $recordRoot $workspace))}
    $ids=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$ord=[Collections.Generic.HashSet[int64]]::new();$qids=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$qord=[Collections.Generic.HashSet[int64]]::new()
    foreach($d in $documents){if(-not$ids.Add($d.id)){Throw-Wf 4 'record.duplicate-document-id' 'Document ID is duplicated.'};if(-not$ord.Add((Get-WfOrdinal $d.id))){Throw-Wf 4 'record.duplicate-document-ordinal' 'Document ordinal is duplicated.'};foreach($q in $d.questions){if(-not$qids.Add($q.id)){Throw-Wf 4 'record.duplicate-question-id' 'Question ID is duplicated.'};if(-not$qord.Add((Get-WfOrdinal $q.id))){Throw-Wf 4 'record.duplicate-question-ordinal' 'Question ordinal is duplicated.'}}}
    foreach($d in $documents){
        if($d.path-eq$manifest.entrypoint){$d.module=$null;$d.subject=$null;continue}
        if(-not$d.path.Contains('/')){$d.module=$null;$d.subject=$null;continue}
        $owners=@($manifest.modules|Where-Object{$d.path-eq$_.root-or$d.path.StartsWith($_.root+'/')});if($owners.Count-ne1){Throw-Wf 4 'record.module-containment' 'Nested authored document must belong to exactly one module.'};$m=$owners[0];$d.module=$m.id
        foreach($s in $m.subjects){if($s.kind-eq'document'-and$d.path-eq$s.entrypoint){$d.subject=$m.id+'/'+$s.id}elseif($s.kind-eq'collection'-and($d.path-eq$s.root-or$d.path.StartsWith($s.root+'/'))){$d.subject=$m.id+'/'+$s.id}}
    }
    $entry=$documents|Where-Object{$_.path-eq$manifest.entrypoint}|Select-Object -First 1;if($null-eq$entry-or$entry.kind-ne'map'){Throw-Wf 4 'record.entrypoint-kind' 'Record entrypoint must be a map.'}
    $byId=[ordered]@{};$byPath=[ordered]@{};foreach($d in $documents){$byId[$d.id]=$d;$byPath[$d.path]=$d}
    foreach($d in $documents){
        foreach($r in $d.relationships){if(-not$byId.Contains($r.id)-or-not$byPath.Contains($r.path)-or$byPath[$r.path].id-ne$r.id){Throw-Wf 4 'relationship.target' 'Relationship ID/path target differs or is missing.'};$t=$byId[$r.id];if(($r.relation-eq'Governed-By'-and-not($t.kind-eq'decision'-and$t.status-eq'Accepted'))-or($r.relation-eq'Supported-By'-and-not($t.kind-eq'evidence'-and$t.status-eq'Active'))){Throw-Wf 4 'relationship.target-kind-status' 'Relationship target kind/status is invalid.'}}
        foreach($id in $d.supersedes){if($id-eq$d.id){Throw-Wf 4 'supersession.self-edge' 'Self supersession is forbidden.'};if(-not$byId.Contains($id)){Throw-Wf 4 'supersession.target-missing' 'Supersession target is missing.'};$t=$byId[$id];if(($d.kind-eq'decision')-ne($t.kind-eq'decision')){Throw-Wf 4 'supersession.kind' 'Supersession lifecycle families differ.'};if($t.supersededBy-notcontains$d.id){Throw-Wf 4 'supersession.reciprocal' 'Supersession edge is not reciprocal.'}}
        foreach($q in $d.questions){foreach($x in $q.appliesTo){if(-not$byId.Contains($x.id)-or-not$byPath.Contains($x.path)-or$byPath[$x.path].id-ne$x.id){Throw-Wf 4 'question.target' 'Question Applies-To target differs.'}};foreach($x in $q.addressedBy){if(-not$byId.Contains($x.id)-or$byId[$x.id].kind-ne'evidence'){Throw-Wf 4 'question.target-kind' 'Addressed-By must target evidence.'}};foreach($x in $q.resolvedBy){$t=$byId[$x.id];if($null-eq$t-or-not(($t.kind-eq'decision'-and$t.status-eq'Accepted')-or($t.kind-in@('evidence','brief')-and$t.status-eq'Active'))){Throw-Wf 4 'question.target-kind-status' 'Resolved-By target kind/status differs.'}}}
    }
    # Directed supersession cycles.
    foreach($start in $documents){$vis=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$stack=[Collections.Generic.Stack[string]]::new();$stack.Push($start.id);while($stack.Count){$id=$stack.Pop();if(-not$vis.Add($id)){Throw-Wf 4 'supersession.cycle' 'Supersession graph contains a cycle.'};foreach($next in $byId[$id].supersedes){$stack.Push($next)}}}
    $catalog=Get-WfCatalog $documents $manifest
    if($ValidateGenerated){
        foreach($d in $documents){foreach($region in $d.regions){$expected=Get-WfRegionBytes $d $documents $manifest $region.name;$openMarker="<!-- wayfinder:generated name=`"$($region.name)`" generator=`"document-index-v1`" input-sha256=`"$($region.digest)`" -->";$start=$d.text.IndexOf($openMarker,[StringComparison]::Ordinal);if($start-lt0){Throw-Wf 4 'generated.marker' 'Generated region marker cannot be located.'};$closeMarker='<!-- /wayfinder:generated -->';$end=$d.text.IndexOf($closeMarker,$start,[StringComparison]::Ordinal);if($end-lt0){Throw-Wf 4 'generated.marker' 'Generated region close marker is missing.'};$actual=$d.text.Substring($start,$end+$closeMarker.Length-$start);if($actual-ne$expected){Throw-Wf 4 'generated.stale' 'Generated region is stale.'}}}
        foreach($artifact in $manifest.generatedArtifacts){$path=Join-Path $recordRoot $artifact.path;$expected=ConvertTo-WfPrettyJsonBytes $catalog;if(-not([IO.File]::ReadAllBytes($path)-ceq$expected)){if((Get-WfSha256Bytes ([IO.File]::ReadAllBytes($path)))-ne(Get-WfSha256Bytes $expected)){Throw-Wf 4 'generated.catalog-stale' 'Generated catalog is stale.'}}}
    }
    return [ordered]@{workspaceRoot=$workspace;recordRoot=$recordRoot;manifest=$manifest;documents=$documents;catalog=$catalog}
}

function Invoke-WfValidate {
    param([System.Collections.IDictionary]$Options)
    $model=Get-WfRecordModel $Options['workspace-root'] -ValidateGenerated
    $catalogBytes=ConvertTo-WfPrettyJsonBytes $model.catalog
    return [ordered]@{
        workspace=[ordered]@{workspaceRoot=$model.workspaceRoot;recordRoot=$model.recordRoot}
        validation=[ordered]@{documents=$model.documents.Count;questions=(@($model.documents.questions)).Count;warnings=[Collections.ArrayList]::new();catalogSha256=(Get-WfSha256Bytes $catalogBytes)}
    }
}

function ConvertTo-WfMetadataBlock {
    param($Spec)
    $lines=[Collections.ArrayList]@('<!-- wayfinder:metadata -->',"- **ID:** $($Spec.id)","- **Kind:** $($Spec.kind)","- **Status:** $($Spec.status)","- **Updated:** $($Spec.updated)","- **Summary:** $($Spec.summary)")
    if($null-ne$Spec.decisionDate){[void]$lines.Add("- **Decision-Date:** $($Spec.decisionDate)")};if($Spec.supersedes.Count){[void]$lines.Add("- **Supersedes:** $($Spec.supersedes-join', ')")};if($Spec.supersededBy.Count){[void]$lines.Add("- **Superseded-By:** $($Spec.supersededBy-join', ')")};[void]$lines.Add('<!-- /wayfinder:metadata -->');return $lines-join"`n"
}

function ConvertTo-WfDocumentBytes {
    param($Spec,[string]$TemplateRoot=$script:ContractRoot)
    $required=@('output','title','id','kind','status','updated','summary','decisionDate','supersedes','supersededBy','relationships','sections','questions','sources');Assert-WfClosedObject $Spec $required $required 2
    foreach($a in @('supersedes','supersededBy','relationships','sections','questions','sources')){Assert-WfArray $Spec[$a] 2}
    foreach($name in @('output','title','id','kind','status','updated','summary')){if($Spec[$name]-isnot[string]){Throw-Wf 2 'json.type' "Render $name must be a string."}}
    $templatePath=Join-Path $script:SkillRoot "assets/contract-v1/templates/$($Spec.kind).md";if(-not[IO.File]::Exists($templatePath)){Throw-Wf 2 'document.kind' 'Unknown render kind.'};$template=Read-WfTextFile $templatePath 2
    $slots=@([regex]::Matches($template,'\{\{([A-Z_]+)\}\}')|ForEach-Object{$_.Groups[1].Value})
    $actualSlots = @($slots | Sort-Object) -join '|'
    $expectedSlots = @('CONTENT','METADATA_BLOCK','RELATIONSHIP_BLOCK','TITLE' | Sort-Object) -join '|'
    if($actualSlots-ne$expectedSlots){Throw-Wf 2 'template.slots' 'Literal template slots differ.'};if($slots.Count-ne4){Throw-Wf 2 'template.slots' 'Literal template must contain each slot once.'}
    foreach($value in (@($Spec.title,$Spec.summary)+@($Spec.sections|ForEach-Object{$_.content}))){if($value-is[string]-and$value-match'\{\{[A-Z_]+\}\}'){Throw-Wf 2 'template.recursive-slot' 'Reserved template slot occurs in supplied prose.'}}
    $rel='';if($Spec.relationships.Count){$rl=[Collections.ArrayList]@('<!-- wayfinder:relationships -->');foreach($r in $Spec.relationships){Assert-WfClosedObject $r @('relation','targetId','targetPath') @('relation','targetId','targetPath') 2;[void]$rl.Add("- **$($r.relation):** [$($r.targetId)]($($r.targetPath))")};[void]$rl.Add('<!-- /wayfinder:relationships -->');$rel=($rl-join"`n")+"`n`n"}
    $content=[Collections.ArrayList]::new();foreach($section in $Spec.sections){Assert-WfClosedObject $section @('heading','content') @('heading','content') 2;if($section.heading-isnot[string]-or$section.content-isnot[string]){Throw-Wf 2 'json.type' 'Section heading/content must be strings.'};[void]$content.Add("## $($section.heading)`n`n$($section.content)")}
    foreach($q in $Spec.questions){Assert-WfClosedObject $q @('id','title','state','raised','scope','appliesTo','addressedBy','resolvedBy','resolutionDate','sections') @('id','title','state','raised','scope','appliesTo','addressedBy','resolvedBy','resolutionDate','sections') 2;$ql=[Collections.ArrayList]@('<!-- wayfinder:question -->',"<a id=`"$($q.id)`"></a>","### $($q.title)","- **ID:** $($q.id)","- **State:** $($q.state)","- **Raised:** $($q.raised)");if($q.appliesTo.Count){[void]$ql.Add('- **Applies-To:** '+(($q.appliesTo|ForEach-Object{"[$($_.targetId)]($($_.targetPath))"})-join', '))}else{[void]$ql.Add("- **Scope:** $($q.scope)")};if($q.addressedBy.Count){[void]$ql.Add('- **Addressed-By:** '+(($q.addressedBy|ForEach-Object{"[$($_.targetId)]($($_.targetPath))"})-join', '))};if($q.resolvedBy.Count){[void]$ql.Add('- **Resolved-By:** '+(($q.resolvedBy|ForEach-Object{"[$($_.targetId)]($($_.targetPath))"})-join', '))};if($null-ne$q.resolutionDate){[void]$ql.Add("- **Resolution-Date:** $($q.resolutionDate)")};foreach($s in $q.sections){[void]$ql.Add('');[void]$ql.Add("#### $($s.heading)");[void]$ql.Add('');[void]$ql.Add($s.content)};[void]$ql.Add('<!-- /wayfinder:question -->');[void]$content.Add($ql-join"`n")}
    foreach($s in $Spec.sources){$requiredSource=@('key','title','citation','original','published','accessed','applicability','usedFor','limitations');Assert-WfClosedObject $s $requiredSource $requiredSource 2;foreach($name in @('key','title','citation','original','accessed','applicability','usedFor','limitations')){if($s[$name]-isnot[string]){Throw-Wf 2 'render.source' 'Source fields must use declared string types.'}};$sl=[Collections.ArrayList]@('<!-- wayfinder:source -->',"<a id=`"$($s.key)`"></a>","### $($s.key) — $($s.title)","- **Citation:** $($s.citation)","- **Original:** $($s.original)");if($null-ne$s.published){[void]$sl.Add("- **Published:** $($s.published)")};[void]$sl.Add("- **Accessed:** $($s.accessed)");[void]$sl.Add("- **Applicability:** $($s.applicability)");[void]$sl.Add('');[void]$sl.Add('#### Used for');[void]$sl.Add('');[void]$sl.Add($s.usedFor);[void]$sl.Add('');[void]$sl.Add('#### Limitations');[void]$sl.Add('');[void]$sl.Add($s.limitations);[void]$sl.Add('<!-- /wayfinder:source -->');[void]$content.Add($sl-join"`n")}
    $contentText=if($content.Count){($content-join"`n`n")}else{''};$rendered=$template.Replace('{{TITLE}}',$Spec.title).Replace('{{METADATA_BLOCK}}',(ConvertTo-WfMetadataBlock $Spec)).Replace('{{RELATIONSHIP_BLOCK}}',$rel).Replace('{{CONTENT}}',$contentText)
    if($rendered-match'\{\{[A-Z_]+\}\}'){Throw-Wf 2 'template.slots' 'Unexpanded reserved template slot remains.'};return $script:Utf8NoBom.GetBytes($rendered)
}

function Invoke-WfGenerate {
    param([System.Collections.IDictionary]$Options)
    $workspace=Resolve-WfPhysicalPath $Options['workspace-root'];$request=Read-WfJsonFile (Resolve-WfPhysicalPath $Options.request) 2;Assert-WfClosedObject $request @('format','schemaVersion','action') @('format','schemaVersion','action','documents','questions','paths') 2
    if($request.format-ne'wayfinder-generation-request'-or$request.schemaVersion-ne1){Throw-Wf 2 'generate.format' 'Generation request identity differs.'}
    if($request.action-notin@('allocate','render','catalog','regions')){Throw-Wf 2 'generate.action' 'Unknown generation action.'}
    if($request.action-eq'allocate'){
        Assert-WfClosedObject $request @('format','schemaVersion','action','documents','questions') @('format','schemaVersion','action','documents','questions') 2;Assert-WfArray $request.documents 2;Assert-WfArray $request.questions 2;$model=Get-WfRecordModel $workspace -ValidateGenerated:$false;$maxDoc=[int64](($model.documents|ForEach-Object{Get-WfOrdinal $_.id}|Measure-Object -Maximum).Maximum);$measuredQuestion=($model.documents.questions|ForEach-Object{Get-WfOrdinal $_.id}|Measure-Object -Maximum).Maximum;$maxQuestion=if($null-eq$measuredQuestion){[int64]0}else{[int64]$measuredQuestion};$docs=[Collections.ArrayList]::new();foreach($item in $request.documents){Assert-WfClosedObject $item @('title','mnemonic') @('title','mnemonic') 2;$mn=$item.mnemonic;if($null-eq$mn){$mn=([regex]::Matches($item.title,'[A-Za-z0-9]+')|ForEach-Object{$_.Value.ToLowerInvariant()})-join'-'};if([string]::IsNullOrEmpty($mn)-or$mn.Length-gt48-or$mn-cnotmatch'^[a-z0-9]+(?:-[a-z0-9]+)*$'){Throw-Wf 2 'allocation.mnemonic-required' 'A valid explicit mnemonic is required.'};$maxDoc++;[void]$docs.Add([ordered]@{id=('wf-{0:D4}-{1}'-f([int64]$maxDoc),$mn);candidate=$true})};$questions=[Collections.ArrayList]::new();foreach($item in $request.questions){Assert-WfClosedObject $item @('title','mnemonic') @('title','mnemonic') 2;$mn=$item.mnemonic;if($null-eq$mn){$mn=([regex]::Matches($item.title,'[A-Za-z0-9]+')|ForEach-Object{$_.Value.ToLowerInvariant()})-join'-'};if([string]::IsNullOrEmpty($mn)-or$mn.Length-gt48-or$mn-cnotmatch'^[a-z0-9]+(?:-[a-z0-9]+)*$'){Throw-Wf 2 'allocation.mnemonic-required' 'A valid explicit mnemonic is required.'};$maxQuestion++;[void]$questions.Add([ordered]@{id=('wfq-{0:D4}-{1}'-f([int64]$maxQuestion),$mn);candidate=$true})};return [ordered]@{documents=$docs;questions=$questions}
    }
    if($request.action-eq'render'){
        Assert-WfClosedObject $request @('format','schemaVersion','action','documents') @('format','schemaVersion','action','documents') 2;if(-not$Options.Contains('output-root')){Throw-Wf 2 'generate.output-root' 'Render requires output root.'};$output=Resolve-WfPhysicalPath $Options['output-root'];$prepared=[Collections.ArrayList]::new();$seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach($spec in $request.documents){[void](Test-WfPortablePath $spec.output -ExitClass 2);if(-not$seen.Add($spec.output)){Throw-Wf 2 'render.duplicate-output' 'Render outputs must be unique.'};Assert-WfNoSymlinkComponents $output $spec.output 3;$target=Join-Path $output $spec.output;if([IO.File]::Exists($target)-or[IO.Directory]::Exists($target)){Throw-Wf 3 'generate.output-exists' 'Render target already exists.'};$bytes=ConvertTo-WfDocumentBytes $spec;[void]$prepared.Add(@($target,$bytes))}
        foreach($pair in $prepared){$parent=Split-Path $pair[0]-Parent;if(-not[IO.Directory]::Exists($parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null};Write-WfBytesExclusive $pair[0] $pair[1]};return [ordered]@{rendered=$request.documents.Count;paths=[Collections.ArrayList]@($request.documents.output)}
    }
    $model=Get-WfRecordModel $workspace -ValidateGenerated:($request.action-ne'catalog'-and$request.action-ne'regions')
    if($request.action-eq'catalog'){
        Assert-WfClosedObject $request @('format','schemaVersion','action') @('format','schemaVersion','action') 2;$paths=[Collections.ArrayList]::new();$bytes=ConvertTo-WfPrettyJsonBytes $model.catalog;foreach($artifact in $model.manifest.generatedArtifacts){$target=Join-Path $model.recordRoot $artifact.path;Write-WfBytesReplace $target $bytes;[void]$paths.Add($artifact.path)};return [ordered]@{generated=$paths;catalogSha256=Get-WfSha256Bytes $bytes}
    }
    Assert-WfClosedObject $request @('format','schemaVersion','action','paths') @('format','schemaVersion','action','paths') 2;$updated=[Collections.ArrayList]::new();foreach($path in $request.paths){$doc=$model.documents|Where-Object{$_.path-eq$path}|Select-Object -First 1;if($null-eq$doc-or$doc.regions.Count-eq0){Throw-Wf 2 'generate.region-path' 'Requested path contains no declared generated region.'};$text=$doc.text;foreach($region in @($doc.regions|Sort-Object start -Descending)){$openMarker="<!-- wayfinder:generated name=`"$($region.name)`" generator=`"document-index-v1`" input-sha256=`"$($region.digest)`" -->";$start=$text.IndexOf($openMarker,[StringComparison]::Ordinal);if($start-lt0){Throw-Wf 4 'generated.marker' 'Generated region marker cannot be located.'};$closeMarker='<!-- /wayfinder:generated -->';$close=$text.IndexOf($closeMarker,$start,[StringComparison]::Ordinal);if($close-lt0){Throw-Wf 4 'generated.marker' 'Generated region close marker is missing.'};$close+=$closeMarker.Length;$replacement=Get-WfRegionBytes $doc $model.documents $model.manifest $region.name;$text=$text.Substring(0,$start)+$replacement+$text.Substring($close)};Write-WfBytesReplace $doc.fullPath $script:Utf8NoBom.GetBytes($text);[void]$updated.Add($path)};return [ordered]@{generated=$updated}
}

function Get-WfVirtualDocuments {
    param($Specs,$Manifest,[string]$WorkspaceRoot,[string]$RecordRoot)
    $documents=[Collections.ArrayList]::new()
    foreach($spec in $Specs){
        $relationships=[Collections.ArrayList]::new();foreach($r in $spec.relationships){$path=Resolve-WfDocumentLink $spec.output $r.targetPath $RecordRoot 2;[void]$relationships.Add([ordered]@{relation=$r.relation;id=$r.targetId;target=$r.targetPath;path=$path})}
        $questions=[Collections.ArrayList]::new();foreach($q in $spec.questions){$a=[Collections.ArrayList]::new();foreach($x in $q.appliesTo){[void]$a.Add([ordered]@{id=$x.targetId;path=(Resolve-WfDocumentLink $spec.output $x.targetPath $RecordRoot 2)})};$b=[Collections.ArrayList]::new();foreach($x in $q.addressedBy){[void]$b.Add([ordered]@{id=$x.targetId;path=(Resolve-WfDocumentLink $spec.output $x.targetPath $RecordRoot 2)})};$c=[Collections.ArrayList]::new();foreach($x in $q.resolvedBy){[void]$c.Add([ordered]@{id=$x.targetId;path=(Resolve-WfDocumentLink $spec.output $x.targetPath $RecordRoot 2)})};$resumption=if($q.state-eq'Open'){($q.sections|Where-Object{$_.heading-eq'Next step'}|Select-Object -First 1).content}elseif($q.state-eq'Investigating'){($q.sections|Where-Object{$_.heading-eq'Current activity'}|Select-Object -First 1).content}elseif($q.state-eq'Deferred'){($q.sections|Where-Object{$_.heading-eq'Revisit trigger'}|Select-Object -First 1).content}else{($q.sections|Where-Object{$_.heading-in@('Resolution','Retirement reason')}|Select-Object -First 1).content};[void]$questions.Add([ordered]@{id=$q.id;anchor=$q.id;title=$q.title;state=$q.state;raised=$q.raised;appliesTo=$a;addressedBy=$b;resolvedBy=$c;resumption=$resumption})}
        $d=[ordered]@{path=$spec.output;title=$spec.title;id=$spec.id;kind=$spec.kind;status=$spec.status;updated=$spec.updated;summary=$spec.summary;supersedes=[Collections.ArrayList]@($spec.supersedes);supersededBy=[Collections.ArrayList]@($spec.supersededBy);relationships=$relationships;questions=$questions;sources=[Collections.ArrayList]@($spec.sources);module=$null;subject=$null;spec=$spec}
        if($d.path-ne$Manifest.entrypoint-and$d.path.Contains('/')){$owners=@($Manifest.modules|Where-Object{$d.path-eq$_.root-or$d.path.StartsWith($_.root+'/')});if($owners.Count-ne1){Throw-Wf 4 'record.module-containment' 'Nested proposed document must belong to exactly one module.'};$m=$owners[0];$d.module=$m.id;foreach($s in $m.subjects){if($s.kind-eq'document'-and$d.path-eq$s.entrypoint){$d.subject=$m.id+'/'+$s.id}elseif($s.kind-eq'collection'-and($d.path-eq$s.root-or$d.path.StartsWith($s.root+'/'))){$d.subject=$m.id+'/'+$s.id}}}
        [void]$documents.Add($d)
    }
    return ,$documents
}

function Assert-WfProposal {
    param($Proposal,[string]$Workspace,[string]$RecordRoot)
    $required=@('format','schemaVersion','mode','profile','effectiveDate','manifest','documents','concerns','epistemicStates','omittedModules','authorityBoundary','interviewResume','materialInferences','sourceInventory','intakeLedger','materialSourcePaths','semanticReadiness');Assert-WfClosedObject $Proposal $required $required 2
    if($Proposal.format-ne'wayfinder-initialize-proposal'){Throw-Wf 2 'proposal.format' 'Proposal format differs.'};if($Proposal.schemaVersion-ne1){Throw-Wf 2 'proposal.unsupported-version' 'Proposal version differs.'};if($Proposal.mode-notin@('fresh','source-assisted')){Throw-Wf 2 'proposal.mode' 'Proposal mode differs.'};if(-not(Test-WfDate $Proposal.effectiveDate)){Throw-Wf 2 'record.date' 'Proposal effective date is invalid.'}
    Assert-WfClosedObject $Proposal.profile @('id','confirmed') @('id','confirmed') 2;if($Proposal.profile.id-notin@('foundation','evidence-led','software-product')-or$Proposal.profile.confirmed-ne$true){Throw-Wf 2 'proposal.profile' 'Starter profile must be registered and explicitly confirmed.'}
    foreach($name in @('documents','concerns','epistemicStates','omittedModules','materialInferences','materialSourcePaths')){Assert-WfArray $Proposal[$name] 2};if($Proposal.documents.Count-eq0-or$Proposal.concerns.Count-eq0){Throw-Wf 2 'proposal.structure' 'Proposal requires documents and concerns.'}
    $docIds=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$docOrd=[Collections.Generic.HashSet[int64]]::new();$questionIds=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$questionOrd=[Collections.Generic.HashSet[int64]]::new();$expectedDoc=1;$expectedQuestion=1;$paths=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach($doc in $Proposal.documents){$renderRequired=@('output','title','id','kind','status','updated','summary','decisionDate','supersedes','supersededBy','relationships','sections','questions','sources');Assert-WfClosedObject $doc $renderRequired $renderRequired 2;foreach($a in @('supersedes','supersededBy','relationships','sections','questions','sources')){Assert-WfArray $doc[$a] 2};[void](Test-WfPortablePath $doc.output -ExitClass 2);if(-not$paths.Add($doc.output)){Throw-Wf 2 'initialize.target-collision' 'Proposed target paths collide.'};if(-not(Test-WfIdentifier $doc.id document)){Throw-Wf 2 'record.document-id' 'Proposed document ID is invalid.'};if(-not$docIds.Add($doc.id)-or-not$docOrd.Add((Get-WfOrdinal $doc.id))){Throw-Wf 2 'proposal.document-id-collision' 'Proposed document IDs or ordinals collide.'};if((Get-WfOrdinal $doc.id)-ne$expectedDoc){Throw-Wf 2 'proposal.document-id-order' 'Greenfield document ordinals must begin at 1 and be consecutive.'};$expectedDoc++
        foreach($q in $doc.questions){if(-not(Test-WfIdentifier $q.id question)){Throw-Wf 2 'record.question-id' 'Proposed question ID is invalid.'};if(-not$questionIds.Add($q.id)-or-not$questionOrd.Add((Get-WfOrdinal $q.id))){Throw-Wf 2 'proposal.question-id-order' 'Question IDs or ordinals collide.'};if((Get-WfOrdinal $q.id)-ne$expectedQuestion){Throw-Wf 2 'proposal.question-id-order' 'Question ordinals must begin at 1 and be consecutive.'};$expectedQuestion++}
        foreach($section in $doc.sections){if($section.content-is[string]-and$section.content.Trim()-match'^(?i:TBD|TODO|FIXME|PLACEHOLDER|UNKNOWN)$'){Throw-Wf 2 'proposal.placeholder' 'Ambiguous placeholder content is forbidden.'}}
    }
    $homes=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);foreach($id in $docIds){[void]$homes.Add($id)};foreach($id in $questionIds){[void]$homes.Add($id)};$concerns=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);foreach($c in $Proposal.concerns){Assert-WfClosedObject $c @('id','statement','homeId') @('id','statement','homeId') 2;if(-not$concerns.Add($c.id)){Throw-Wf 2 'proposal.concern-id' 'Concern IDs must be unique.'};if(-not$homes.Contains($c.homeId)){Throw-Wf 2 'proposal.concern-home' 'Concern home does not resolve uniquely.'}}
    $enabled=@($Proposal.manifest.modules.id);$requiredOmissions=@(@('research','product','architecture','development')|Where-Object{$enabled-notcontains$_});$omitted=@($Proposal.omittedModules.id);$requiredOmissionKey=@($requiredOmissions|Sort-Object)-join'|';$omittedKey=@($omitted|Sort-Object)-join'|';if($requiredOmissionKey-ne$omittedKey){Throw-Wf 2 'proposal.omitted-module-completeness' 'Every disabled standard module requires exactly one omission.'}
    Assert-WfClosedObject $Proposal.authorityBoundary @('statement','coauthoritativePaths','competingCurrentAuthority') @('statement','coauthoritativePaths','competingCurrentAuthority') 2;Assert-WfArray $Proposal.authorityBoundary.coauthoritativePaths 2;Assert-WfArray $Proposal.authorityBoundary.competingCurrentAuthority 2;if($Proposal.authorityBoundary.competingCurrentAuthority.Count){Throw-Wf 3 'proposal.competing-authority' 'Competing current authority blocks planning.'}
    foreach($inference in $Proposal.materialInferences){if($inference.confirmed-ne$true){Throw-Wf 3 'proposal.inference-unconfirmed' 'Material agent inference is not confirmed.'}}
    Assert-WfClosedObject $Proposal.interviewResume @('summary','nextWorkflow','recommendedFocusIds') @('summary','nextWorkflow','recommendedFocusIds') 2;if($Proposal.interviewResume.nextWorkflow-ne'interview'-or$Proposal.interviewResume.recommendedFocusIds.Count-eq0){Throw-Wf 3 'proposal.semantic-readiness' 'Durable Interview resumption pointers are required.'};foreach($id in $Proposal.interviewResume.recommendedFocusIds){if(-not$homes.Contains($id)){Throw-Wf 3 'proposal.semantic-readiness' 'Interview focus ID does not resolve.'}}
    $readinessFields=@('identityAndIntent','outcomes','boundaries','people','currentKnowledge','consequentialUnknowns','structure','publicationBasis');Assert-WfClosedObject $Proposal.semanticReadiness $readinessFields $readinessFields 2;foreach($name in $readinessFields){if($Proposal.semanticReadiness[$name]-notin@('supported','explicit-unresolved')){Throw-Wf 3 'proposal.semantic-readiness' 'Readiness predicate is invalid.'};if($Proposal.semanticReadiness[$name]-eq'explicit-unresolved'-and$questionIds.Count-eq0){Throw-Wf 3 'proposal.semantic-readiness' 'Explicit unresolved readiness requires a durable question.'}}
    $entrySpec=$Proposal.documents|Where-Object{$_.output-eq$Proposal.manifest.entrypoint}|Select-Object -First 1;if($null-eq$entrySpec-or$entrySpec.kind-ne'map'-or($entrySpec.sections.heading-notcontains'Authority boundary')){Throw-Wf 3 'proposal.knowledge-map' 'Knowledge map requires an authority boundary.'}
    foreach($module in $Proposal.manifest.modules|Where-Object{$_.id.StartsWith('local-')}){$spec=$Proposal.documents|Where-Object{$_.output-eq$module.entrypoint}|Select-Object -First 1;$headings=if($null-eq$spec){@()}else{@($spec.sections.heading)};if($null-eq$spec-or@(@('Purpose','Authority boundary','Audience','Relationship to standard modules')|Where-Object{$headings-notcontains$_}).Count){Throw-Wf 3 'proposal.local-module-boundary' 'Local module requires an explicit independent governance boundary.'}}
    if($Proposal.mode-eq'fresh'){if($null-ne$Proposal.sourceInventory-or$null-ne$Proposal.intakeLedger-or$Proposal.materialSourcePaths.Count){Throw-Wf 2 'proposal.source-binding' 'Fresh proposal forbids source bindings.'}}else{if($null-eq$Proposal.sourceInventory-or$null-eq$Proposal.intakeLedger){Throw-Wf 2 'proposal.source-binding' 'Source-assisted proposal requires inventory and intake bindings.'}}
    return [ordered]@{documentIds=$docIds;questionIds=$questionIds;paths=$paths}
}

function Resolve-WfBaseline {
    param($Baseline,[string]$Workspace,[int]$ExitClass=3,[string]$Code='initialize.baseline-unresolved')
    if($Baseline.kind-eq'snapshot'){$path=Join-Path $Workspace $Baseline.path;if(-not[IO.File]::Exists($path)-or(Test-WfSymlink $path)-or(Get-WfSha256File $path)-ne$Baseline.sha256){Throw-Wf $ExitClass $Code 'Snapshot baseline cannot be resolved to exact bytes.'};return [ordered]@{kind='snapshot';path=$Baseline.path;sha256=$Baseline.sha256}}
    $loose=Join-Path $Workspace ('.git/'+$Baseline.ref);$commit=$null;if([IO.File]::Exists($loose)){$commit=([IO.File]::ReadAllText($loose)).Trim()}else{$packed=Join-Path $Workspace '.git/packed-refs';if([IO.File]::Exists($packed)){foreach($line in [IO.File]::ReadAllLines($packed)){if($line-match'^([0-9a-f]{40}|[0-9a-f]{64}) (refs/.+)$'-and$Matches[2]-eq$Baseline.ref){$commit=$Matches[1];break}}}};if($commit-notmatch'^(?:[0-9a-f]{40}|[0-9a-f]{64})$'){Throw-Wf $ExitClass $Code 'Git baseline ref is not locally resolvable.'};return [ordered]@{kind='git-ref';ref=$Baseline.ref;commit=$commit}
}

function Get-WfProposalSourceBindings {
    param($Proposal,[string]$Workspace)
    if($Proposal.mode-eq'fresh'){return [ordered]@{inventory=$null;intake=$null;materialSourcePaths=[Collections.ArrayList]::new();attachments=[ordered]@{}}}
    foreach($bindingName in @('sourceInventory','intakeLedger')){$binding=$Proposal[$bindingName];Assert-WfClosedObject $binding @('path','sha256') @('path','sha256') 2;[void](Test-WfRelativeSourcePath $binding.path 2)}
    $inventoryPath=Join-Path $Workspace $Proposal.sourceInventory.path;$intakePath=Join-Path $Workspace $Proposal.intakeLedger.path
    $inventory=Read-WfJsonFile $inventoryPath 3;$inventoryCanonical=ConvertTo-WfCanonicalJson $inventory;$inventoryDigest=Get-WfSha256Text $inventoryCanonical;if($inventoryDigest-ne$Proposal.sourceInventory.sha256){Throw-Wf 3 'initialize.inventory-digest' 'Bound inventory digest differs.'}
    # Rebuild from the inventory's own bounded declaration.
    $request=[ordered]@{format='wayfinder-source-inventory-request';schemaVersion=1;selections=[Collections.ArrayList]@($inventory.selections.path);targetRoots=$inventory.targetRoots;limits=$inventory.limits};$temp=Join-Path ([IO.Path]::GetTempPath()) ('wf-request-'+[Guid]::NewGuid().ToString('N')+'.json');try{[IO.File]::WriteAllBytes($temp,(ConvertTo-WfPrettyJsonBytes $request));$rebuilt=Invoke-WfInventory ([ordered]@{'workspace-root'=$Workspace;request=$temp});if((ConvertTo-WfCanonicalJson $rebuilt.inventory)-ne$inventoryCanonical){Throw-Wf 3 'initialize.inventory-stale' 'Current bounded source inventory differs.'}}finally{if([IO.File]::Exists($temp)){[IO.File]::Delete($temp)}}
    $ledger=Read-WfJsonFile $intakePath 3;$ledgerCanonical=ConvertTo-WfCanonicalJson $ledger;$ledgerDigest=Get-WfSha256Text $ledgerCanonical;if($ledgerDigest-ne$Proposal.intakeLedger.sha256){Throw-Wf 3 'initialize.intake-digest' 'Bound intake ledger digest differs.'};$tempLedger=Join-Path ([IO.Path]::GetTempPath()) ('wf-ledger-'+[Guid]::NewGuid().ToString('N')+'.json');try{[IO.File]::WriteAllBytes($tempLedger,(ConvertTo-WfPrettyJsonBytes $ledger));$intake=Test-WfIntake $tempLedger $Workspace $inventory $inventoryDigest}catch [WayfinderFailure]{if($_.Exception.StableCode-eq'intake.source-stale'){Throw-Wf 3 'initialize.inventory-stale' 'Current source bytes differ.'};throw}finally{if([IO.File]::Exists($tempLedger)){[IO.File]::Delete($tempLedger)}}
    $ledgerPaths=@($ledger.sources.path);foreach($path in $Proposal.materialSourcePaths){if($ledgerPaths-notcontains$path){Throw-Wf 3 'initialize.material-source-disposition' 'Material source lacks a reviewed disposition.'}}
    $attachments=[ordered]@{'inventory.json'=$script:Utf8NoBom.GetBytes($inventoryCanonical);'intake.json'=$script:Utf8NoBom.GetBytes($ledgerCanonical)}
    return [ordered]@{inventory=[ordered]@{path=$Proposal.sourceInventory.path;sha256=$inventoryDigest;bundlePath='inventory.json'};intake=[ordered]@{path=$Proposal.intakeLedger.path;sha256=$ledgerDigest;bundlePath='intake.json'};materialSourcePaths=[Collections.ArrayList]@($Proposal.materialSourcePaths);attachments=$attachments;intakeValidation=$intake}
}

function Get-WfPreview {
    param($Plan,[string]$PlanDigest,[string]$OperationId,$PayloadBytes)
    $lines=[Collections.ArrayList]@('# Wayfinder initialization review','',('- **Plan digest:** `sha256:'+$PlanDigest+'`'),('- **Operation ID:** `'+$OperationId+'`'),('- **Mode:** `'+$Plan.mode+'`'),('- **Profile:** `'+$Plan.review.profile.id+'` (confirmed)'),('- **Workspace:** `'+$Plan.workspace.workspaceRoot+'`'),('- **Record root:** `'+$Plan.manifest.recordRoot+'`'),'','## Exact target tree','')
    foreach($path in $Plan.review.targetTree){[void]$lines.Add('- `'+$path+'`')}
    [void]$lines.Add('');[void]$lines.Add('## Concern-to-home map');[void]$lines.Add('');foreach($item in $Plan.review.concernHomes){[void]$lines.Add('- `'+$item.id+'` → `'+$item.homeId+'` — '+$item.statement)}
    [void]$lines.Add('');[void]$lines.Add('## Explicit unresolved and epistemic states');[void]$lines.Add('');foreach($item in $Plan.review.epistemicStates){[void]$lines.Add('- **'+$item.state+':** '+$item.statement+' (`'+$item.targetId+'`)')}
    [void]$lines.Add('');[void]$lines.Add('## Omitted standard modules');[void]$lines.Add('');foreach($item in $Plan.review.omittedModules){[void]$lines.Add('- `'+$item.id+'` — '+$item.reason)}
    [void]$lines.Add('');[void]$lines.Add('## Authority boundary');[void]$lines.Add('');[void]$lines.Add($Plan.review.authorityBoundary.statement)
    [void]$lines.Add('');[void]$lines.Add('## Material agent inferences');[void]$lines.Add('');if($Plan.review.materialInferences.Count-eq0){[void]$lines.Add('- None declared.')}else{foreach($item in $Plan.review.materialInferences){[void]$lines.Add('- '+$item.statement+' — '+$item.basis)}}
    [void]$lines.Add('');[void]$lines.Add('## Preconditions');[void]$lines.Add('');foreach($path in $Plan.preconditions.targetsAbsent){[void]$lines.Add('- `'+$path+'` is absent.')}
    [void]$lines.Add('');[void]$lines.Add('## Ordered future operation');[void]$lines.Add('');$index=0;foreach($operation in $Plan.operations){$index++;[void]$lines.Add(('{0}. `{1}` `{2}`'-f$index,$operation.action,$operation.path))}
    [void]$lines.Add('');[void]$lines.Add('## Exact authored document payloads');[void]$lines.Add('');foreach($payload in $Plan.payloads|Where-Object{$_.role-eq'authored-document'}){[void]$lines.Add('### `'+$payload.targetPath+'` — `'+$payload.documentId+'`');[void]$lines.Add('');[void]$lines.Add('```markdown');$text=$script:Utf8Strict.GetString($PayloadBytes[$payload.bundlePath]).TrimEnd("`n");[void]$lines.Add($text);[void]$lines.Add('```');[void]$lines.Add('')}
    [void]$lines.Add('## Interview resumption');[void]$lines.Add('');[void]$lines.Add($Plan.review.interviewResume.summary);[void]$lines.Add('');[void]$lines.Add('Recommended focus: '+(($Plan.review.interviewResume.recommendedFocusIds|ForEach-Object{'`'+$_+'`'})-join', '));return($lines-join"`n")+"`n"
}

function Invoke-WfInitializePlan {
    param([System.Collections.IDictionary]$Options)
    $workspace=Resolve-WfPhysicalPath $Options['workspace-root'];if(-not[IO.Directory]::Exists($workspace)){Throw-Wf 3 'initialize.workspace' 'Workspace root must be a directory.'};$proposalPath=Resolve-WfPhysicalPath $Options.proposal;if(Test-WfSymlink $proposalPath-or-not[IO.File]::Exists($proposalPath)){Throw-Wf 2 'proposal.file' 'Proposal must be a non-symbolic regular file.'};$proposal=Read-WfJsonFile $proposalPath 2
    $bundleInput=[IO.Path]::GetFullPath($Options['bundle-root']);$bundleRoot=[IO.Path]::GetPathRoot($bundleInput);$bundleSegments=$bundleInput.Substring($bundleRoot.Length).Split([IO.Path]::DirectorySeparatorChar,[StringSplitOptions]::RemoveEmptyEntries);$cursor=$bundleRoot
    for($segmentIndex=0;$segmentIndex-lt$bundleSegments.Count;$segmentIndex++){
        $candidate=Join-Path $cursor $bundleSegments[$segmentIndex]
        if(-not[IO.File]::Exists($candidate)-and-not[IO.Directory]::Exists($candidate)-and-not(Test-WfSymlink $candidate)){for($tail=$segmentIndex;$tail-lt$bundleSegments.Count;$tail++){$cursor=Join-Path $cursor $bundleSegments[$tail]};break}
        $item=if([IO.Directory]::Exists($candidate)){[IO.DirectoryInfo]::new($candidate)}else{[IO.FileInfo]::new($candidate)}
        if($null-ne$item.LinkTarget){if($segmentIndex-ne0){Throw-Wf 3 'initialize.bundle-symlink' 'Bundle path contains a symbolic-link component.'};$cursor=$item.ResolveLinkTarget($true).FullName}else{$cursor=$candidate}
    }
    $bundleFull=[IO.Path]::GetFullPath($cursor);if(Test-WfContained $bundleFull $workspace){Throw-Wf 2 'initialize.bundle-location' 'Bundle must be outside the workspace.'};if([IO.File]::Exists($bundleFull)-or[IO.Directory]::Exists($bundleFull)-or(Test-WfSymlink $bundleFull)){Throw-Wf 3 'initialize.bundle-exists' 'Bundle target already exists.'}
    if($proposal-is[Collections.IDictionary]-and$proposal.Contains('manifest')-and$proposal.manifest-is[Collections.IDictionary]-and$proposal.manifest.Contains('recordRoot')-and$proposal.manifest.recordRoot-is[string]){Assert-WfNoSymlinkComponents $workspace $proposal.manifest.recordRoot 3}
    if($proposal-is[Collections.IDictionary]-and$proposal.Contains('documents')-and$proposal.documents-is[Collections.IList]-and$proposal.Contains('manifest')-and$proposal.manifest-is[Collections.IDictionary]-and$proposal.manifest.Contains('generatedArtifacts')-and$proposal.manifest.generatedArtifacts-is[Collections.IList]){$declaredTargets=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase);foreach($item in $proposal.documents){if($item-is[Collections.IDictionary]-and$item.Contains('output')-and$item.output-is[string]-and-not$declaredTargets.Add($item.output)){Throw-Wf 2 'initialize.target-collision' 'Proposed target paths collide.'}};foreach($item in $proposal.manifest.generatedArtifacts){if($item-is[Collections.IDictionary]-and$item.Contains('path')-and$item.path-is[string]-and-not$declaredTargets.Add($item.path)){Throw-Wf 2 'initialize.target-collision' 'Generated artifact collides with another target.'}}}
    $manifestModel=Get-WfManifestModel $proposal.manifest $workspace -ExitClass 2;$recordRoot=$manifestModel.recordRoot;[void](Assert-WfProposal $proposal $workspace $recordRoot)
    $manifestPath=Join-Path $workspace '.wayfinder/manifest.json';if([IO.File]::Exists($manifestPath)-or(Test-WfSymlink $manifestPath)){Throw-Wf 3 'initialize.manifest-exists' 'Wayfinder manifest already exists.'};$operationsRoot=Join-Path $workspace '.wayfinder/operations';if([IO.Directory]::Exists($operationsRoot)-and@(Get-ChildItem -LiteralPath $operationsRoot -Force).Count){Throw-Wf 5 'initialize.recovery-required' 'Prior initialization operation state requires recovery.'}
    Assert-WfNoSymlinkComponents $workspace $proposal.manifest.recordRoot 3
    $targetPaths=[Collections.ArrayList]::new();foreach($doc in $proposal.documents){$target=if($proposal.manifest.recordRoot-eq'.'){$doc.output}else{$proposal.manifest.recordRoot+'/'+$doc.output};[void]$targetPaths.Add($target)};foreach($artifact in $proposal.manifest.generatedArtifacts){$target=if($proposal.manifest.recordRoot-eq'.'){$artifact.path}else{$proposal.manifest.recordRoot+'/'+$artifact.path};if($targetPaths.Contains($target)){Throw-Wf 2 'initialize.target-collision' 'Generated artifact collides with another target.'};[void]$targetPaths.Add($target)};[void]$targetPaths.Add('.wayfinder/manifest.json')
    foreach($target in $targetPaths){Assert-WfNoSymlinkComponents $workspace $target 3;$full=Join-Path $workspace $target;if([IO.File]::Exists($full)-or[IO.Directory]::Exists($full)){Throw-Wf 3 'initialize.target-exists' 'Initialization target already exists.' ([ordered]@{path=$target})}}
    $moduleRoots=[Collections.ArrayList]::new();foreach($module in $proposal.manifest.modules){$target=if($proposal.manifest.recordRoot-eq'.'){$module.root}else{$proposal.manifest.recordRoot+'/'+$module.root};if([IO.Directory]::Exists((Join-Path $workspace $target))){Throw-Wf 3 'initialize.module-root-exists' 'Module root already exists.' ([ordered]@{path=$target})};[void]$moduleRoots.Add($target)}
    $baseline=Resolve-WfBaseline $proposal.manifest.canonicalBaseline $workspace 3 'initialize.baseline-unresolved';$sources=Get-WfProposalSourceBindings $proposal $workspace
    $virtual=Get-WfVirtualDocuments $proposal.documents $proposal.manifest $workspace $recordRoot;$payloadBytes=[ordered]@{};$docBytes=[ordered]@{}
    foreach($d in $virtual){$bytes=ConvertTo-WfDocumentBytes $d.spec;$text=$script:Utf8Strict.GetString($bytes);$markers=@([regex]::Matches($text,'(?ms)^<!-- wayfinder:generated name="([a-z0-9-]+)" generator="document-index-v1" input-sha256="[0-9a-f]{64}" -->\n.*?^<!-- /wayfinder:generated -->$'));for($markerIndex=$markers.Count-1;$markerIndex-ge0;$markerIndex--){$marker=$markers[$markerIndex];$replacement=Get-WfRegionBytes $d $virtual $proposal.manifest $marker.Groups[1].Value;$text=$text.Substring(0,$marker.Index)+$replacement+$text.Substring($marker.Index+$marker.Length)};$docBytes[$d.path]=$script:Utf8NoBom.GetBytes($text)}
    $catalog=Get-WfCatalog $virtual $proposal.manifest;$catalogBytes=ConvertTo-WfPrettyJsonBytes $catalog;$manifestBytes=ConvertTo-WfPrettyJsonBytes $proposal.manifest
    $payloads=[Collections.ArrayList]::new();$ordinal=1;$templateDigest=(Get-WfSha256File (Join-Path $script:ContractRoot 'templates/brief.md'))
    foreach($d in $virtual){$bundlePath='payload/{0:D4}'-f$ordinal;$target=if($proposal.manifest.recordRoot-eq'.'){$d.path}else{$proposal.manifest.recordRoot+'/'+$d.path};$bytes=$docBytes[$d.path];$payloadBytes[$bundlePath]=$bytes;[void]$payloads.Add([ordered]@{bundlePath=$bundlePath;targetPath=$target;role='authored-document';documentId=$d.id;byteLength=$bytes.Length;sha256=Get-WfSha256Bytes $bytes;producer=[ordered]@{id="template-$($d.kind)-v1";sha256=(Get-WfSha256File (Join-Path $script:ContractRoot "templates/$($d.kind).md"))}});$ordinal++}
    foreach($artifact in $proposal.manifest.generatedArtifacts){$bundlePath='payload/{0:D4}'-f$ordinal;$target=if($proposal.manifest.recordRoot-eq'.'){$artifact.path}else{$proposal.manifest.recordRoot+'/'+$artifact.path};$payloadBytes[$bundlePath]=$catalogBytes;[void]$payloads.Add([ordered]@{bundlePath=$bundlePath;targetPath=$target;role='generated-artifact';documentId=$null;byteLength=$catalogBytes.Length;sha256=Get-WfSha256Bytes $catalogBytes;producer=[ordered]@{id='document-catalog-v1';sha256=(Get-WfSha256File (Join-Path $script:SkillRoot 'references/contracts/v1.md'))}});$ordinal++}
    $bundlePath='payload/{0:D4}'-f$ordinal;$payloadBytes[$bundlePath]=$manifestBytes;[void]$payloads.Add([ordered]@{bundlePath=$bundlePath;targetPath='.wayfinder/manifest.json';role='manifest';documentId=$null;byteLength=$manifestBytes.Length;sha256=Get-WfSha256Bytes $manifestBytes;producer=[ordered]@{id='manifest-schema-v1';sha256=(Get-WfSha256File (Join-Path $script:ContractRoot 'schemas/manifest.schema.json'))}})
    $directories=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);foreach($payload in $payloads){$parent=[IO.Path]::GetDirectoryName($payload.targetPath.Replace('/',[IO.Path]::DirectorySeparatorChar));while(-not[string]::IsNullOrEmpty($parent)){[void]$directories.Add($parent.Replace([IO.Path]::DirectorySeparatorChar,'/'));$parent=[IO.Path]::GetDirectoryName($parent)}};$directoryList=@($directories|Sort-Object{($_.Split('/').Count.ToString('D4')+'|'+$_)})
    $operations=[Collections.ArrayList]::new();foreach($dir in $directoryList){[void]$operations.Add([ordered]@{action='create-directory';path=$dir})};foreach($p in $payloads|Where-Object{$_.role-ne'manifest'}){[void]$operations.Add([ordered]@{action='create-file';path=$p.targetPath;payload=$p.bundlePath;sha256=$p.sha256})};$mp=$payloads[-1];[void]$operations.Add([ordered]@{action='publish-manifest';path='.wayfinder/manifest.json';payload=$mp.bundlePath;sha256=$mp.sha256})
    $validation=[ordered]@{documents=$virtual.Count;questions=(@($virtual.questions)).Count;warnings=[Collections.ArrayList]::new();catalogSha256=Get-WfSha256Bytes $catalogBytes}
    $contractDigest=Get-WfSha256File (Join-Path $script:ContractRoot 'contract.json');$proposalDigest=Get-WfSha256Text (ConvertTo-WfCanonicalJson $proposal)
    $preconditionTargets=[Collections.ArrayList]@('.wayfinder/manifest.json');foreach($path in $targetPaths){if($path-ne'.wayfinder/manifest.json'){[void]$preconditionTargets.Add($path)}};$targetTree=@($targetPaths);[Array]::Sort($targetTree,[StringComparer]::Ordinal)
    $plan=[ordered]@{format='wayfinder-initialize-plan';schemaVersion=1;contractVersion=1;contractSha256=$contractDigest;proposalSha256=$proposalDigest;mode=$proposal.mode;effectiveDate=$proposal.effectiveDate;workspace=[ordered]@{workspaceRoot=$workspace;recordRoot=$recordRoot};manifest=$proposal.manifest;sourceBindings=[ordered]@{inventory=$sources.inventory;intake=$sources.intake;materialSourcePaths=$sources.materialSourcePaths};preconditions=[ordered]@{manifestAbsent=$true;targetsAbsent=$preconditionTargets;moduleRootsAbsent=$moduleRoots;bundleAbsent=$true;canonicalBaseline=$baseline};review=[ordered]@{profile=$proposal.profile;concernHomes=$proposal.concerns;epistemicStates=$proposal.epistemicStates;omittedModules=$proposal.omittedModules;authorityBoundary=$proposal.authorityBoundary;materialInferences=$proposal.materialInferences;interviewResume=$proposal.interviewResume;semanticReadiness=$proposal.semanticReadiness;targetTree=[Collections.ArrayList]@($targetTree)};validation=$validation;payloads=$payloads;operations=$operations}
    $planText=ConvertTo-WfCanonicalJson $plan;$planBytes=$script:Utf8NoBom.GetBytes($planText);$planDigest=Get-WfSha256Bytes $planBytes;$operationId='wfinit-'+$planDigest.Substring(0,24);if($env:WAYFINDER_TEST_MODE-eq'1'-and$env:WAYFINDER_TEST_OPERATION_ID){if($env:WAYFINDER_TEST_OPERATION_ID-notmatch'^wfinit-test-[a-z0-9]+(?:-[a-z0-9]+)*$'){Throw-Wf 2 'initialize.operation-id' 'Injected operation ID is invalid.'};$operationId=$env:WAYFINDER_TEST_OPERATION_ID};$preview=Get-WfPreview $plan $planDigest $operationId $payloadBytes
    [IO.Directory]::CreateDirectory($bundleFull)|Out-Null;try{[IO.Directory]::CreateDirectory((Join-Path $bundleFull 'payload'))|Out-Null;foreach($key in $payloadBytes.Keys){Write-WfBytesExclusive (Join-Path $bundleFull $key) $payloadBytes[$key]};foreach($key in $sources.attachments.Keys){Write-WfBytesExclusive (Join-Path $bundleFull $key) $sources.attachments[$key]};Write-WfBytesExclusive (Join-Path $bundleFull 'plan.json') $planBytes;Write-WfBytesExclusive (Join-Path $bundleFull 'preview.md') $script:Utf8NoBom.GetBytes($preview)}catch{if([IO.Directory]::Exists($bundleFull)){[IO.Directory]::Delete($bundleFull,$true)};throw}
    return [ordered]@{planSha256=$planDigest;operationId=$operationId;bundleRoot=$bundleFull;payloadCount=$payloads.Count;preview='preview.md'}
}

function Get-WfOperationTimestamp {
    if($env:WAYFINDER_TEST_MODE-eq'1'-and-not[string]::IsNullOrEmpty($env:WAYFINDER_TEST_CLOCK)){if($env:WAYFINDER_TEST_CLOCK-notmatch'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$'){Throw-Wf 2 'initialize.clock' 'Injected clock is invalid.'};return $env:WAYFINDER_TEST_CLOCK}
    return [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ',[Globalization.CultureInfo]::InvariantCulture)
}

function Invoke-WfFailureBoundary {
    param([string]$Name)
    if($env:WAYFINDER_TEST_MODE-eq'1'-and$env:WAYFINDER_TEST_FAILURE_BOUNDARY-eq$Name){Throw-Wf 5 'initialize.interrupted' "Initialization interrupted at $Name."}
}

function Read-WfPlanBundle {
    param([string]$BundleRoot)
    $bundle=Resolve-WfPhysicalPath $BundleRoot;if(-not[IO.Directory]::Exists($bundle)-or(Test-WfSymlink $bundle)){Throw-Wf 3 'initialize.bundle-members' 'Initialization bundle is missing or symbolic.'}
    $planPath=Join-Path $bundle 'plan.json';$planBytes=[IO.File]::ReadAllBytes($planPath);$plan=Read-WfJsonBytes $planBytes 2
    $fields=@('format','schemaVersion','contractVersion','contractSha256','proposalSha256','mode','effectiveDate','workspace','manifest','sourceBindings','preconditions','review','validation','payloads','operations');Assert-WfClosedObject $plan $fields $fields 2
    if($plan.format-ne'wayfinder-initialize-plan'-or$plan.schemaVersion-ne1-or$plan.contractVersion-ne1){Throw-Wf 2 'initialize.plan-format' 'Initialization plan identity differs.'}
    if((ConvertTo-WfCanonicalJson $plan)-ne$script:Utf8Strict.GetString($planBytes)){Throw-Wf 2 'initialize.plan-canonical' 'Initialization plan is not exact canonical JSON.'}
    Assert-WfArray $plan.payloads 2;Assert-WfArray $plan.operations 2
    $expected=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);[void]$expected.Add('plan.json');[void]$expected.Add('preview.md')
    foreach($payload in $plan.payloads){foreach($name in @('bundlePath','targetPath','role','documentId','byteLength','sha256','producer')){if(-not$payload.Contains($name)){Throw-Wf 2 'json.missing-field' "Plan payload is missing $name."}};[void]$expected.Add($payload.bundlePath)}
    foreach($name in @('inventory','intake')){if($null-ne$plan.sourceBindings[$name]){[void]$expected.Add($plan.sourceBindings[$name].bundlePath)}}
    $actual=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach($item in Get-ChildItem -LiteralPath $bundle -Recurse -Force){if(Test-WfSymlink $item.FullName){Throw-Wf 3 'initialize.bundle-members' 'Initialization bundle contains a symbolic link.'};if(-not$item.PSIsContainer){[void]$actual.Add([IO.Path]::GetRelativePath($bundle,$item.FullName).Replace([IO.Path]::DirectorySeparatorChar,'/'))}}
    if($actual.Count-ne$expected.Count){Throw-Wf 3 'initialize.bundle-members' 'Initialization bundle membership differs.'};foreach($path in $expected){if(-not$actual.Contains($path)){Throw-Wf 3 'initialize.bundle-members' 'Initialization bundle membership differs.'}}
    foreach($payload in $plan.payloads){$path=Join-Path $bundle $payload.bundlePath;if(-not[IO.File]::Exists($path)){Throw-Wf 3 'initialize.bundle-members' 'A declared payload is missing.'};$bytes=[IO.File]::ReadAllBytes($path);if($bytes.Length-ne[int64]$payload.byteLength-or(Get-WfSha256Bytes $bytes)-ne$payload.sha256){Throw-Wf 3 'apply.payload-digest' 'A declared payload digest differs.'}}
    return [ordered]@{root=$bundle;plan=$plan;planBytes=$planBytes;planSha256=(Get-WfSha256Bytes $planBytes)}
}

function Add-WfOperationEvent {
    param([string]$Journal,[string]$OperationId,[Collections.ArrayList]$Events,[string]$Type,[System.Collections.IDictionary]$Data,[string]$Timestamp)
    $previous=if($Events.Count){$Events[$Events.Count-1].eventSha256}else{$null};$basis=[ordered]@{format='wayfinder-initialization-event';schemaVersion=1;operationId=$OperationId;sequence=$Events.Count+1;timestamp=$Timestamp;type=$Type;previousEventSha256=$previous;data=$Data};$event=[ordered]@{};foreach($key in $basis.Keys){$event[$key]=$basis[$key]};$event.eventSha256=Get-WfSha256Text (ConvertTo-WfCanonicalJson $basis);$raw=$script:Utf8NoBom.GetBytes((ConvertTo-WfCanonicalJson $event)+"`n");$stream=[IO.FileStream]::new($Journal,[IO.FileMode]::Append,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$stream.Write($raw);$stream.Flush($true)}finally{$stream.Dispose()};[void]$Events.Add($event);return $event
}

function Test-WfApplyPreconditions {
    param($Plan,[string]$Workspace,[switch]$AllowOwned,[Collections.Generic.HashSet[string]]$Owned)
    $manifestPath=Join-Path $Workspace '.wayfinder/manifest.json';if(-not$AllowOwned-and([IO.File]::Exists($manifestPath)-or(Test-WfSymlink $manifestPath))){Throw-Wf 3 'apply.manifest-exists' 'Wayfinder manifest appeared before publication.'}
    foreach($payload in $Plan.payloads){$path=Join-Path $Workspace $payload.targetPath;if([IO.File]::Exists($path)-or[IO.Directory]::Exists($path)-or(Test-WfSymlink $path)){if(-not$AllowOwned-or$null-eq$Owned-or-not$Owned.Contains($payload.targetPath)){if($payload.role-eq'manifest'){Throw-Wf 3 'apply.manifest-exists' 'Wayfinder manifest appeared before publication.'};Throw-Wf 3 'apply.target-exists' 'An initialization target already exists.' ([ordered]@{path=$payload.targetPath})}}}
    $current=Resolve-WfBaseline $Plan.manifest.canonicalBaseline $Workspace 3 'apply.baseline-stale';if((ConvertTo-WfCanonicalJson $current)-ne(ConvertTo-WfCanonicalJson $Plan.preconditions.canonicalBaseline)){Throw-Wf 3 'apply.baseline-stale' 'Canonical baseline changed after planning.'}
    if($null-ne$Plan.sourceBindings.inventory){$inventory=Read-WfJsonFile (Join-Path $Plan.workspace.workspaceRoot $Plan.sourceBindings.inventory.path) 3;foreach($entry in $inventory.entries){if($entry.included){$path=Join-Path $Workspace $entry.path;if(-not[IO.File]::Exists($path)-or(Test-WfSymlink $path)){Throw-Wf 3 'apply.inventory-stale' 'A bound source is missing or symbolic.'};$bytes=[IO.File]::ReadAllBytes($path);if($bytes.Length-ne[int64]$entry.byteLength-or(Get-WfSha256Bytes $bytes)-ne$entry.sha256){Throw-Wf 3 'apply.inventory-stale' 'A bound source changed after planning.'}}}}
}

function Copy-WfBundleExact {
    param([string]$Source,[string]$Destination)
    [IO.Directory]::CreateDirectory($Destination)|Out-Null;foreach($item in Get-ChildItem -LiteralPath $Source -Recurse -Force){$relative=[IO.Path]::GetRelativePath($Source,$item.FullName);$target=Join-Path $Destination $relative;if($item.PSIsContainer){[IO.Directory]::CreateDirectory($target)|Out-Null}else{$parent=Split-Path $target -Parent;if(-not[IO.Directory]::Exists($parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null};Write-WfBytesExclusive $target ([IO.File]::ReadAllBytes($item.FullName))}}
}

function New-WfApplyResultData {
    param($Plan,[string]$OperationId,[string]$PlanDigest,[string]$JournalHead)
    return [ordered]@{status='completed';operationId=$OperationId;planSha256=$PlanDigest;manifest='.wayfinder/manifest.json';receipt=".wayfinder/operations/$OperationId/receipt.json";journalHeadSha256=$JournalHead;validation=$Plan.validation;handoff=[ordered]@{nextWorkflow='interview';recommendedFocusIds=$Plan.review.interviewResume.recommendedFocusIds}}
}

function New-WfReceiptBytes {
    param($Plan,[string]$BundleRoot,[string]$OperationId,[string]$PlanDigest,[string]$Timestamp,[string]$JournalHead)
    $targetRows=[Collections.ArrayList]::new()
    foreach($payload in $Plan.payloads){[void]$targetRows.Add([ordered]@{path=$payload.targetPath;sha256=$payload.sha256})}
    $targetSetDigest=Get-WfSha256Text (ConvertTo-WfCanonicalJson $targetRows)
    $counts=[ordered]@{incorporate=0;reference=0;preserveOutOfScope=0;unresolved=0}
    $ledgerDigest=$null
    if($null-ne$Plan.sourceBindings.intake){
        $ledgerDigest=$Plan.sourceBindings.intake.sha256
        $ledger=Read-WfJsonFile (Join-Path $BundleRoot $Plan.sourceBindings.intake.bundlePath) 2
        foreach($source in $ledger.sources){
            switch($source.disposition){incorporate{$counts.incorporate++}reference{$counts.reference++}'preserve-out-of-scope'{$counts.preserveOutOfScope++}unresolved{$counts.unresolved++}}
        }
    }
    $catalogPayload=$Plan.payloads|Where-Object{$_.role-eq'generated-artifact'}|Select-Object -First 1
    $openQuestions=[Collections.ArrayList]::new()
    if($null-ne$catalogPayload){
        $catalog=Read-WfJsonFile (Join-Path $BundleRoot $catalogPayload.bundlePath) 2
        foreach($question in $catalog.questions){if($question.state-in@('Open','Investigating','Deferred')){[void]$openQuestions.Add($question.id)}}
    }
    $receipt=[ordered]@{format='wayfinder-initialization-receipt';schemaVersion=1;operationId=$OperationId;completedAt=$Timestamp;mode=$Plan.mode;planSha256=$PlanDigest;contractVersion=1;contractSha256=$Plan.contractSha256;adapter=[ordered]@{id=$script:AdapterId;sha256=(Get-WfSha256File $PSCommandPath)};canonicalBaseline=$Plan.preconditions.canonicalBaseline;manifestSha256=($Plan.payloads|Where-Object{$_.role-eq'manifest'}|Select-Object -First 1).sha256;targetSetSha256=$targetSetDigest;intake=[ordered]@{ledgerDigest=$ledgerDigest;incorporate=$counts.incorporate;reference=$counts.reference;preserveOutOfScope=$counts.preserveOutOfScope;unresolved=$counts.unresolved};validation=[ordered]@{validatorVersion=1;errors=0;warnings=$Plan.validation.warnings.Count;resultSha256=(Get-WfSha256Text (ConvertTo-WfCanonicalJson $Plan.validation))};operationalIntegrity=[ordered]@{status='passed';targetCount=$Plan.payloads.Count;manifestPublishedLast=$true};semanticReadiness=[ordered]@{status='passed';predicates=$Plan.review.semanticReadiness;authorityConfirmed=$true};entrypoint=$Plan.manifest.entrypoint;openQuestionIds=$openQuestions;nextWorkflow='interview';recommendedFocusIds=$Plan.review.interviewResume.recommendedFocusIds;journalHeadSha256=$JournalHead}
    return $script:Utf8NoBom.GetBytes((ConvertTo-WfCanonicalJson $receipt))
}

function Invoke-WfInitializeApply {
    param([System.Collections.IDictionary]$Options)
    $workspace=Resolve-WfPhysicalPath $Options['workspace-root'];$bundleInfo=Read-WfPlanBundle $Options['bundle-root'];$plan=$bundleInfo.plan;$planDigest=$bundleInfo.planSha256
    if($Options['plan-sha256']-ne$planDigest){Throw-Wf 3 'apply.plan-digest' 'Supplied plan digest differs from exact plan bytes.'};if($Options['confirmation-token']-ne("wayfinder-confirm-sha256:"+$planDigest)){Throw-Wf 2 'apply.confirmation-token' 'Confirmation token does not bind the exact plan.'}
    if($plan.contractSha256-ne(Get-WfSha256File (Join-Path $script:ContractRoot 'contract.json'))){Throw-Wf 3 'apply.contract-digest' 'Plan contract digest differs from the executing contract.'};if($plan.workspace.workspaceRoot-ne$workspace){Throw-Wf 3 'apply.workspace-binding' 'Plan workspace binding differs from this physical workspace.'}
    Test-WfApplyPreconditions $plan $workspace
    $operationId='wfinit-'+$planDigest.Substring(0,24);$control=Join-Path $workspace '.wayfinder';$controlCreated=-not[IO.Directory]::Exists($control);if($controlCreated){[IO.Directory]::CreateDirectory($control)|Out-Null};$lockPath=Join-Path $control 'initialize.lock'
    if([IO.File]::Exists($lockPath)-or(Test-WfSymlink $lockPath)){Throw-Wf 5 'lock.contention' 'Another initialization lock exists.'}
    $hostName=[Net.Dns]::GetHostName();$lock=[ordered]@{format='wayfinder-initialization-lock';schemaVersion=1;operationId=$operationId;planSha256=$planDigest;owner=[ordered]@{host=$hostName;pid=$PID;token=[Guid]::NewGuid().ToString('N')}};Write-WfBytesExclusive $lockPath $script:Utf8NoBom.GetBytes((ConvertTo-WfCanonicalJson $lock)+"`n");Invoke-WfFailureBoundary 'after-lock-acquired'
    $operationRoot=Join-Path $control "operations/$operationId";if([IO.Directory]::Exists($operationRoot)){Throw-Wf 5 'initialize.recovery-required' 'Operation state already exists.'};[IO.Directory]::CreateDirectory($operationRoot)|Out-Null;$imported=Join-Path $operationRoot 'bundle';Copy-WfBundleExact $bundleInfo.root $imported
    $journal=Join-Path $operationRoot 'events.jsonl';$events=[Collections.ArrayList]::new();$timestamp=Get-WfOperationTimestamp;$targetRows=[Collections.ArrayList]::new();foreach($payload in $plan.payloads){[void]$targetRows.Add([ordered]@{path=$payload.targetPath;sha256=$payload.sha256})};$targetSetDigest=Get-WfSha256Text (ConvertTo-WfCanonicalJson $targetRows)
    [void](Add-WfOperationEvent $journal $operationId $events 'operation-recorded' ([ordered]@{planSha256=$planDigest;targetSetSha256=$targetSetDigest;targets=$targetRows;controlRootCreated=$controlCreated}) $timestamp);Invoke-WfFailureBoundary 'after-bundle-imported'
    $staging=Join-Path $operationRoot 'staging';[IO.Directory]::CreateDirectory($staging)|Out-Null;[void](Add-WfOperationEvent $journal $operationId $events 'staging-started' ([ordered]@{}) $timestamp);Invoke-WfFailureBoundary 'after-staging-started';$stageIndex=0
    foreach($payload in $plan.payloads){$stageIndex++;$target=Join-Path $staging $payload.bundlePath;$parent=Split-Path $target -Parent;if(-not[IO.Directory]::Exists($parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null};$bytes=[IO.File]::ReadAllBytes((Join-Path $imported $payload.bundlePath));Write-WfBytesExclusive $target $bytes;[void](Add-WfOperationEvent $journal $operationId $events 'payload-staged' ([ordered]@{bundlePath=$payload.bundlePath;sha256=$payload.sha256}) $timestamp);Invoke-WfFailureBoundary ('after-stage-{0:D4}'-f$stageIndex)}
    [void](Add-WfOperationEvent $journal $operationId $events 'staging-complete' ([ordered]@{}) $timestamp);Invoke-WfFailureBoundary 'after-staging-complete';Test-WfApplyPreconditions $plan $workspace;[void](Add-WfOperationEvent $journal $operationId $events 'preconditions-rechecked' ([ordered]@{}) $timestamp);Invoke-WfFailureBoundary 'after-preconditions-rechecked'
    [void](Add-WfOperationEvent $journal $operationId $events 'publication-started' ([ordered]@{}) $timestamp);Invoke-WfFailureBoundary 'after-publication-started';$directoryIndex=0;$fileIndex=0
    foreach($operation in $plan.operations){
        if($operation.action-eq'create-directory'){$directoryIndex++;$target=Join-Path $workspace $operation.path;if(-not[IO.Directory]::Exists($target)){[IO.Directory]::CreateDirectory($target)|Out-Null;[void](Add-WfOperationEvent $journal $operationId $events 'directory-created' ([ordered]@{path=$operation.path}) $timestamp)};Invoke-WfFailureBoundary ('after-directory-{0:D4}'-f$directoryIndex);continue}
        if($operation.action-eq'create-file'){$fileIndex++;Invoke-WfFailureBoundary ('before-file-{0:D4}'-f$fileIndex);[void](Add-WfOperationEvent $journal $operationId $events 'file-create-started' ([ordered]@{path=$operation.path;sha256=$operation.sha256}) $timestamp);$target=Join-Path $workspace $operation.path;Write-WfBytesExclusive $target ([IO.File]::ReadAllBytes((Join-Path $staging $operation.payload)));if((Get-WfSha256File $target)-ne$operation.sha256){Throw-Wf 5 'initialize.recovery-required' 'Published target verification failed.'};[void](Add-WfOperationEvent $journal $operationId $events 'file-created' ([ordered]@{path=$operation.path;sha256=$operation.sha256}) $timestamp);Invoke-WfFailureBoundary ('after-file-{0:D4}'-f$fileIndex);continue}
        if($operation.action-eq'publish-manifest'){Invoke-WfFailureBoundary 'before-manifest-publication';[void](Add-WfOperationEvent $journal $operationId $events 'manifest-publish-started' ([ordered]@{path=$operation.path;sha256=$operation.sha256}) $timestamp);$target=Join-Path $workspace $operation.path;Write-WfBytesExclusive $target ([IO.File]::ReadAllBytes((Join-Path $staging $operation.payload)));[void](Add-WfOperationEvent $journal $operationId $events 'manifest-published' ([ordered]@{path=$operation.path;sha256=$operation.sha256}) $timestamp);Invoke-WfFailureBoundary 'after-manifest-publication'}
    }
    [void](Add-WfOperationEvent $journal $operationId $events 'live-validation-started' ([ordered]@{}) $timestamp);Invoke-WfFailureBoundary 'after-live-validation-started';$live=Get-WfRecordModel $workspace -ValidateGenerated;foreach($payload in $plan.payloads){if((Get-WfSha256File (Join-Path $workspace $payload.targetPath))-ne$payload.sha256){Throw-Wf 5 'initialize.recovery-required' 'Live target bytes differ after publication.'}};[void](Add-WfOperationEvent $journal $operationId $events 'live-validation-complete' ([ordered]@{documents=$live.documents.Count;questions=@($live.documents.questions).Count}) $timestamp);Invoke-WfFailureBoundary 'after-live-validation-complete'
    $receiptPath=Join-Path $operationRoot 'receipt.json';$receiptBytes=New-WfReceiptBytes $plan $imported $operationId $planDigest $timestamp $events[$events.Count-1].eventSha256;Write-WfBytesExclusive $receiptPath $receiptBytes;[void](Add-WfOperationEvent $journal $operationId $events 'receipt-written' ([ordered]@{sha256=(Get-WfSha256Bytes $receiptBytes)}) $timestamp);Invoke-WfFailureBoundary 'after-receipt-written';[void](Add-WfOperationEvent $journal $operationId $events 'complete' ([ordered]@{}) $timestamp);Invoke-WfFailureBoundary 'after-complete';if([IO.Directory]::Exists($staging)){[IO.Directory]::Delete($staging,$true)};[IO.File]::Delete($lockPath)
    return New-WfApplyResultData $plan $operationId $planDigest $events[$events.Count-1].eventSha256
}

function Read-WfOperationEvents {
    param([string]$Journal,[string]$OperationId)
    $events=[Collections.ArrayList]::new();if(-not[IO.File]::Exists($Journal)){return ,$events};$bytes=[IO.File]::ReadAllBytes($Journal);try{$text=$script:Utf8Strict.GetString($bytes)}catch{return $null};if($text.Contains("`r")-or-not$text.EndsWith("`n")){return $null};$previous=$null;$sequence=0
    foreach($line in $text.TrimEnd("`n").Split("`n")){$sequence++;try{$event=Read-WfJsonBytes $script:Utf8NoBom.GetBytes($line) 2}catch{return $null};$fields=@('format','schemaVersion','operationId','sequence','timestamp','type','previousEventSha256','data','eventSha256');try{Assert-WfClosedObject $event $fields $fields 2}catch{return $null};$basis=[ordered]@{};foreach($key in $fields[0..7]){$basis[$key]=$event[$key]};if($event.operationId-ne$OperationId-or$event.sequence-ne$sequence-or$event.previousEventSha256-ne$previous-or$event.eventSha256-ne(Get-WfSha256Text (ConvertTo-WfCanonicalJson $basis))-or(ConvertTo-WfCanonicalJson $event)-ne$line){return $null};$previous=$event.eventSha256;[void]$events.Add($event)};return ,$events
}

function Test-WfOperationEventOrder {
    param($Events,$Plan)
    $expected=[Collections.ArrayList]::new()
    $targetRows=[Collections.ArrayList]::new();foreach($payload in $Plan.payloads){[void]$targetRows.Add([ordered]@{path=$payload.targetPath;sha256=$payload.sha256})}
    $operationData=[ordered]@{planSha256=(Get-WfSha256Text (ConvertTo-WfCanonicalJson $Plan));targetSetSha256=(Get-WfSha256Text (ConvertTo-WfCanonicalJson $targetRows));targets=$targetRows;controlRootCreated=$null}
    [void]$expected.Add([ordered]@{type='operation-recorded';data=$operationData})
    [void]$expected.Add([ordered]@{type='staging-started';data=[ordered]@{}})
    foreach($payload in $Plan.payloads){[void]$expected.Add([ordered]@{type='payload-staged';data=[ordered]@{bundlePath=$payload.bundlePath;sha256=$payload.sha256}})}
    foreach($type in @('staging-complete','preconditions-rechecked','publication-started')){[void]$expected.Add([ordered]@{type=$type;data=[ordered]@{}})}
    foreach($operation in $Plan.operations){
        if($operation.action-eq'create-directory'){
            if($operation.path-ne'.wayfinder'){[void]$expected.Add([ordered]@{type='directory-created';data=[ordered]@{path=$operation.path}})}
        }elseif($operation.action-eq'create-file'){
            $data=[ordered]@{path=$operation.path;sha256=$operation.sha256};[void]$expected.Add([ordered]@{type='file-create-started';data=$data});[void]$expected.Add([ordered]@{type='file-created';data=$data})
        }else{
            $data=[ordered]@{path=$operation.path;sha256=$operation.sha256};[void]$expected.Add([ordered]@{type='manifest-publish-started';data=$data});[void]$expected.Add([ordered]@{type='manifest-published';data=$data})
        }
    }
    [void]$expected.Add([ordered]@{type='live-validation-started';data=[ordered]@{}})
    [void]$expected.Add([ordered]@{type='live-validation-complete';data=$null})
    [void]$expected.Add([ordered]@{type='receipt-written';data=$null})
    [void]$expected.Add([ordered]@{type='complete';data=[ordered]@{}})
    $rollbackAt=-1;for($i=0;$i-lt$Events.Count;$i++){if($Events[$i].type-eq'rollback-started'){$rollbackAt=$i;break}};$forwardCount=if($rollbackAt-ge0){$rollbackAt}else{$Events.Count};if($forwardCount-gt$expected.Count){return $false}
    for($i=0;$i-lt$forwardCount;$i++){
        if($Events[$i].type-ne$expected[$i].type){return $false}
        if($i-eq0){if($Events[$i].data.controlRootCreated-isnot[bool]){return $false};$expected[$i].data.controlRootCreated=$Events[$i].data.controlRootCreated}
        if($null-ne$expected[$i].data-and(ConvertTo-WfCanonicalJson $Events[$i].data)-ne(ConvertTo-WfCanonicalJson $expected[$i].data)){return $false}
    }
    if($rollbackAt-ge0){for($i=$rollbackAt;$i-lt$Events.Count;$i++){if($i-eq$rollbackAt-and$Events[$i].type-ne'rollback-started'){return $false};if($i-gt$rollbackAt-and$Events[$i].type-notin@('path-removed','rollback-complete','rollback-blocked')){return $false};if($Events[$i].type-in@('rollback-complete','rollback-blocked')-and$i-ne$Events.Count-1){return $false}}}
    return $true
}

function Test-WfRecoveryOwnedState {
    param($Plan,$Events,[string]$Workspace)
    $created=[ordered]@{};$removed=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach($event in $Events){if($event.type-in@('file-created','manifest-published')){$created[$event.data.path]=$event.data.sha256};if($event.type-eq'path-removed'-and$event.data.Contains('path')){[void]$removed.Add($event.data.path)}}
    foreach($payload in $Plan.payloads){$path=Join-Path $Workspace $payload.targetPath;$exists=[IO.File]::Exists($path)-or[IO.Directory]::Exists($path)-or(Test-WfSymlink $path);if($removed.Contains($payload.targetPath)){if($exists){return $false};continue};if($created.Contains($payload.targetPath)){if(-not[IO.File]::Exists($path)-or(Test-WfSymlink $path)-or(Get-WfSha256File $path)-ne$payload.sha256){return $false}}elseif($exists){return $false}}
    return $true
}

function Get-WfImportedOperation {
    param([string]$OperationRoot,[string]$OperationId)
    try{$bundle=Read-WfPlanBundle (Join-Path $OperationRoot 'bundle');$events=Read-WfOperationEvents (Join-Path $OperationRoot 'events.jsonl') $OperationId;if($null-eq$events-or$events.Count-eq0-or-not(Test-WfOperationEventOrder $events $bundle.plan)){return $null};return [ordered]@{bundle=$bundle;events=$events}}catch{return $null}
}

function Invoke-WfResumeOperation {
    param([string]$Workspace,[string]$OperationRoot,[string]$OperationId,$BundleInfo,[Collections.ArrayList]$Events)
    $plan=$BundleInfo.plan;$journal=Join-Path $OperationRoot 'events.jsonl';$timestamp=Get-WfOperationTimestamp;$cursor=0
    function Use-WfEvent {param([string]$Type) $eventCursor=(Get-Variable cursor -Scope 1).Value;if($eventCursor-lt$Events.Count){if($Events[$eventCursor].type-ne$Type){Throw-Wf 5 'initialize.recovery-required' 'Journal cannot be resumed at this event.'};Set-Variable cursor ($eventCursor+1) -Scope 1;return $true};return $false}
    $owned=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach($event in $Events){if($event.type-in@('file-created','manifest-published')){[void]$owned.Add($event.data.path)}}
    Test-WfApplyPreconditions $plan $Workspace -AllowOwned -Owned $owned
    [void](Use-WfEvent 'operation-recorded');$staging=Join-Path $OperationRoot 'staging';if(-not(Use-WfEvent 'staging-started')){[IO.Directory]::CreateDirectory($staging)|Out-Null;[void](Add-WfOperationEvent $journal $OperationId $Events 'staging-started' ([ordered]@{}) $timestamp);$cursor++}
    foreach($payload in $plan.payloads){$target=Join-Path $staging $payload.bundlePath;if(Use-WfEvent 'payload-staged'){if(-not[IO.File]::Exists($target)-or(Get-WfSha256File $target)-ne$payload.sha256){Throw-Wf 5 'initialize.recovery-required' 'Staged payload differs.'}}else{$parent=Split-Path $target -Parent;if(-not[IO.Directory]::Exists($parent)){[IO.Directory]::CreateDirectory($parent)|Out-Null};if([IO.File]::Exists($target)){if((Get-WfSha256File $target)-ne$payload.sha256){Throw-Wf 5 'initialize.recovery-required' 'Staged payload differs.'}}else{Write-WfBytesExclusive $target ([IO.File]::ReadAllBytes((Join-Path $BundleInfo.root $payload.bundlePath)))};[void](Add-WfOperationEvent $journal $OperationId $Events 'payload-staged' ([ordered]@{bundlePath=$payload.bundlePath;sha256=$payload.sha256}) $timestamp);$cursor++}}
    if(-not(Use-WfEvent 'staging-complete')){[void](Add-WfOperationEvent $journal $OperationId $Events 'staging-complete' ([ordered]@{}) $timestamp);$cursor++};if(-not(Use-WfEvent 'preconditions-rechecked')){[void](Add-WfOperationEvent $journal $OperationId $Events 'preconditions-rechecked' ([ordered]@{}) $timestamp);$cursor++};if(-not(Use-WfEvent 'publication-started')){[void](Add-WfOperationEvent $journal $OperationId $Events 'publication-started' ([ordered]@{}) $timestamp);$cursor++}
    foreach($operation in $plan.operations){$target=Join-Path $Workspace $operation.path;if($operation.action-eq'create-directory'){if($operation.path-eq'.wayfinder'){continue};if(Use-WfEvent 'directory-created'){if(-not[IO.Directory]::Exists($target)){Throw-Wf 5 'initialize.recovery-required' 'Owned directory is missing.'}}else{if(-not[IO.Directory]::Exists($target)){[IO.Directory]::CreateDirectory($target)|Out-Null};[void](Add-WfOperationEvent $journal $OperationId $Events 'directory-created' ([ordered]@{path=$operation.path}) $timestamp);$cursor++};continue}
        if($operation.action-eq'create-file'){if(-not(Use-WfEvent 'file-create-started')){[void](Add-WfOperationEvent $journal $OperationId $Events 'file-create-started' ([ordered]@{path=$operation.path;sha256=$operation.sha256}) $timestamp);$cursor++};if(Use-WfEvent 'file-created'){if(-not[IO.File]::Exists($target)-or(Get-WfSha256File $target)-ne$operation.sha256){Throw-Wf 5 'initialize.recovery-required' 'Owned file differs.'}}else{if([IO.File]::Exists($target)){if((Get-WfSha256File $target)-ne$operation.sha256){Throw-Wf 5 'initialize.recovery-required' 'Target race blocks resume.'}}else{Write-WfBytesExclusive $target ([IO.File]::ReadAllBytes((Join-Path $staging $operation.payload)))};[void](Add-WfOperationEvent $journal $OperationId $Events 'file-created' ([ordered]@{path=$operation.path;sha256=$operation.sha256}) $timestamp);$cursor++};continue}
        if(-not(Use-WfEvent 'manifest-publish-started')){[void](Add-WfOperationEvent $journal $OperationId $Events 'manifest-publish-started' ([ordered]@{path=$operation.path;sha256=$operation.sha256}) $timestamp);$cursor++};if(Use-WfEvent 'manifest-published'){if(-not[IO.File]::Exists($target)-or(Get-WfSha256File $target)-ne$operation.sha256){Throw-Wf 5 'initialize.recovery-required' 'Owned manifest differs.'}}else{if([IO.File]::Exists($target)){Throw-Wf 5 'initialize.recovery-required' 'Unexpected manifest blocks resume.'};Write-WfBytesExclusive $target ([IO.File]::ReadAllBytes((Join-Path $staging $operation.payload)));[void](Add-WfOperationEvent $journal $OperationId $Events 'manifest-published' ([ordered]@{path=$operation.path;sha256=$operation.sha256}) $timestamp);$cursor++}
    }
    if(-not(Use-WfEvent 'live-validation-started')){[void](Add-WfOperationEvent $journal $OperationId $Events 'live-validation-started' ([ordered]@{}) $timestamp);$cursor++}
    $live=Get-WfRecordModel $Workspace -ValidateGenerated
    foreach($payload in $plan.payloads){if((Get-WfSha256File (Join-Path $Workspace $payload.targetPath))-ne$payload.sha256){Throw-Wf 5 'initialize.recovery-required' 'Live target bytes differ after publication.'}}
    if(-not(Use-WfEvent 'live-validation-complete')){[void](Add-WfOperationEvent $journal $OperationId $Events 'live-validation-complete' ([ordered]@{documents=$live.documents.Count;questions=@($live.documents.questions).Count}) $timestamp);$cursor++}
    $receiptPath=Join-Path $OperationRoot 'receipt.json'
    $receiptEvent=if($cursor-lt$Events.Count){$Events[$cursor]}else{$null}
    if($null-ne$receiptEvent-and$receiptEvent.type-ne'receipt-written'){Throw-Wf 5 'initialize.recovery-required' 'Journal cannot be resumed at the receipt event.'}
    $receiptTimestamp=if($null-ne$receiptEvent){$receiptEvent.timestamp}else{$timestamp}
    $receiptBytes=New-WfReceiptBytes $plan $BundleInfo.root $OperationId $BundleInfo.planSha256 $receiptTimestamp $Events[$cursor-1].eventSha256
    $receiptSha=Get-WfSha256Bytes $receiptBytes
    if($null-ne$receiptEvent){
        if(-not[IO.File]::Exists($receiptPath)-or(Test-WfSymlink $receiptPath)-or(Get-WfSha256File $receiptPath)-ne$receiptSha-or$receiptEvent.data.sha256-ne$receiptSha){Throw-Wf 5 'initialize.recovery-required' 'Receipt differs from the recoverable operation.'}
        $cursor++
    }else{
        if([IO.File]::Exists($receiptPath)-or(Test-WfSymlink $receiptPath)){if((Test-WfSymlink $receiptPath)-or(Get-WfSha256File $receiptPath)-ne$receiptSha){Throw-Wf 5 'initialize.recovery-required' 'Receipt differs from the recoverable operation.'}}else{Write-WfBytesExclusive $receiptPath $receiptBytes}
        [void](Add-WfOperationEvent $journal $OperationId $Events 'receipt-written' ([ordered]@{sha256=$receiptSha}) $timestamp);$cursor++
    }
    if(-not(Use-WfEvent 'complete')){[void](Add-WfOperationEvent $journal $OperationId $Events 'complete' ([ordered]@{}) $timestamp);$cursor++};if([IO.Directory]::Exists($staging)){[IO.Directory]::Delete($staging,$true)};$lockPath=Join-Path $Workspace '.wayfinder/initialize.lock';if([IO.File]::Exists($lockPath)){[IO.File]::Delete($lockPath)};return New-WfApplyResultData $plan $OperationId $BundleInfo.planSha256 $Events[$Events.Count-1].eventSha256
}

function Invoke-WfRollbackOperation {
    param([string]$Workspace,[string]$OperationRoot,[string]$OperationId,$Plan,[Collections.ArrayList]$Events)
    $journal=Join-Path $OperationRoot 'events.jsonl';$timestamp=Get-WfOperationTimestamp;$started=$Events.type-contains'rollback-started';if(-not$started){[void](Add-WfOperationEvent $journal $OperationId $Events 'rollback-started' ([ordered]@{}) $timestamp);Invoke-WfFailureBoundary 'after-rollback-started'};$already=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);foreach($event in $Events){if($event.type-eq'path-removed'){[void]$already.Add($event.data.path)}};$manual=$false;$fileIndex=0
    foreach($payload in @($Plan.payloads|Sort-Object{if($_.role-eq'manifest'){'0'}else{'1'+(9999-[int]($_.bundlePath.Split('/')[-1])).ToString('D4')}})){$fileIndex++;if($already.Contains($payload.targetPath)){continue};$created=$false;foreach($event in $Events){if($event.type-in@('file-created','manifest-published')-and$event.data.path-eq$payload.targetPath){$created=$true;break}};if(-not$created){continue};$path=Join-Path $Workspace $payload.targetPath;if(-not[IO.File]::Exists($path)-or(Test-WfSymlink $path)-or(Get-WfSha256File $path)-ne$payload.sha256){$manual=$true;continue};[IO.File]::Delete($path);[void](Add-WfOperationEvent $journal $OperationId $Events 'path-removed' ([ordered]@{path=$payload.targetPath;kind='file'}) $timestamp);Invoke-WfFailureBoundary ('after-rollback-file-{0:D4}'-f$fileIndex)}
    $directories=@($Events|Where-Object{$_.type-eq'directory-created'}|ForEach-Object{$_.data.path}|Sort-Object{-(($_.Split('/')).Count)})
    $directoryIndex=0
    foreach($relative in $directories){
        $directoryIndex++
        if($already.Contains($relative)){continue}
        $path=Join-Path $Workspace $relative
        if([IO.Directory]::Exists($path)){
            if(@(Get-ChildItem -LiteralPath $path -Force).Count-eq0){
                [IO.Directory]::Delete($path)
                [void](Add-WfOperationEvent $journal $OperationId $Events 'path-removed' ([ordered]@{path=$relative;kind='directory'}) $timestamp)
                Invoke-WfFailureBoundary ('after-rollback-directory-{0:D4}'-f$directoryIndex)
            }else{$manual=$true}
        }
    }
    if($manual){[void](Add-WfOperationEvent $journal $OperationId $Events 'rollback-blocked' ([ordered]@{}) $timestamp);return [ordered]@{status='manual-recovery';operationId=$OperationId;recoveryAction=$null}}
    [void](Add-WfOperationEvent $journal $OperationId $Events 'rollback-complete' ([ordered]@{}) $timestamp);$lockPath=Join-Path $Workspace '.wayfinder/initialize.lock';if([IO.File]::Exists($lockPath)){[IO.File]::Delete($lockPath)};return [ordered]@{status='rolled-back';operationId=$OperationId;recoveryAction=$null}
}

function Invoke-WfInitializeRecover {
    param([System.Collections.IDictionary]$Options)
    $workspace=Resolve-WfPhysicalPath $Options['workspace-root'];$operationId=$Options['operation-id'];if($operationId-notmatch'^wfinit-(?:[0-9a-f]{24}|test-[a-z0-9]+(?:-[a-z0-9]+)*)$'){Throw-Wf 2 'initialize.operation-id' 'Operation ID is invalid.'};if($Options.action-notin@('inspect','resume','rollback')){Throw-Wf 2 'recover.action' 'Recovery action is invalid.'}
    $operationRoot=Join-Path $workspace ".wayfinder/operations/$operationId";$lockPath=Join-Path $workspace '.wayfinder/initialize.lock';if(-not[IO.Directory]::Exists($operationRoot)){if([IO.File]::Exists($lockPath)){if($Options.action-eq'inspect'){return [ordered]@{status='blocked';operationId=$operationId;recoveryAction='rollback'}};if($Options.action-eq'rollback'){[IO.File]::Delete($lockPath);return [ordered]@{status='rolled-back';operationId=$operationId}}};return [ordered]@{status='manual-recovery';operationId=$operationId;recoveryAction=$null}}
    if($Options.action-ne'inspect'-and[IO.File]::Exists($lockPath)){try{$lock=Read-WfJsonFile $lockPath 5;Assert-WfClosedObject $lock @('format','schemaVersion','operationId','planSha256','owner') @('format','schemaVersion','operationId','planSha256','owner') 5;Assert-WfClosedObject $lock.owner @('host','pid','token') @('host','pid','token') 5}catch{Throw-Wf 5 'lock.manual-recovery' 'Initialization lock is malformed.'};if($lock.operationId-ne$operationId-or$lock.owner.host-ne[Net.Dns]::GetHostName()){Throw-Wf 5 'lock.contention' 'Initialization lock belongs to another operation or host.'}}
    $imported=Get-WfImportedOperation $operationRoot $operationId;if($null-eq$imported){return [ordered]@{status='manual-recovery';operationId=$operationId;recoveryAction=$null}};$events=$imported.events;$plan=$imported.bundle.plan;$ownedStateValid=Test-WfRecoveryOwnedState $plan $events $workspace;if(-not$ownedStateValid-and$Options.action-ne'rollback'){return [ordered]@{status='manual-recovery';operationId=$operationId;recoveryAction=$null}};$last=$events[$events.Count-1]
    if($last.type-eq'complete'){$receiptPath=Join-Path $operationRoot 'receipt.json';$manual=-not[IO.File]::Exists($receiptPath);if(-not$manual){try{$receipt=Read-WfJsonFile $receiptPath 2;if((ConvertTo-WfCanonicalJson $receipt)-ne$script:Utf8Strict.GetString([IO.File]::ReadAllBytes($receiptPath))){$manual=$true}}catch{$manual=$true}};if($manual){return [ordered]@{status='manual-recovery';operationId=$operationId;recoveryAction=$null}};return [ordered]@{status='completed';operationId=$operationId;recoveryAction=$null}}
    if($last.type-eq'rollback-complete'){return [ordered]@{status='rolled-back';operationId=$operationId;recoveryAction=$null}}
    if($Options.action-eq'inspect'){$recoveryAction=if($events.type-contains'rollback-started'){'rollback'}else{'resume'};return [ordered]@{status='resumable';operationId=$operationId;recoveryAction=$recoveryAction}}
    if($Options.action-eq'rollback'){return Invoke-WfRollbackOperation $workspace $operationRoot $operationId $plan $events}
    return Invoke-WfResumeOperation $workspace $operationRoot $operationId $imported.bundle $events
}

function Test-WfGovernedTextProfile {
    param([string]$Path,[byte[]]$Bytes)
    if($Bytes.Length-ge3-and$Bytes[0]-eq0xEF-and$Bytes[1]-eq0xBB-and$Bytes[2]-eq0xBF){Throw-Wf 2 'text.bom' 'Governed package text has a BOM.' ([ordered]@{path=$Path})}
    try{$text=$script:Utf8Strict.GetString($Bytes)}catch{Throw-Wf 2 'text.invalid-utf8' 'Governed package text is not strict UTF-8.' ([ordered]@{path=$Path})}
    if($text.Contains("`r")-or-not$text.EndsWith("`n")-or$text.EndsWith("`n`n")){Throw-Wf 2 'text.newline' 'Governed package text must use LF and one terminal LF.' ([ordered]@{path=$Path})}
}

function Get-WfProbeFiles {
    param([string]$LiteralPath)
    $options = [IO.EnumerationOptions]::new()
    $options.RecurseSubdirectories = $false
    $options.IgnoreInaccessible = $false
    $options.AttributesToSkip = [IO.FileAttributes]0
    $pending = [Collections.Generic.Stack[IO.DirectoryInfo]]::new()
    $pending.Push([IO.DirectoryInfo]::new($LiteralPath))
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($entry in $directory.EnumerateFileSystemInfos('*',$options)) {
            if (($entry.Attributes -band ([IO.FileAttributes]::Hidden -bor [IO.FileAttributes]::System)) -ne 0) { continue }
            if (($entry.Attributes -band [IO.FileAttributes]::Directory) -ne 0) {
                if ($null -eq $entry.LinkTarget -and ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) {
                    $pending.Push([IO.DirectoryInfo]::new($entry.FullName))
                }
            } else { $entry }
        }
    }
}

function Invoke-WfProbe {
    $releasePath=[IO.Path]::Combine($script:ContractRoot,'release.json')
    try{$release=Read-WfJsonFile $releasePath 2}catch [WayfinderFailure]{if($_.Exception.StableCode-in@('json.invalid','text.invalid-utf8','text.invalid-unicode','text.bom','text.newline','json.duplicate-key','json.number')){Throw-Wf 2 'package.release-invalid' 'Release descriptor is invalid.'};throw}
    Assert-WfClosedObject $release @('format','schemaVersion','releaseId','status','contractVersion','contractManifest','adapters','certifications') @('format','schemaVersion','releaseId','status','contractVersion','contractManifest','adapters','certifications') 2
    if($release.format-ne'wayfinder-contract-release'-or$release.schemaVersion-ne1){Throw-Wf 2 'package.release-invalid' 'Release identity differs.'};if($release.contractVersion-ne1){Throw-Wf 2 'package.contract-version' 'Release contract version differs.'}
    if($release.releaseId-notmatch'^v1-candidate-revision-[1-9][0-9]*$'-or$release.status-notin@('unactivated-candidate','unactivated-frozen','activated-frozen')){Throw-Wf 2 'package.release-schema' 'Release identity/status is outside the schema.'}
    Assert-WfClosedObject $release.contractManifest @('path','sha256') @('path','sha256') 2;if($release.contractManifest.path-ne'assets/contract-v1/contract.json'){Throw-Wf 2 'package.release-invalid' 'Contract manifest path differs.'}
    Assert-WfArray $release.adapters 2;Assert-WfArray $release.certifications 2
    $contractPath=[IO.Path]::Combine($script:SkillRoot,$release.contractManifest.path)
    if(-not[IO.File]::Exists($contractPath)){Throw-Wf 2 'package.missing-resource' 'Contract manifest is missing.'};if((Get-WfSha256File $contractPath)-ne$release.contractManifest.sha256){Throw-Wf 2 'package.resource-digest' 'Contract manifest digest differs.'}
    $contract=Read-WfJsonFile $contractPath 2;Assert-WfClosedObject $contract @('format','schemaVersion','contractVersion','candidateRevision','status','governedScopes','governedResources','registries') @('format','schemaVersion','contractVersion','candidateRevision','status','governedScopes','governedResources','registries') 2
    if($contract.format-ne'wayfinder-executable-contract'-or$contract.schemaVersion-ne1-or$contract.contractVersion-ne1){Throw-Wf 2 'package.contract-version' 'Contract manifest identity differs.'}
    if($release.releaseId-ne("v1-candidate-revision-"+$contract.candidateRevision)){Throw-Wf 2 'package.release-schema' 'Release and contract revisions disagree.'};if(($contract.status-eq'frozen')-ne($release.status-in@('unactivated-frozen','activated-frozen'))){Throw-Wf 2 'package.release-schema' 'Release and contract lifecycle statuses disagree.'}
    $schema=Read-WfJsonFile ([IO.Path]::Combine($script:ContractRoot,'schemas/release.schema.json')) 2
    $releaseIdShape=$schema.properties.releaseId;if(($releaseIdShape.Contains('const')-and$releaseIdShape.const-ne$release.releaseId)-or($releaseIdShape.Contains('pattern')-and$release.releaseId-notmatch$releaseIdShape.pattern)){Throw-Wf 2 'package.release-schema' 'Release ID disagrees with release schema.'}
    $statusShape=$schema.properties.status;if(($statusShape.Contains('const')-and$statusShape.const-ne$release.status)-or($statusShape.Contains('enum')-and$statusShape.enum-notcontains$release.status)){Throw-Wf 2 'package.release-schema' 'Release status disagrees with release schema.'}
    $adapterPaths=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$adapterIds=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$self=$null
    foreach($adapter in $release.adapters){Assert-WfClosedObject $adapter @('id','path','sha256') @('id','path','sha256') 2;if($adapter.id-notmatch'^[a-z0-9]+(?:-[a-z0-9]+)*-v1$'-or$adapter.path-notmatch'^scripts/adapters/[a-z0-9]+(?:-[a-z0-9]+)*\.(?:py|mjs|ps1)$'){Throw-Wf 2 'package.adapter-entry' 'Adapter registry entry has invalid identity.'};if(-not$adapterPaths.Add($adapter.path)-or-not$adapterIds.Add($adapter.id)){Throw-Wf 2 'package.adapter-entry' 'Adapter registry entries must be unique.'};$path=[IO.Path]::Combine($script:SkillRoot,$adapter.path);if(-not[IO.File]::Exists($path)){Throw-Wf 2 'package.missing-resource' 'Registered adapter is missing.'};if((Get-WfSha256File $path)-ne$adapter.sha256){if($adapter.path-eq$script:AdapterRelativePath){Throw-Wf 2 'package.adapter-digest' 'Executing adapter digest differs from registry.'};Throw-Wf 2 'package.adapter-digest' 'Registered adapter digest differs.'};if($adapter.path-eq$script:AdapterRelativePath){$self=$adapter}}
    if($null-eq$self-or$self.id-ne$script:AdapterId){Throw-Wf 2 'package.adapter-entry' 'Executing adapter identity is absent or mismatched.'}
    Assert-WfArray $contract.governedResources 2;Assert-WfArray $contract.governedScopes 2;$resourcePaths=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach($resource in $contract.governedResources){Assert-WfClosedObject $resource @('path','role','sha256') @('path','role','sha256') 2;if(-not$resourcePaths.Add($resource.path)){Throw-Wf 2 'package.duplicate-resource' 'Governed resource is duplicated.'};$path=[IO.Path]::Combine($script:SkillRoot,$resource.path);if(-not[IO.File]::Exists($path)){Throw-Wf 2 'package.missing-resource' 'Governed resource is missing.' ([ordered]@{path=$resource.path})};$bytes=[IO.File]::ReadAllBytes($path);if((Get-WfSha256Bytes $bytes)-ne$resource.sha256){Throw-Wf 2 'package.resource-digest' 'Governed resource digest differs.' ([ordered]@{path=$resource.path})};Test-WfGovernedTextProfile $resource.path $bytes}
    foreach($scope in $contract.governedScopes){$path=[IO.Path]::Combine($script:SkillRoot,$scope.path);if($scope.recursive){foreach($file in Get-WfProbeFiles $path){$relative=[IO.Path]::GetRelativePath($script:SkillRoot,$file.FullName).Replace([IO.Path]::DirectorySeparatorChar,'/');if(-not$resourcePaths.Contains($relative)){Throw-Wf 2 'package.unlisted-resource' 'A governed-scope resource is unlisted.' ([ordered]@{path=$relative})}}}else{if(-not$resourcePaths.Contains($scope.path)){Throw-Wf 2 'package.unlisted-resource' 'A governed resource is unlisted.'}}}
    $known=Read-WfJsonFile ([IO.Path]::Combine($script:ContractRoot,'known-answer.json')) 2;$count=0
    foreach($item in $known.sha256){$bytes=[byte[]]@($item.utf8);if((Get-WfSha256Bytes $bytes)-ne$item.expected){Throw-Wf 2 'probe.known-answer' 'SHA-256 known answer differs.'};$count++}
    foreach($item in $known.nfc){$s=[string]::new([char[]]@($item.codePoints|ForEach-Object{[char]$_}));if($s.Normalize([Text.NormalizationForm]::FormC)-ne$item.expected){Throw-Wf 2 'probe.known-answer' 'NFC known answer differs.'};$count++}
    foreach($item in $known.canonicalJson){if((ConvertTo-WfCanonicalJson $item.input)-ne$item.expected){Throw-Wf 2 'probe.known-answer' 'Canonical JSON known answer differs.'};$count++}
    foreach($item in $known.portablePaths){$allowDot=$item.Contains('allowDot')-and[bool]$item.allowDot;$accepted=$true;try{[void](Test-WfPortablePath $item.value -AllowDot:$allowDot -ExitClass 2)}catch [WayfinderFailure]{$accepted=$false};if($accepted-ne$item.accepted){Throw-Wf 2 'probe.known-answer' 'Portable path known answer differs.'};$count++}
    $capabilities=[Collections.ArrayList]@('canonical-json-integer-subset','document-catalog-v1','document-index-v1','document-render-v1','initialize-apply-v1','initialize-plan-v1','initialize-recover-v1','nfc','record-validation-v1','sha256','source-inventory-v1','strict-json','symlink-inspection','utf8-strict')
    $runtimeVersion=$PSVersionTable.PSVersion.ToString()
    return [ordered]@{adapter=[ordered]@{id=$script:AdapterId;path=$script:AdapterRelativePath;sha256=$self.sha256};contract=[ordered]@{version=1;releaseId=$release.releaseId;status=$release.status;sha256=$release.contractManifest.sha256};deterministic=[ordered]@{knownAnswers=[ordered]@{count=$count};capabilities=$capabilities};environment=[ordered]@{implementation='PowerShell';version=$runtimeVersion;platform=$PSVersionTable.Platform}}
}

function Parse-WfOptions {
    param([string[]]$Tokens)
    $options=[ordered]@{};$index=0;while($index-lt$Tokens.Count){$token=$Tokens[$index];if(-not$token.StartsWith('--')-or$index+1-ge$Tokens.Count){Throw-Wf 2 'command.arguments' 'Options require --name VALUE pairs.'};$name=$token.Substring(2);if($options.Contains($name)){Throw-Wf 2 'command.arguments' "Duplicate option: --$name"};$options[$name]=$Tokens[$index+1];$index+=2};return $options
}

function Assert-WfOptions {
    param($Options,[string[]]$Required,[string[]]$Allowed)
    foreach($name in $Required){if(-not$Options.Contains($name)){Throw-Wf 2 'command.arguments' "Missing option: --$name"}};foreach($name in @($Options.Keys)){if($Allowed-notcontains$name){Throw-Wf 2 'command.arguments' "Unknown option: --$name"}}
}

function Invoke-WfMain {
    param([string[]]$Arguments)
    $known=@('probe','discover','inventory','initialize-plan','initialize-apply','initialize-recover','validate','generate')
    $command=if($Arguments.Count){$Arguments[0]}else{'unknown'};if($known-notcontains$command){$command='unknown'}
    try{
        if($env:WAYFINDER_TEST_MODE-eq'1'-and$env:WAYFINDER_TEST_RAISE-eq'1'){throw[InvalidOperationException]::new('Injected unexpected failure.')}
        if($command-eq'unknown'){Throw-Wf 2 'command.unknown' 'Unknown Wayfinder command.'}
        $options=Parse-WfOptions @($Arguments|Select-Object -Skip 1)
        switch($command){
            probe{Assert-WfOptions $options @() @();$data=Invoke-WfProbe}
            discover{if($options.Contains('workspace-root')){Assert-WfOptions $options @('workspace-root') @('workspace-root')}else{Assert-WfOptions $options @('start') @('start')};$data=Invoke-WfDiscover $options}
            inventory{Assert-WfOptions $options @('workspace-root','request') @('workspace-root','request','ledger');$data=Invoke-WfInventory $options}
            validate{Assert-WfOptions $options @('workspace-root') @('workspace-root');$data=Invoke-WfValidate $options}
            generate{Assert-WfOptions $options @('workspace-root','request') @('workspace-root','request','output-root');$data=Invoke-WfGenerate $options}
            'initialize-plan'{Assert-WfOptions $options @('workspace-root','proposal','bundle-root') @('workspace-root','proposal','bundle-root');$data=Invoke-WfInitializePlan $options}
            'initialize-apply'{Assert-WfOptions $options @('workspace-root','bundle-root','plan-sha256','confirmation-token') @('workspace-root','bundle-root','plan-sha256','confirmation-token');$data=Invoke-WfInitializeApply $options}
            'initialize-recover'{Assert-WfOptions $options @('workspace-root','operation-id','action') @('workspace-root','operation-id','action');$data=Invoke-WfInitializeRecover $options}
        }
        Write-WfResult $command $true 'ok' $data @() 0
    }catch [WayfinderFailure]{
        $failure=[WayfinderFailure]$_.Exception;Write-WfResult $command $false $failure.StableCode ([ordered]@{}) @((New-WfDiagnostic $failure)) $failure.ExitClass
    }catch{
        if($env:WAYFINDER_TEST_DEBUG-eq'1'){[Console]::Error.WriteLine($_.Exception.ToString());[Console]::Error.WriteLine($_.InvocationInfo.PositionMessage)}
        $failure=[WayfinderFailure]::new(70,'internal.unexpected','Unexpected internal failure.',[ordered]@{});Write-WfResult $command $false $failure.StableCode ([ordered]@{}) @((New-WfDiagnostic $failure)) 70
    }
}

Invoke-WfMain $args
exit $script:ExitCode
