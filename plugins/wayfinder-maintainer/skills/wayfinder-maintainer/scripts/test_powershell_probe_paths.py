import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[5]
ADAPTER = ROOT / 'plugins/wayfinder/skills/wayfinder/scripts/adapters/wayfinder-powershell.ps1'


class PowerShellProbePathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ADAPTER.read_text(encoding='utf-8')
        start = cls.source.index('function Invoke-WfProbe {')
        end = cls.source.index('\nfunction Parse-WfOptions', start)
        cls.probe = cls.source[start:end]
        helper_start = cls.source.index('function Get-WfProbeFiles {')
        helper_end = cls.source.index('\nfunction Invoke-WfProbe', helper_start)
        cls.helper = cls.source[helper_start:helper_end]

    def test_startup_paths_use_dotnet_without_management_commands(self):
        self.assertIn("$script:SkillRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($PSScriptRoot))", self.source)
        self.assertIn("$script:ContractRoot = [IO.Path]::Combine($script:SkillRoot,'assets/contract-v1')", self.source)
        self.assertNotIn('$script:SkillRoot = Split-Path', self.source)
        self.assertNotIn("$script:ContractRoot = Join-Path", self.source)

    def test_probe_uses_exact_dotnet_path_substitutions(self):
        expected = (
            "[IO.Path]::Combine($script:ContractRoot,'release.json')",
            '[IO.Path]::Combine($script:SkillRoot,$release.contractManifest.path)',
            "[IO.Path]::Combine($script:ContractRoot,'schemas/release.schema.json')",
            '[IO.Path]::Combine($script:SkillRoot,$adapter.path)',
            '[IO.Path]::Combine($script:SkillRoot,$resource.path)',
            '[IO.Path]::Combine($script:SkillRoot,$scope.path)',
            "[IO.Path]::Combine($script:ContractRoot,'known-answer.json')",
        )
        self.assertNotIn('Join-Path', self.probe)
        self.assertNotIn('Get-ChildItem', self.probe)
        for expression in expected:
            self.assertEqual(self.probe.count(expression), 1, expression)

    def test_probe_enumerator_preserves_governed_scope_boundary(self):
        self.assertEqual(self.probe.count('Get-WfProbeFiles $path'), 1)
        for expression in (
            '$options.RecurseSubdirectories = $false',
            '$options.IgnoreInaccessible = $false',
            '$options.AttributesToSkip = [IO.FileAttributes]0',
            "[IO.FileAttributes]::Hidden -bor [IO.FileAttributes]::System",
            '[IO.FileAttributes]::Directory',
            '[IO.FileAttributes]::ReparsePoint',
            '$null -eq $entry.LinkTarget',
            '[IO.DirectoryInfo]::new($LiteralPath)',
            "EnumerateFileSystemInfos('*',$options)",
        ):
            self.assertIn(expression, self.helper)
        self.assertNotIn('Get-ChildItem', self.helper)
        self.assertNotIn('Get-DiagnosticProbeFiles', self.source)

    def test_runtime_adapter_contains_no_counterfactual_instrumentation(self):
        for marker in ('TRANSFORM-GUARD:', 'PROBE-TRANSFORM-GUARD:', 'DIAGNOSTIC'):
            self.assertNotIn(marker, self.source)


if __name__ == '__main__':
    unittest.main()
