import base64
import os
import shutil
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[5]
SPEC = importlib.util.spec_from_file_location('component_diagnostics', ROOT/'scripts/measure_powershell_components.py')
d = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(d)

class ComponentDiagnosticTests(unittest.TestCase):
    def fixture(self):
        source = d.ADAPTER.read_text(); digest = hashlib.sha256(d.ADAPTER.read_bytes()).hexdigest()
        payload = {'format':'wayfinder-command-result','schemaVersion':1,'ok':True,'command':'probe','code':'ok','data':{},'diagnostics':[]}
        text = json.dumps(payload)
        report = dict(format='wayfinder-powershell-component-observation',schemaVersion=1,scenario='minimal',adapterSha256=digest,
                      adapterPath=str(d.ADAPTER),skillRoot=str(d.SKILL),prefixLength=d.expected_prefix(source),
                      sourceLength=len(source.encode('utf-16-le'))//2,runtimeVersion='7.6.6',times={k:0.0 for k in d.TIMERS},
                      modulesBefore=[],modulesAfter=[],payload=payload,formattedText=text,repeatedTexts=[text]*3,outputByteEquality=True)
        return report,digest,source

    def test_boundary_rejects_changed_dispatch_and_trailing_execution(self):
        source = d.ADAPTER.read_text()
        self.assertGreater(d.expected_prefix(source),0)
        for changed in (source+'Write-Output unexpected\n',source.replace('Invoke-WfMain $args','Invoke-WfMain probe'),source.replace('exit $script:ExitCode','exit 0')):
            with self.assertRaises(ValueError): d.expected_prefix(changed)
        unicode_source='😀\nInvoke-WfMain $args\nexit $script:ExitCode\n'
        self.assertEqual(d.expected_prefix(unicode_source),3)

    def test_report_validates_binding_and_exact_shape(self):
        report,digest,source=self.fixture(); d.validate_observation(report,'minimal',digest,source)
        for key,value in (('skillRoot','wrong'),('prefixLength',0),('adapterSha256','wrong'),('outputByteEquality',False),('extra',1)):
            bad=copy.deepcopy(report);bad[key]=value
            with self.assertRaises(ValueError): d.validate_observation(bad,'minimal',digest,source)

    def test_invalid_times_and_changed_formatter_output_fail(self):
        report,digest,source=self.fixture()
        for value in (-1,float('nan'),float('inf'),True,'1'):
            bad=copy.deepcopy(report);bad['times']['formatFirst']=value
            with self.assertRaises(ValueError): d.validate_observation(bad,'minimal',digest,source)
        for changed in ('repeatedTexts','formattedText'):
            bad=copy.deepcopy(report);bad[changed]=['different']*3 if changed=='repeatedTexts' else '{}'
            with self.assertRaises(ValueError): d.validate_observation(bad,'minimal',digest,source)
        bad=copy.deepcopy(report);bad['times']['unknown']=0
        with self.assertRaises(ValueError): d.validate_observation(bad,'minimal',digest,source)

    def test_probe_payload_identity_is_checked(self):
        report,digest,source=self.fixture();report['scenario']='probe'
        report['payload']['data']={'adapter':{'id':'powershell-v1','path':'scripts/adapters/wayfinder-powershell.ps1','sha256':digest},'environment':{'version':'7.6.6'}}
        report['formattedText']=json.dumps(report['payload']);report['repeatedTexts']=[report['formattedText']]*3
        d.validate_observation(report,'probe',digest,source)
        report['payload']['data']['adapter']['sha256']='wrong'
        with self.assertRaises(ValueError):d.validate_observation(report,'probe',digest,source)

    def test_subprocess_timeout_and_failure_are_not_success(self):
        with mock.patch.object(d.subprocess,'run',side_effect=subprocess.TimeoutExpired('pwsh',15)) as run:
            with self.assertRaises(subprocess.TimeoutExpired):d.measure_one(['pwsh'],'empty-process','', '')
            self.assertEqual(run.call_args.kwargs['timeout'],15)
        with mock.patch.object(d.subprocess,'run',return_value=subprocess.CompletedProcess(['pwsh'],1,b'',b'failure')):
            with self.assertRaisesRegex(ValueError,'failure'):d.measure_one(['pwsh'],'empty-process','','')

    def test_existing_output_refused_before_child_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'report.json';path.write_text('original\n')
            with mock.patch.object(sys,'argv',['diagnostics','--output',str(path)]),mock.patch.object(d.platform,'system',return_value='Linux'),mock.patch.object(d,'resource',object()),mock.patch.object(d,'measure_one') as measure:
                with self.assertRaises(FileExistsError): d.main()
                measure.assert_not_called()
            self.assertEqual(path.read_text(),'original\n')

    def test_failed_measurement_leaves_incomplete_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'report.json'
            with mock.patch.object(sys,'argv',['diagnostics','--output',str(path)]),mock.patch.object(d.platform,'system',return_value='Linux'),mock.patch.object(d,'resource',object()),mock.patch.object(d,'measure_one',side_effect=ValueError('failed')):
                with self.assertRaises(ValueError):d.main()
            self.assertEqual(json.loads(path.read_text()),{'complete':False})

    @unittest.skipUnless(shutil.which(os.environ.get('WAYFINDER_POWERSHELL_RUNTIME','pwsh')), 'PowerShell unavailable; actual AST prefix guard not run')
    def test_actual_powershell_ast_guard_rejects_unexpected_source_shapes(self):
        wrapper=d.WRAPPER.read_text();guard=wrapper.split('# PREFIX-GUARD:BEGIN\n',1)[1].split('# PREFIX-GUARD:END',1)[0]
        suffix='Invoke-WfMain $args\nexit $script:ExitCode\n'
        sources=['$x=1\n'+suffix,'param($x)\n'+suffix,'begin { $x=1 }\n'+suffix,'using namespace System\n'+suffix,'$x=1\n'+suffix+'Write-Output unexpected\n',suffix.replace('exit $script:ExitCode','exit 0')]
        encoded=base64.b64encode(json.dumps(sources).encode()).decode()
        command=guard+"\n$ErrorActionPreference='Stop'; $sources=ConvertFrom-Json ([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('"+encoded+"'))); $i=0; foreach($source in $sources) { $t=$null; $e=$null; $ast=[System.Management.Automation.Language.Parser]::ParseInput($source,'original.ps1',[ref]$t,[ref]$e); $accepted=$true; try { [void](Get-DiagnosticPrefixLength $ast $source) } catch { $accepted=$false }; if ($accepted -ne ($i -eq 0)) { throw 'Unexpected prefix acceptance' }; $i++ }; if ($i -ne 6) { throw 'Missing fixtures' }"
        result=subprocess.run([os.environ.get('WAYFINDER_POWERSHELL_RUNTIME','pwsh'),'-NoLogo','-NoProfile','-NonInteractive','-Command',command],capture_output=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
        self.assertEqual(result.stdout,b'')
