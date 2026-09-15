# Independent diagnostics only; the registered adapter is never rewritten.
param([Parameter(Mandatory)][string]$AdapterPath,
      [Parameter(Mandatory)][ValidateSet('minimal','probe')][string]$Scenario)
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
$componentTimes = [ordered]@{}
$modulesBefore = @(Get-Module | ForEach-Object { [ordered]@{name=$_.Name;version=$_.Version.ToString()} })
$timer = [Diagnostics.Stopwatch]::StartNew()
$adapterBytes = [IO.File]::ReadAllBytes($AdapterPath)
$adapterSource = [Text.UTF8Encoding]::new($false,$true).GetString($adapterBytes)
$timer.Stop(); $componentTimes.sourceReadDecode = $timer.Elapsed.TotalSeconds
$sourceDigest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($adapterBytes)).ToLowerInvariant()
$tokens = $null; $parseErrors = $null
$timer.Restart()
$fullAst = [System.Management.Automation.Language.Parser]::ParseInput($adapterSource,$AdapterPath,[ref]$tokens,[ref]$parseErrors)
$timer.Stop(); $componentTimes.fullSourceParse = $timer.Elapsed.TotalSeconds
if ($parseErrors.Count -ne 0) { throw 'Adapter did not parse.' }
$prefixLength = Get-DiagnosticPrefixLength $fullAst $adapterSource
$prefixSource = $adapterSource.Substring(0,$prefixLength)
$timer.Restart()
$prefixAst = [System.Management.Automation.Language.Parser]::ParseInput($prefixSource,$AdapterPath,[ref]$tokens,[ref]$parseErrors)
$timer.Stop(); $componentTimes.diagnosticPrefixParse = $timer.Elapsed.TotalSeconds
if ($parseErrors.Count -ne 0) { throw 'Diagnostic prefix did not parse.' }
$timer.Restart()
$initializationBlock = $prefixAst.GetScriptBlock()
$timer.Stop(); $componentTimes.scriptBlockCreation = $timer.Elapsed.TotalSeconds
if ($initializationBlock.File -cne $AdapterPath) { throw 'Diagnostic source path metadata differs.' }
$timer.Restart()
. $initializationBlock
$timer.Stop(); $componentTimes.loadInitialization = $timer.Elapsed.TotalSeconds
$expectedSkillRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($AdapterPath)))
if ($script:SkillRoot -cne $expectedSkillRoot -or $script:AdapterId -cne 'powershell-v1') { throw 'Diagnostic original skill root/identity differs.' }
$modulesAfter = @(Get-Module | ForEach-Object { [ordered]@{name=$_.Name;version=$_.Version.ToString()} })
$payload = [ordered]@{format='wayfinder-command-result';schemaVersion=1;ok=$true;command='probe';code='ok';data=[ordered]@{};diagnostics=[Collections.ArrayList]@()}
$componentTimes.probeWork = 0.0
if ($Scenario -eq 'probe') {
    $timer.Restart(); $payload.data = Invoke-WfProbe
    $timer.Stop(); $componentTimes.probeWork = $timer.Elapsed.TotalSeconds
}
$timer.Restart(); $firstText = ConvertTo-WfDisplayJson $payload
$timer.Stop(); $componentTimes.formatFirst = $timer.Elapsed.TotalSeconds
$repeatedTexts = [Collections.Generic.List[string]]::new()
for ($index=1; $index -le 3; $index++) {
    $timer.Restart(); $nextText = ConvertTo-WfDisplayJson $payload
    $timer.Stop(); $componentTimes["formatRepeat$index"] = $timer.Elapsed.TotalSeconds
    $repeatedTexts.Add($nextText)
    if ($nextText -cne $firstText) { throw 'Formatter output changed across calls.' }
}
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
$report = [ordered]@{format='wayfinder-powershell-component-observation';schemaVersion=1;scenario=$Scenario;adapterSha256=$sourceDigest;adapterPath=$AdapterPath;skillRoot=$script:SkillRoot;prefixLength=$prefixLength;sourceLength=$adapterSource.Length;runtimeVersion=$PSVersionTable.PSVersion.ToString();times=$componentTimes;modulesBefore=$modulesBefore;modulesAfter=$modulesAfter;payload=$payload;formattedText=$firstText;repeatedTexts=$repeatedTexts;outputByteEquality=$byteEquality}
# Reporting is deliberately outside every measured component interval.
[Console]::Out.WriteLine((ConvertTo-Json -InputObject $report -Depth 50 -Compress))
