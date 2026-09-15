# Independent diagnostics only; the registered adapter is never rewritten.
param([Parameter(Mandatory)][string]$AdapterPath,
      [Parameter(Mandatory)][ValidateSet('minimal','probe')][string]$Scenario,
      [ValidateSet('original','startup','paths','full','control')][string]$Variant = 'original')
Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'
# PREFIX-GUARD:BEGIN
function Get-DiagnosticPrefixLength {
param($Ast,[string]$Source)
if ($null -ne $Ast.DynamicParamBlock -or $null -ne $Ast.CleanBlock -or $null -ne $Ast.ParamBlock -or $null -ne $Ast.BeginBlock -or $null -ne $Ast.ProcessBlock -or $Ast.UsingStatements.Count -ne 0 -or $null -eq $Ast.EndBlock -or ($null -ne $Ast.EndBlock.Traps -and $Ast.EndBlock.Traps.Count -ne 0)) { throw 'Unexpected adapter source shape or parse errors.' }
$statements = $Ast.EndBlock.Statements
if ($statements.Count -lt 2 -or $statements[-2].Extent.Text -cne 'Invoke-WfMain $args' -or $statements[-1].Extent.Text -cne 'exit $script:ExitCode') { throw 'Unexpected adapter dispatch boundary.' }
$prefixLength = $statements[-2].Extent.StartOffset
if (-not [string]::IsNullOrWhiteSpace($Source.Substring($statements[-1].Extent.EndOffset))) { throw 'Unexpected source after dispatch.' }
return $prefixLength
}
# PREFIX-GUARD:END
# ENUMERATION-HELPER:BEGIN
function Get-DiagnosticProbeFiles {
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
                if ($null -eq $entry.LinkTarget -and ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) { $pending.Push([IO.DirectoryInfo]::new($entry.FullName)) }
            } else { $entry }
        }
    }
}
# ENUMERATION-HELPER:END
function Get-DiagnosticFileRows {
    param($Files,[string]$Root)
    $rows = [Collections.Generic.List[string]]::new()
    foreach ($file in $Files) {
        $relative = [IO.Path]::GetRelativePath($Root,$file.FullName).Replace([IO.Path]::DirectorySeparatorChar,'/')
        $kind = if ($null -eq $file.LinkTarget) { 'file' } else { 'file-link' }
        $rows.Add($relative+'|'+$kind)
    }
    $rows.Sort([StringComparer]::Ordinal)
    return ,$rows.ToArray()
}
function Assert-DiagnosticEnumerationEqual {
    param([string]$Root)
    $expected = Get-DiagnosticFileRows @(Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction Stop) $Root
    $actual = Get-DiagnosticFileRows @(Get-DiagnosticProbeFiles $Root) $Root
    if ([string]::Join("`n",$expected) -cne [string]::Join("`n",$actual)) { throw 'Diagnostic enumeration differs from pinned oracle.' }
    return ,$actual
}

