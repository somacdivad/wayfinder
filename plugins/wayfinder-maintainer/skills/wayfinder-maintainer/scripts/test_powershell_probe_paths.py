import base64
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[5]
spec = importlib.util.spec_from_file_location('probe_paths', ROOT/'scripts/measure_powershell_probe_paths.py')
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)

class ProbePathTests(unittest.TestCase):
    def control_fixture(self):
        digest=hashlib.sha256(d.ADAPTER.read_bytes()).hexdigest()
        contract=json.loads((d.SKILL/'assets/contract-v1/contract.json').read_text())
        return dict(format='wayfinder-powershell-probe-compatibility',schemaVersion=1,complete=True,
                    adapterSha256=digest,adapterPath=str(d.ADAPTER),skillRoot=str(d.SKILL),runtimeVersion='7.6.6',
                    fixtures=[{'name':'empty','rows':[]},{'name':'nested-hidden-literal-unicode-links-cycle','rows':['visible.txt|file']},{'name':'missing-root','failureEquality':True}],
                    recursiveScopes=[{'path':x['path'],'rows':[]} for x in contract['governedScopes'] if x['recursive']],permissionStatus='unavailable')

    def fixture(self, scenario='minimal', variant='original'):
        source=d.ADAPTER.read_text();digest=hashlib.sha256(d.ADAPTER.read_bytes()).hexdigest();prefix=d.prototype_prefix(source,variant)
        payload={'format':'wayfinder-command-result','schemaVersion':1,'ok':True,'command':'probe','code':'ok','data':{},'diagnostics':[]}
        if scenario=='probe':payload['data']={'adapter':{'id':'powershell-v1','path':'scripts/adapters/wayfinder-powershell.ps1','sha256':digest},'environment':{'version':'7.6.6'}}
        text=json.dumps(payload);after=[] if variant!='original' else d.MANAGEMENT;work=[] if variant=='full' else d.MANAGEMENT
        labels=d._base.TIMERS-({'probeWork'} if scenario=='minimal' else set())
        if variant!='original':labels|={'startupTransformation'}
        report=dict(format='wayfinder-powershell-probe-prototype-observation',schemaVersion=1,scenario=scenario,variant=variant,diagnosticCounterfactual=variant!='original',prefixSha256=hashlib.sha256(prefix.encode()).hexdigest(),contractRoot=str(d.SKILL/'assets/contract-v1'),adapterSha256=digest,adapterPath=str(d.ADAPTER),skillRoot=str(d.SKILL),runtimeVersion='7.6.6',prefixLength=len(prefix.encode('utf-16-le'))//2,sourceLength=len(source.encode('utf-16-le'))//2,times={k:0.01 for k in labels},modulesBefore=[],modulesBeforeLoad=[],modulesAfter=copy.deepcopy(after),modulesAfterProbe=copy.deepcopy(work),modulesAfterFormatting=copy.deepcopy(work),payload=payload,formattedText=text,repeatedTexts=[text]*3,outputByteEquality=True)
        return report,digest,source

    def cohorts(self):
        entries=[]
        for name,scenario,variant in d.SCENARIOS:
            values=[]
            for number in range(9):
                report,digest,source=self.fixture('minimal' if scenario=='empty-process' else scenario,variant)
                order=d.SCENARIOS if number==0 or number%2 else tuple(reversed(d.SCENARIOS))
                values.append(dict(wallSeconds=0.2,childUserSeconds=0.1,childSystemSeconds=0.01,exit=0,components=None if scenario=='empty-process' else report,round=number,order=[x[0] for x in order].index(name)))
            entries.append(dict(scenario=name,firstObservation=values[0],samples=values[1:]))
        return entries,digest,source

    def test_transform_is_exact_and_requires_unique_source(self):
        source=d.ADAPTER.read_text();before=d.ADAPTER.read_bytes();prefix=d.prototype_prefix(source,'full')
        self.assertNotIn(d.ASSIGNMENTS[0][0],prefix);self.assertIn(d.ASSIGNMENTS[1][1],prefix)
        self.assertEqual(d.ADAPTER.read_bytes(),before)
        for changed in (source.replace(d.ASSIGNMENTS[0][0],''),source.replace(d.ASSIGNMENTS[0][0],d.ASSIGNMENTS[0][0]+'\n'+d.ASSIGNMENTS[0][0]),source+'unexpected\n'):
            with self.assertRaises(ValueError):d.prototype_prefix(changed,'full')

    def test_variant_module_transitions_and_provenance(self):
        for scenario in ('probe',):
            for variant in ('original','startup','paths','full'):
                report,digest,source=self.fixture(scenario,variant);d.validate_observation(report,scenario,digest,source,variant)
                for key,value in (('prefixSha256','wrong'),('diagnosticCounterfactual',None),('contractRoot','wrong'),('modulesBefore',d.MANAGEMENT),('modulesAfterProbe',None),('modulesAfterFormatting',None),('prefixLength',0)):
                    bad=copy.deepcopy(report);bad[key]=value
                    with self.assertRaises(ValueError):d.validate_observation(bad,scenario,digest,source,variant)
                bad=copy.deepcopy(report);bad['modulesAfter']=d.MANAGEMENT if variant!='original' else []
                with self.assertRaises(ValueError):d.validate_observation(bad,scenario,digest,source,variant)

    def test_timer_shape_and_output_equality(self):
        report,digest,source=self.fixture(variant='full')
        for value in (True,-1,float('nan'),float('inf'),'1'):
            bad=copy.deepcopy(report);bad['times']['startupTransformation']=value
            with self.assertRaises(ValueError):d.validate_observation(bad,'minimal',digest,source,'full')
        bad=copy.deepcopy(report);bad['times']['probeWork']=0
        with self.assertRaises(ValueError):d.validate_observation(bad,'minimal',digest,source,'full')
        report['repeatedTexts'][0]='different'
        with self.assertRaises(ValueError):d.validate_observation(report,'minimal',digest,source,'full')

    def test_exact_rounds_and_paired_results(self):
        entries,digest,source=self.cohorts();d.validate_cohorts(entries,digest,source)
        for key,value in (('round',0),('order',0),('wallSeconds',float('nan')),('exit',1)):
            bad=copy.deepcopy(entries);bad[1]['samples'][1][key]=value
            with self.assertRaises(ValueError):d.validate_cohorts(bad,digest,source)
        with self.assertRaises(ValueError):d.validate_cohorts(entries[:-1],digest,source)
        bad=entries[4]['samples'][0]['components'];bad['payload']['data']['extra']='different';bad['formattedText']=json.dumps(bad['payload']);bad['repeatedTexts']=[bad['formattedText']]*3
        with self.assertRaisesRegex(ValueError,'disagreement'):d.validate_cohorts(entries,digest,source)

    def test_timeout_crash_and_incomplete_or_existing_output(self):
        for error in (subprocess.TimeoutExpired('pwsh',15),ValueError('worker failed')):
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'report.json'
                with mock.patch.object(sys,'argv',['diagnostics','--output',str(path)]),mock.patch.object(d.platform,'system',return_value='Linux'),mock.patch.object(d,'resource',object()),mock.patch.object(d,'compatibility_preflight',return_value=self.control_fixture()),mock.patch.object(d,'measure_one',side_effect=error),mock.patch.object(sys,'stdout',io.StringIO()):
                    with self.assertRaises(type(error)):d.main()
                self.assertEqual(json.loads(path.read_text()),{'complete':False})
                with mock.patch.object(sys,'argv',['diagnostics','--output',str(path)]),mock.patch.object(d.platform,'system',return_value='Linux'),mock.patch.object(d,'resource',object()),mock.patch.object(d,'compatibility_preflight',return_value=self.control_fixture()),mock.patch.object(d,'measure_one') as run:
                    with self.assertRaises(FileExistsError):d.main()
                    run.assert_not_called()
        with mock.patch.object(d.subprocess,'run',return_value=subprocess.CompletedProcess('pwsh',1,b'',b'crash')):
            with self.assertRaises(ValueError):d.measure_one(['pwsh'],'empty-process','','')

    def test_driver_runs_45_serial_calls_and_reports_pairs(self):
        entries,_,_=self.cohorts();prototypes={e['scenario']:e['firstObservation'] for e in entries};calls=[]
        def measure(command,scenario,digest,source,variant):
            name=next(n for n,s,v in d.SCENARIOS if s==scenario and v==variant);calls.append(name)
            if scenario!='empty-process':self.assertEqual(command[command.index('-Variant')+1],variant)
            value=copy.deepcopy(prototypes[name]);value.pop('round');value.pop('order');return value
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'report.json'
            with mock.patch.object(sys,'argv',['diagnostics','--output',str(path)]),mock.patch.object(d.platform,'system',return_value='Linux'),mock.patch.object(d,'resource',object()),mock.patch.object(d,'compatibility_preflight',return_value=self.control_fixture()),mock.patch.object(d,'measure_one',side_effect=measure),mock.patch.object(sys,'stdout',io.StringIO()):self.assertEqual(d.main(),0)
            result=json.loads(path.read_text());self.assertTrue(result['complete']);self.assertEqual(len(calls),45);self.assertEqual(calls[10:15],[n for n,_,_ in reversed(d.SCENARIOS)]);self.assertEqual(len(result['pairedDifferences']),3)

    @unittest.skipUnless(shutil.which(os.environ.get('WAYFINDER_POWERSHELL_RUNTIME','pwsh')),'PowerShell unavailable; actual probe transform AST guard not run')
    def test_actual_transform_guard_rejects_nested_missing_and_duplicate_assignments(self):
        guard=d.WRAPPER.read_text().split('# TRANSFORM-GUARD:BEGIN\n')[1].split('# TRANSFORM-GUARD:END')[0]
        assignments='\n'.join(a for a,_ in d.ASSIGNMENTS);sources=[assignments,assignments.replace(d.ASSIGNMENTS[0][0],''),assignments+'\n'+d.ASSIGNMENTS[0][0],'function Nested {\n'+assignments+'\n}']
        encoded=base64.b64encode(json.dumps(sources).encode()).decode()
        command="Set-StrictMode -Version 3.0; $ErrorActionPreference='Stop'; $sources=ConvertFrom-Json ([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('"+encoded+"'))); $i=0; foreach($adapterSource in $sources) { $t=$null;$e=$null;$fullAst=[System.Management.Automation.Language.Parser]::ParseInput($adapterSource,'original.ps1',[ref]$t,[ref]$e);$accepted=$true;try {\n"+guard+"\n} catch {$accepted=$false};if($accepted -ne ($i-eq0)){throw 'Wrong transform acceptance'};$i++ };if($i-ne4){throw 'Missing fixtures'}"
        result=subprocess.run([os.environ.get('WAYFINDER_POWERSHELL_RUNTIME','pwsh'),'-NoLogo','-NoProfile','-NonInteractive','-Command',command],capture_output=True,timeout=15);self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'));self.assertEqual(result.stdout,b'')

    def test_compatibility_report_rejects_incomplete_scope_and_fixture_coverage(self):
        report=self.control_fixture();digest=hashlib.sha256(d.ADAPTER.read_bytes()).hexdigest();d.validate_compatibility(report,digest)
        for key,value in (('complete',False),('recursiveScopes',[]),('fixtures',[]),('permissionStatus','passed-without-check'),('adapterSha256','wrong')):
            bad=copy.deepcopy(report);bad[key]=value
            with self.assertRaises(ValueError):d.validate_compatibility(bad,digest)
        bad=copy.deepcopy(report);bad['recursiveScopes'][0]['rows']=['z|file','a|file']
        with self.assertRaises(ValueError):d.validate_compatibility(bad,digest)
        with mock.patch.object(d.subprocess,'run',return_value=subprocess.CompletedProcess('pwsh',1,b'',b'enumeration mismatch')):
            with self.assertRaises(ValueError):d.compatibility_preflight(['pwsh'],digest)

    def test_standalone_import_does_not_write_bytecode_without_canonical_controls(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder);(target/'scripts').mkdir()
            for name in ('measure_powershell_probe_paths.py','measure_powershell_startup_paths.py','measure_powershell_components.py'):
                shutil.copyfile(ROOT/'scripts'/name,target/'scripts'/name)
            env=dict(os.environ);env.pop('PYTHONDONTWRITEBYTECODE',None)
            code="import runpy; runpy.run_path("+repr(str(target/'scripts/measure_powershell_probe_paths.py'))+",run_name='diagnostic_import'); runpy.run_path("+repr(str(target/'scripts/measure_powershell_startup_paths.py'))+",run_name='diagnostic_import')"
            result=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
            self.assertEqual(list(target.rglob('*.pyc')),[]);self.assertEqual(list(target.rglob('__pycache__')),[])

    def test_probe_replacements_are_bounded_and_unique(self):
        source=d.ADAPTER.read_text();full=d.prototype_prefix(source,'full');paths=d.prototype_prefix(source,'paths')
        self.assertIn('Get-DiagnosticProbeFiles $path',full);self.assertIn('Get-ChildItem -LiteralPath $path -Recurse -File',paths)
        for original,_ in d.PROBE_REPLACEMENTS:
            start=source.index('function Invoke-WfProbe {');end=source.index('\nfunction Parse-WfOptions',start)
            changed=source[:start]+source[start:end].replace(original,'unexpected')+source[end:]
            with self.assertRaises(ValueError):d.prototype_prefix(changed,'full')

    @unittest.skipUnless(shutil.which(os.environ.get('WAYFINDER_POWERSHELL_RUNTIME','pwsh')),'PowerShell unavailable; actual probe command extent guard not run')
    def test_actual_probe_guard_rejects_nested_duplicate_and_changed_commands(self):
        guard=d.WRAPPER.read_text().split('# PROBE-TRANSFORM-GUARD:BEGIN\n')[1].split('# PROBE-TRANSFORM-GUARD:END')[0]
        source=d.ADAPTER.read_text();start=source.index('function Invoke-WfProbe {');end=source.index('\nfunction Parse-WfOptions',start);probe=source[start:end]
        sources=[source,source.replace(d.PROBE_REPLACEMENTS[0][0],d.PROBE_REPLACEMENTS[0][0]+' -Resolve'),source[:start]+probe.replace('    $releasePath=',"    function Nested { "+d.PROBE_REPLACEMENTS[0][0]+" }; $releasePath=")+source[end:],source[:start]+probe.replace(d.PROBE_REPLACEMENTS[0][0],'unexpected')+source[end:]]
        encoded=base64.b64encode(json.dumps(sources).encode()).decode()
        command="Set-StrictMode -Version 3.0;$ErrorActionPreference='Stop';$sources=ConvertFrom-Json ([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('"+encoded+"')));$i=0;foreach($adapterSource in $sources){$t=$null;$e=$null;$fullAst=[System.Management.Automation.Language.Parser]::ParseInput($adapterSource,'original.ps1',[ref]$t,[ref]$e);$accepted=$true;try {\n"+guard+"\n}catch{$accepted=$false};if($accepted-ne($i-eq0)){throw 'Wrong probe guard acceptance'};$i++};if($i-ne4){throw 'Missing fixtures'}"
        result=subprocess.run([os.environ.get('WAYFINDER_POWERSHELL_RUNTIME','pwsh'),'-NoLogo','-NoProfile','-NonInteractive','-Command',command],capture_output=True,timeout=15);self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