$componentTimes = [ordered]@{}
$modulesBefore = @(Get-Module | ForEach-Object { [ordered]@{name=$_.Name;version=$_.Version.ToString()} })
if (@($modulesBefore | Where-Object { $_.name -eq 'Microsoft.PowerShell.Management' }).Count -ne 0) { throw 'Management already loaded before measurement.' }
$timer = [Diagnostics.Stopwatch]::StartNew()
$adapterBytes = [IO.File]::ReadAllBytes($AdapterPath)
$adapterSource = [Text.UTF8Encoding]::new($false,$true).GetString($adapterBytes)
$timer.Stop(); $componentTimes.sourceReadDecode = $timer.Elapsed.TotalSeconds
$sourceDigest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($adapterBytes)).ToLowerInvariant()
$expectedSkillRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($AdapterPath)))
if ($Variant -eq 'control') {
    $fixture = [IO.Path]::Combine([IO.Path]::GetTempPath(),'wayfinder-enumeration-'+[Guid]::NewGuid().ToString('N'))
    $ownsFixture = $false
    $cases = [Collections.Generic.List[object]]::new()
    $permissionStatus = 'unavailable'
    try {
        [void][IO.Directory]::CreateDirectory($fixture); $ownsFixture = $true
        $empty = [IO.Path]::Combine($fixture,'empty'); [void][IO.Directory]::CreateDirectory($empty)
        $cases.Add([ordered]@{name='empty';rows=(Assert-DiagnosticEnumerationEqual $empty)})
        $tree = [IO.Path]::Combine($fixture,'tree'); [void][IO.Directory]::CreateDirectory($tree)
        foreach ($dir in @('nested','.hidden-directory','[literal]','unicode-é')) { [void][IO.Directory]::CreateDirectory([IO.Path]::Combine($tree,$dir)) }
        foreach ($file in @('visible.txt','.hidden.txt','nested/child.txt','.hidden-directory/child.txt','[literal]/wild*.txt','unicode-é/文.txt')) { [IO.File]::WriteAllText([IO.Path]::Combine($tree,$file),'fixture') }
        [void][IO.File]::CreateSymbolicLink([IO.Path]::Combine($tree,'file-link'),[IO.Path]::Combine($tree,'visible.txt'))
        [void][IO.Directory]::CreateSymbolicLink([IO.Path]::Combine($tree,'directory-link'),[IO.Path]::Combine($tree,'nested'))
        [void][IO.File]::CreateSymbolicLink([IO.Path]::Combine($tree,'broken-link'),[IO.Path]::Combine($tree,'absent.txt'))
        [void][IO.Directory]::CreateSymbolicLink([IO.Path]::Combine($tree,'nested/cycle'),$tree)
        $cases.Add([ordered]@{name='nested-hidden-literal-unicode-links-cycle';rows=(Assert-DiagnosticEnumerationEqual $tree)})
        $missing = [IO.Path]::Combine($fixture,'missing')
        $oracleFailed=$false; $helperFailed=$false
        try { [void]@(Get-ChildItem -LiteralPath $missing -Recurse -File -ErrorAction Stop) } catch { $oracleFailed=$true }
        try { [void]@(Get-DiagnosticProbeFiles $missing) } catch { $helperFailed=$true }
        if (-not $oracleFailed -or -not $helperFailed) { throw 'Missing-root failure differs.' }
        $cases.Add([ordered]@{name='missing-root';failureEquality=$true})
        $denied = [IO.Path]::Combine($fixture,'denied'); [void][IO.Directory]::CreateDirectory($denied)
        [IO.File]::WriteAllText([IO.Path]::Combine($denied,'file.txt'),'denied')
        try {
            [IO.File]::SetUnixFileMode($denied,[IO.UnixFileMode]0)
            $oracleFailed=$false; $helperFailed=$false
            try { [void]@(Get-ChildItem -LiteralPath $denied -Recurse -File -ErrorAction Stop) } catch { $oracleFailed=$true }
            try { [void]@(Get-DiagnosticProbeFiles $denied) } catch { $helperFailed=$true }
            if ($oracleFailed -ne $helperFailed) { throw 'Permission failure differs.' }
            if ($oracleFailed) { $permissionStatus='passed' }
        } finally { [IO.File]::SetUnixFileMode($denied,[IO.UnixFileMode]::UserRead -bor [IO.UnixFileMode]::UserWrite -bor [IO.UnixFileMode]::UserExecute) }
        $contract = ConvertFrom-Json ([IO.File]::ReadAllText([IO.Path]::Combine($expectedSkillRoot,'assets/contract-v1/contract.json')))
        $scopes = [Collections.Generic.List[object]]::new()
        foreach ($scope in $contract.governedScopes) {
            if ($scope.recursive) {
                $scopeRoot=[IO.Path]::Combine($expectedSkillRoot,$scope.path)
                $scopes.Add([ordered]@{path=$scope.path;rows=(Assert-DiagnosticEnumerationEqual $scopeRoot)})
            }
        }
        if ($scopes.Count -eq 0) { throw 'No real recursive scopes checked.' }
        $report=[ordered]@{format='wayfinder-powershell-probe-compatibility';schemaVersion=1;complete=$true;adapterSha256=$sourceDigest;adapterPath=$AdapterPath;skillRoot=$expectedSkillRoot;runtimeVersion=$PSVersionTable.PSVersion.ToString();fixtures=$cases.ToArray();recursiveScopes=$scopes.ToArray();permissionStatus=$permissionStatus}
        [Console]::Out.WriteLine((ConvertTo-Json -InputObject $report -Depth 50 -Compress))
    } finally { if ($ownsFixture) { [IO.Directory]::Delete($fixture,$true) } }
    exit 0
}

$tokens = $null; $parseErrors = $null
$timer.Restart()
$fullAst = [System.Management.Automation.Language.Parser]::ParseInput($adapterSource,$AdapterPath,[ref]$tokens,[ref]$parseErrors)
$timer.Stop(); $componentTimes.fullSourceParse = $timer.Elapsed.TotalSeconds
if ($parseErrors.Count -ne 0) { throw 'Adapter did not parse.' }
$prefixLength = Get-DiagnosticPrefixLength $fullAst $adapterSource
$prefixSource = $adapterSource.Substring(0,$prefixLength)
$timer.Restart()
# TRANSFORM-GUARD:BEGIN
$originalAssignments = @(
    '$script:SkillRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent',
    '$script:ContractRoot = Join-Path $script:SkillRoot ''assets/contract-v1'''
)
$replacementAssignments = @(
    '$script:SkillRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($PSScriptRoot))',
    '$script:ContractRoot = [IO.Path]::Combine($script:SkillRoot,''assets/contract-v1'')'
)
foreach ($assignment in $originalAssignments) {
    $matches = @($fullAst.EndBlock.Statements | Where-Object { $_ -is [System.Management.Automation.Language.AssignmentStatementAst] -and $_.Extent.Text -ceq $assignment })
    if ($matches.Count -ne 1 -or [regex]::Matches($adapterSource,[regex]::Escape($assignment)).Count -ne 1) { throw 'Startup assignment is missing, duplicated or not top-level.' }
}
# TRANSFORM-GUARD:END
# PROBE-TRANSFORM-GUARD:BEGIN
$probeFunctions = @($fullAst.FindAll({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -ceq 'Invoke-WfProbe'},$true))
$topLevelProbe = @($fullAst.EndBlock.Statements | Where-Object { $_ -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $_.Name -ceq 'Invoke-WfProbe' })
if ($probeFunctions.Count -ne 1 -or $topLevelProbe.Count -ne 1 -or $adapterSource.Contains('Get-DiagnosticProbeFiles')) { throw 'Probe function/helper name shape differs.' }
$probeReplacements = [ordered]@{
    'Join-Path $script:ContractRoot ''release.json''' = '[IO.Path]::Combine($script:ContractRoot,''release.json'')'
    'Join-Path $script:SkillRoot $release.contractManifest.path' = '[IO.Path]::Combine($script:SkillRoot,$release.contractManifest.path)'
    'Join-Path $script:ContractRoot ''schemas/release.schema.json''' = '[IO.Path]::Combine($script:ContractRoot,''schemas/release.schema.json'')'
    'Join-Path $script:SkillRoot $adapter.path' = '[IO.Path]::Combine($script:SkillRoot,$adapter.path)'
    'Join-Path $script:SkillRoot $resource.path' = '[IO.Path]::Combine($script:SkillRoot,$resource.path)'
    'Join-Path $script:SkillRoot $scope.path' = '[IO.Path]::Combine($script:SkillRoot,$scope.path)'
    'Join-Path $script:ContractRoot ''known-answer.json''' = '[IO.Path]::Combine($script:ContractRoot,''known-answer.json'')'
    'Get-ChildItem -LiteralPath $path -Recurse -File' = 'Get-DiagnosticProbeFiles $path'
}
$commands = @($topLevelProbe[0].Body.FindAll({param($node) $node -is [System.Management.Automation.Language.CommandAst] -and $node.GetCommandName() -in @('Join-Path','Get-ChildItem')},$true))
if ($commands.Count -ne 8) { throw 'Probe command count differs.' }
foreach ($command in $commands) {
    if (-not $probeReplacements.Contains($command.Extent.Text) -or @($commands | Where-Object { $_.Extent.Text -ceq $command.Extent.Text }).Count -ne 1) { throw 'Probe command extent/arguments differ.' }
    $owner=$command.Parent
    while ($null -ne $owner -and $owner -isnot [System.Management.Automation.Language.FunctionDefinitionAst]) { $owner=$owner.Parent }
    if ($owner.Name -cne 'Invoke-WfProbe') { throw 'Nested probe replacement is unsupported.' }
}
# PROBE-TRANSFORM-GUARD:END
if ($Variant -in @('paths','full')) {
    $orderedCommands = @($commands)
    [Array]::Reverse($orderedCommands)
    $previousOffset = $prefixSource.Length
    foreach ($command in $orderedCommands) {
        if ($command.Extent.StartOffset -ge $previousOffset) { throw 'Probe command extents are not in source order.' }
        $previousOffset = $command.Extent.StartOffset
        if ($Variant -eq 'paths' -and $command.GetCommandName() -eq 'Get-ChildItem') { continue }
        $offset=$command.Extent.StartOffset;$length=$command.Extent.EndOffset-$offset
        $prefixSource=$prefixSource.Remove($offset,$length).Insert($offset,$probeReplacements[$command.Extent.Text])
    }
}
if ($Variant -ne 'original') {
    for ($assignmentIndex=0; $assignmentIndex -lt 2; $assignmentIndex++) {
        $prefixSource = $prefixSource.Replace($originalAssignments[$assignmentIndex],$replacementAssignments[$assignmentIndex])
    }
}
$timer.Stop()
if ($Variant -ne 'original') { $componentTimes.startupTransformation = $timer.Elapsed.TotalSeconds }
$prefixDigest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.UTF8Encoding]::new($false,$true).GetBytes($prefixSource))).ToLowerInvariant()
$timer.Restart()
$prefixAst = [System.Management.Automation.Language.Parser]::ParseInput($prefixSource,$AdapterPath,[ref]$tokens,[ref]$parseErrors)
$timer.Stop(); $componentTimes.diagnosticPrefixParse = $timer.Elapsed.TotalSeconds
if ($parseErrors.Count -ne 0) { throw 'Diagnostic prefix did not parse.' }
$timer.Restart()
$initializationBlock = $prefixAst.GetScriptBlock()
$timer.Stop(); $componentTimes.scriptBlockCreation = $timer.Elapsed.TotalSeconds
if ($initializationBlock.File -cne $AdapterPath) { throw 'Diagnostic source path metadata differs.' }
$modulesBeforeLoad = @(Get-Module | ForEach-Object { [ordered]@{name=$_.Name;version=$_.Version.ToString()} })
if (@($modulesBeforeLoad | Where-Object { $_.name -eq 'Microsoft.PowerShell.Management' }).Count -ne 0) { throw 'Management loaded before intended load interval.' }
$timer.Restart()
. $initializationBlock
$timer.Stop(); $componentTimes.loadInitialization = $timer.Elapsed.TotalSeconds
$expectedSkillRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($AdapterPath)))
if ($script:SkillRoot -cne $expectedSkillRoot -or $script:AdapterId -cne 'powershell-v1' -or $script:ContractRoot -cne [IO.Path]::Combine($expectedSkillRoot,'assets/contract-v1')) { throw 'Diagnostic original skill root/identity differs.' }
$modulesAfter = @(Get-Module | ForEach-Object { [ordered]@{name=$_.Name;version=$_.Version.ToString()} })
if ($Variant -ne 'original' -and @($modulesAfter | Where-Object { $_.name -eq 'Microsoft.PowerShell.Management' }).Count -ne 0) { throw 'Management loaded during .NET startup.' }
$payload = [ordered]@{format='wayfinder-command-result';schemaVersion=1;ok=$true;command='probe';code='ok';data=[ordered]@{};diagnostics=[Collections.ArrayList]@()}
if ($Scenario -eq 'probe') {
    $timer.Restart(); $payload.data = Invoke-WfProbe
    $timer.Stop(); $componentTimes.probeWork = $timer.Elapsed.TotalSeconds
}
$modulesAfterProbe = @(Get-Module | ForEach-Object { [ordered]@{name=$_.Name;version=$_.Version.ToString()} })
$timer.Restart(); $firstText = ConvertTo-WfDisplayJson $payload
$timer.Stop(); $componentTimes.formatFirst = $timer.Elapsed.TotalSeconds
$repeatedTexts = [Collections.Generic.List[string]]::new()
for ($index=1; $index -le 3; $index++) {
    $timer.Restart(); $nextText = ConvertTo-WfDisplayJson $payload
    $timer.Stop(); $componentTimes["formatRepeat$index"] = $timer.Elapsed.TotalSeconds
    $repeatedTexts.Add($nextText)
    if ($nextText -cne $firstText) { throw 'Formatter output changed across calls.' }
}
$modulesAfterFormatting = @(Get-Module | ForEach-Object { [ordered]@{name=$_.Name;version=$_.Version.ToString()} })
$outputBytes = [Text.UTF8Encoding]::new($false,$true).GetBytes($firstText)
$temporaryPath = [IO.Path]::Combine([IO.Path]::GetTempPath(),'wayfinder-component-'+[Guid]::NewGuid().ToString('N'))
$ownsTemporary = $false
try {
    $timer.Restart()
    $stream = [IO.FileStream]::new($temporaryPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    $ownsTemporary = $true
    try { $stream.Write($outputBytes); $stream.Flush() } finally { $stream.Dispose() }
    $timer.Stop(); $componentTimes.privateFileWrite = $timer.Elapsed.TotalSeconds
    $readBack = [IO.File]::ReadAllBytes($temporaryPath)
    $byteEquality = [Convert]::ToBase64String($readBack) -ceq [Convert]::ToBase64String($outputBytes)
    if (-not $byteEquality) { throw 'Private output byte comparison failed.' }
} finally { if ($ownsTemporary) { [IO.File]::Delete($temporaryPath) } }
if ([Convert]::ToBase64String([IO.File]::ReadAllBytes($AdapterPath)) -cne [Convert]::ToBase64String($adapterBytes)) { throw 'Adapter bytes changed.' }
$report = [ordered]@{format='wayfinder-powershell-probe-prototype-observation';schemaVersion=1;scenario=$Scenario;variant=$Variant;diagnosticCounterfactual=($Variant -ne 'original');prefixSha256=$prefixDigest;contractRoot=$script:ContractRoot;modulesAfterProbe=$modulesAfterProbe;modulesAfterFormatting=$modulesAfterFormatting;adapterSha256=$sourceDigest;adapterPath=$AdapterPath;skillRoot=$script:SkillRoot;prefixLength=$prefixSource.Length;sourceLength=$adapterSource.Length;runtimeVersion=$PSVersionTable.PSVersion.ToString();times=$componentTimes;modulesBefore=$modulesBefore;modulesBeforeLoad=$modulesBeforeLoad;modulesAfter=$modulesAfter;payload=$payload;formattedText=$firstText;repeatedTexts=$repeatedTexts;outputByteEquality=$byteEquality}
# Reporting is deliberately outside every measured component interval.
[Console]::Out.WriteLine((ConvertTo-Json -InputObject $report -Depth 50 -Compress))
