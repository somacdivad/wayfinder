#!/usr/bin/env python3
"""Deterministic regression tests for candidate revision 9 and 10 Windows corrections."""

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MAINTAINER_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = MAINTAINER_ROOT.parents[2] / "wayfinder" / "skills" / "wayfinder"
ADAPTER_PATH = RUNTIME_ROOT / "scripts/adapters/wayfinder.py"
RUNNER_PATH = MAINTAINER_ROOT / "scripts/conformance/v1/run.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sys.dont_write_bytecode = True
adapter = load_module("wayfinder_revision_10_adapter", ADAPTER_PATH)
sys.path.insert(0, str(RUNNER_PATH.parent))
try:
    runner = load_module("wayfinder_revision_10_runner", RUNNER_PATH)
finally:
    sys.path.pop(0)


class FakeCall:
    def __init__(self, result, side_effect=None):
        self.result = result
        self.side_effect = side_effect
        self.calls = []
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        self.calls.append(args)
        if self.side_effect is not None:
            self.side_effect(*args)
        return self.result


class FakeKernel32:
    def __init__(self, *, handle=1234, wait=0x00000102):
        self.OpenProcess = FakeCall(handle)
        self.WaitForSingleObject = FakeCall(wait)
        self.CloseHandle = FakeCall(1)


class WindowsProcessProbeTests(unittest.TestCase):
    def test_pid_bounds_prevent_dword_truncation(self) -> None:
        kernel = FakeKernel32()
        for pid in (0, -1, 0x1_0000_0000):
            self.assertFalse(adapter._windows_process_alive(pid, kernel32=kernel, get_last_error=lambda: 0))
        self.assertEqual(kernel.OpenProcess.calls, [])

    def test_exact_types_and_wait_results(self) -> None:
        for wait, expected in ((0x102, True), (0, False), (0xFFFFFFFF, True), (17, True)):
            with self.subTest(wait=wait):
                kernel = FakeKernel32(wait=wait)
                self.assertEqual(adapter._windows_process_alive(0xFFFFFFFF, kernel32=kernel, get_last_error=lambda: 0), expected)
                self.assertEqual(kernel.OpenProcess.calls, [(0x00100000, False, 0xFFFFFFFF)])
                self.assertEqual(kernel.CloseHandle.calls, [(1234,)])
                self.assertEqual(ctypes.sizeof(kernel.OpenProcess.argtypes[0]), 4)
                self.assertEqual(ctypes.sizeof(kernel.OpenProcess.argtypes[2]), 4)
                self.assertEqual(ctypes.sizeof(kernel.OpenProcess.restype), ctypes.sizeof(ctypes.c_void_p))
                self.assertEqual(ctypes.sizeof(kernel.CloseHandle.restype), 4)

    def test_open_failures_are_fail_closed_except_invalid_parameter(self) -> None:
        for error, expected in ((87, False), (5, True), (12345, True)):
            with self.subTest(error=error):
                kernel = FakeKernel32(handle=0)
                self.assertEqual(adapter._windows_process_alive(41, kernel32=kernel, get_last_error=lambda: error), expected)
                self.assertEqual(kernel.WaitForSingleObject.calls, [])
                self.assertEqual(kernel.CloseHandle.calls, [])

    def test_posix_live_terminated_and_nonexistent_processes(self) -> None:
        if os.name == "nt":
            self.skipTest("POSIX branch")
        self.assertTrue(adapter._process_alive(os.getpid()))
        child = subprocess.Popen([sys.executable, "-c", "pass"])
        child.wait()
        self.assertFalse(adapter._process_alive(child.pid))
        self.assertFalse(adapter._process_alive(0))
        self.assertFalse(adapter._process_alive(-1))


class RecoveryPrecedenceTests(unittest.TestCase):
    def _lock(self, workspace: Path, *, operation: str, plan: str, host: str, pid: int = 1) -> None:
        control = workspace / ".wayfinder"
        control.mkdir(exist_ok=True)
        value = {
            "format": adapter.LOCK_FORMAT,
            "schemaVersion": 1,
            "operationId": operation,
            "planSha256": plan,
            "owner": {"host": host, "pid": pid, "token": "token"},
        }
        (control / "initialize.lock").write_text(adapter.canonical_json(value), encoding="utf-8")

    def test_acquire_checks_action_operation_plan_and_host_before_process(self) -> None:
        cases = (
            (False, "op", "a" * 64, socket.gethostname()),
            (True, "other", "a" * 64, socket.gethostname()),
            (True, "op", "b" * 64, socket.gethostname()),
            (True, "op", "a" * 64, "foreign-host"),
        )
        for recovery, stored_operation, stored_plan, stored_host in cases:
            with self.subTest(recovery=recovery, operation=stored_operation, plan=stored_plan, host=stored_host):
                with tempfile.TemporaryDirectory() as raw:
                    workspace = Path(raw)
                    self._lock(workspace, operation=stored_operation, plan=stored_plan, host=stored_host)
                    with mock.patch.object(adapter, "_process_alive", side_effect=AssertionError("process probe ran early")):
                        with self.assertRaises(adapter.WFError) as raised:
                            adapter._acquire_initialize_lock(workspace, "op", "a" * 64, recovery=recovery)
                    self.assertEqual(raised.exception.code, "lock.contention")

    def test_lock_only_recovery_checks_operation_and_host_before_process(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw)
            self._lock(workspace, operation="other", plan="a" * 64, host=socket.gethostname())
            with mock.patch.object(adapter, "_process_alive", side_effect=AssertionError("process probe ran early")):
                with self.assertRaises(adapter.WFError) as raised:
                    adapter.command_initialize_recover(str(workspace), "op", "rollback")
            self.assertEqual(raised.exception.code, "lock.contention")
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw)
            self._lock(workspace, operation="op", plan="a" * 64, host="foreign-host")
            with mock.patch.object(adapter, "_process_alive", side_effect=AssertionError("process probe ran for foreign host")):
                state = adapter.command_initialize_recover(str(workspace), "op", "inspect")
            self.assertEqual(state["allowedActions"], ["inspect"])


class SpecialFileTests(unittest.TestCase):
    class FakeWinsock:
        def __init__(self, path: Path, *, bind_result=0, create_path=True, error=10047):
            def bind_side_effect(_handle, address, length):
                native = ctypes.cast(address, ctypes.POINTER(runner._SockaddrUn)).contents
                self.bound_family = native.sun_family
                self.bound_path = bytes(native.sun_path).split(b"\0", 1)[0]
                self.bound_length = length
                if bind_result == 0 and create_path:
                    path.touch()

            self.bound_family = None
            self.bound_path = None
            self.bound_length = None
            self.WSAStartup = FakeCall(0)
            self.WSACleanup = FakeCall(0)
            self.WSAGetLastError = FakeCall(error)
            self.socket = FakeCall(1234)
            self.bind = FakeCall(bind_result, bind_side_effect)
            self.closesocket = FakeCall(0)

    def test_local_socket_or_fifo_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "special"
            fixture = runner.create_special_file_fixture(path, windows=False)
            try:
                self.assertTrue(stat.S_ISFIFO(os.lstat(path).st_mode))
                self.assertEqual(adapter._relative_kind(path), "unsupported-file")
            finally:
                runner.cleanup_special_file_fixture(path, fixture)
            self.assertFalse(path.exists())

    def test_mocked_windows_native_ownership_lifetime_and_exact_cleanup(self) -> None:
        """Maintainer logic verification only; this is not real Windows conformance."""
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "special"
            native = self.FakeWinsock(path)
            fixture = runner.create_special_file_fixture(path, windows=True, winsock=native)
            self.assertTrue(path.exists())
            self.assertFalse(fixture.closed)
            self.assertEqual(native.bound_family, runner._AF_UNIX)
            self.assertEqual(native.bound_path, str(path).encode("utf-8"))
            self.assertEqual(native.bound_length, ctypes.sizeof(runner._SockaddrUn))
            self.assertEqual(native.WSAStartup.calls[0][0], 0x0202)
            self.assertEqual(native.socket.calls, [(runner._AF_UNIX, runner._SOCK_STREAM, 0)])
            self.assertEqual(native.closesocket.calls, [])
            self.assertEqual(native.WSACleanup.calls, [])
            runner.cleanup_special_file_fixture(path, fixture)
            runner.cleanup_special_file_fixture(path, fixture)
            self.assertEqual(native.closesocket.calls, [(1234,)])
            self.assertEqual(native.WSACleanup.calls, [()])
            self.assertFalse(path.exists())

    def test_mocked_windows_bind_and_metadata_failures_clean_partial_state(self) -> None:
        """Maintainer logic verification only; this is not real Windows conformance."""
        for bind_result, create_path, diagnostic in (
            (-1, False, "bind returned SOCKET_ERROR (Winsock error 10047)"),
            (0, False, "bound pathname metadata is unavailable"),
        ):
            with self.subTest(diagnostic=diagnostic), tempfile.TemporaryDirectory() as raw:
                path = Path(raw) / "special"
                native = self.FakeWinsock(path, bind_result=bind_result, create_path=create_path)
                with self.assertRaises(runner.CaseFailure) as raised:
                    runner.create_special_file_fixture(path, windows=True, winsock=native)
                self.assertIn(diagnostic, str(raised.exception))
                self.assertEqual(native.closesocket.calls, [(1234,)])
                self.assertEqual(native.WSACleanup.calls, [()])
                self.assertFalse(path.exists())

    def test_mocked_windows_bind_failure_does_not_remove_unowned_path(self) -> None:
        """Maintainer logic verification only; this is not real Windows conformance."""
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "preexisting"
            path.write_text("owner data", encoding="utf-8")
            native = self.FakeWinsock(path, bind_result=-1, create_path=False)
            with self.assertRaisesRegex(runner.CaseFailure, "bind returned SOCKET_ERROR"):
                runner.create_special_file_fixture(path, windows=True, winsock=native)
            self.assertEqual(path.read_text(encoding="utf-8"), "owner data")
            self.assertEqual(native.closesocket.calls, [(1234,)])
            self.assertEqual(native.WSACleanup.calls, [()])

    def test_mocked_windows_fixture_survives_assertion_scope_and_cleans_on_failure(self) -> None:
        """Maintainer logic verification only; this is not real Windows conformance."""
        with tempfile.TemporaryDirectory() as raw:
            acquired = {}
            original_create = runner.create_special_file_fixture

            def acquire(path):
                native = self.FakeWinsock(path)
                fixture = original_create(path, windows=True, winsock=native)
                acquired.update(path=path, native=native, fixture=fixture)
                return fixture

            def fail_inside_scope(*_args):
                self.assertTrue(acquired["path"].exists())
                self.assertEqual(acquired["native"].closesocket.calls, [])
                self.assertEqual(acquired["native"].WSACleanup.calls, [])
                raise runner.CaseFailure("synthetic adapter assertion failure")

            temporary = Path(raw) / "case"
            temporary.mkdir()
            with (
                mock.patch.object(runner, "make_source_tree", side_effect=lambda workspace: (workspace / "sources").mkdir()),
                mock.patch.object(runner, "create_special_file_fixture", side_effect=acquire),
                mock.patch.object(runner, "_inventory_case_body", side_effect=fail_inside_scope),
                self.assertRaisesRegex(runner.CaseFailure, "synthetic adapter assertion failure"),
            ):
                runner.inventory_case(Path("skill"), Path("adapter"), {"id": "inventory-special-file"}, temporary)
            self.assertEqual(acquired["native"].closesocket.calls, [(1234,)])
            self.assertEqual(acquired["native"].WSACleanup.calls, [()])
            self.assertFalse(acquired["path"].exists())

    def test_mocked_windows_signatures_and_path_limit_diagnostic_are_stable(self) -> None:
        """Maintainer logic verification only; this is not real Windows conformance."""
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "special"
            native = self.FakeWinsock(path)
            fixture = runner.create_special_file_fixture(path, windows=True, winsock=native)
            try:
                self.assertEqual(native.socket.restype, runner._SOCKET)
                self.assertEqual(native.bind.argtypes[1], ctypes.POINTER(runner._Sockaddr))
                self.assertEqual(native.WSAStartup.argtypes[1], ctypes.POINTER(runner._WSAData))
            finally:
                fixture.close()
        too_long = Path("C:/") / ("x" * 108)
        native = self.FakeWinsock(too_long)
        with self.assertRaises(runner.CaseFailure) as raised:
            runner.create_special_file_fixture(too_long, windows=True, winsock=native)
        self.assertEqual(
            str(raised.exception),
            f"Windows AF_UNIX fixture setup failed: pathname UTF-8 length {len(str(too_long).encode('utf-8'))} exceeds 107-byte limit",
        )
        self.assertEqual(native.WSAStartup.calls, [])


class InitializePlanNormalizationTests(unittest.TestCase):
    @staticmethod
    def plan(workspace: str, record: str, manifest_record: str = "record") -> dict:
        return {
            "contractSha256": "a" * 64,
            "format": "wayfinder-initialize-plan",
            "manifest": {"recordRoot": manifest_record},
            "note": r"literal backslashes C:\not\a\path-field and JSON \"escaping\"",
            "workspace": {"workspaceRoot": workspace, "recordRoot": record},
        }

    def test_posix_spaces_unicode_json_escaping_and_repeatability(self) -> None:
        workspace = "/tmp/Way finder/naïve"
        plan = self.plan(workspace, workspace + "/record")
        first = runner.normalize_initialize_plan(plan, workspace)
        second = runner.normalize_initialize_plan(plan, workspace)
        self.assertEqual(first, second)
        value = json.loads(first)
        self.assertEqual(value["workspace"], {
            "workspaceRoot": "/private<WORKSPACE>",
            "recordRoot": "/private<WORKSPACE>/record",
        })
        self.assertEqual(value["note"], plan["note"])
        self.assertEqual(value["contractSha256"], "<CONTRACT_SHA256>")

    def test_windows_drive_letter_descendant_and_non_path_backslashes(self) -> None:
        supplied = "D:\\A FOLDE~1\\NAIVE~1\\WORKSP~1"
        physical = "D:\\a folder\\naïve\\workspace"
        plan = self.plan(physical, physical + "\\record")
        with mock.patch.object(runner, "windows_paths_share_identity", return_value=True) as same_identity:
            normalized = json.loads(runner.normalize_initialize_plan(plan, supplied))
        same_identity.assert_called_once_with(physical, supplied)
        self.assertEqual(normalized["workspace"]["workspaceRoot"], "/private<WORKSPACE>")
        self.assertEqual(normalized["workspace"]["recordRoot"], "/private<WORKSPACE>/record")
        self.assertEqual(normalized["note"], plan["note"])

    def test_windows_missing_or_divergent_physical_root_fails_closed(self) -> None:
        physical = "D:\\a folder\\workspace"
        supplied = "D:\\AFOLDE~1\\WORKSP~1"
        with mock.patch.object(
            runner, "windows_paths_share_identity", return_value=False
        ), self.assertRaisesRegex(runner.CaseFailure, "workspaceRoot differs"):
            runner.normalize_initialize_plan(self.plan(physical, physical + "\\record"), supplied)
        for error in (FileNotFoundError(), PermissionError(), ValueError()):
            with self.subTest(error=type(error).__name__), mock.patch.object(
                runner.os.path, "samefile", side_effect=error
            ):
                self.assertFalse(runner.windows_paths_share_identity(physical, supplied))

    def test_outside_inconsistent_or_nonlexical_record_root_fails_closed(self) -> None:
        for workspace, record in (
            ("/tmp/workspace", "/tmp/other/record"),
            ("D:\\workspace", "D:\\other\\record"),
            ("D:\\workspace", "D:\\workspace\\.\\record"),
            ("D:\\workspace", "D:/workspace/record"),
        ):
            with self.subTest(workspace=workspace), mock.patch.object(
                runner, "windows_paths_share_identity", return_value=True
            ), self.assertRaisesRegex(
                runner.CaseFailure, "recordRoot is not the manifest-bound descendant"
            ):
                runner.normalize_initialize_plan(self.plan(workspace, record), workspace)

    def test_malformed_or_inconsistent_windows_paths_fail_closed(self) -> None:
        cases = (
            self.plan("D:\\workspace", "D:\\workspace\\record", "record/../escape"),
            self.plan("D:\\workspace", "D:\\workspace\\record", "record\\child"),
            self.plan("D:\\workspace", "/tmp/workspace/record"),
        )
        for plan in cases:
            with self.subTest(plan=plan), mock.patch.object(
                runner, "windows_paths_share_identity", return_value=True
            ), self.assertRaises(runner.CaseFailure):
                runner.normalize_initialize_plan(plan, "D:\\workspace")

    def test_node_non_link_reparse_rules_are_executable(self) -> None:
        node = os.environ.get("WAYFINDER_NODE_RUNTIME") or shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable; executable helper check not run")
        node_source = (RUNTIME_ROOT / "scripts/adapters/wayfinder-node.mjs").read_text(encoding="utf-8")
        helper = node_source[node_source.index("function windowsDirent"):node_source.index("function physicalDirectory")]
        program = f'''let lstatCalls=0,readlinkCalls=0,contentReads=0,refreshMode="reparse",readlinkMode="einval";
const reparse=()=>({{name:"socket",isSymbolicLink:()=>true}}),regular=()=>({{name:"socket",isSymbolicLink:()=>false}});
const fs={{
  lstatSync:()=>{{lstatCalls++;return{{isSymbolicLink:()=>false,isDirectory:()=>false,isFile:()=>true}}}},
  readdirSync:()=>refreshMode==="missing"?[]:[refreshMode==="reparse"?reparse():regular()],
  readFileSync:()=>{{contentReads++;throw new Error("content read")}},
  readlinkSync:()=>{{readlinkCalls++;if(readlinkMode==="target")return"target";throw Object.assign(new Error(readlinkMode),{{code:readlinkMode==="einval"?"EINVAL":readlinkMode}})}}
}};
const path=require("path").win32;const process={{platform:"win32"}};{helper}
const entry=reparse();
if(lstatKind("C:\\\\work\\\\socket",entry)!=="unsupported-file"||lstatCalls||readlinkCalls!==1||contentReads)throw new Error("unsupported reparse classification");
readlinkMode="target";if(lstatKind("C:\\\\work\\\\socket",entry)!=="symlink"||lstatCalls||contentReads)throw new Error("link classification");
for(const code of ["EACCES","ENOENT","UNKNOWN"]){{readlinkMode=code;let threw=false;try{{lstatKind("C:\\\\work\\\\socket",entry)}}catch(error){{threw=error.code===code}}if(!threw)throw new Error("metadata failure did not fail closed: "+code);}}
readlinkMode="einval";for(const mode of ["missing","regular"]){{refreshMode=mode;let threw=false;try{{lstatKind("C:\\\\work\\\\socket",entry)}}catch(error){{threw=error.code==="EINVAL"}}if(!threw)throw new Error("changed reparse did not fail closed: "+mode);}}
refreshMode="reparse";if(lstatKind("C:\\\\work\\\\socket")!=="unsupported-file"||lstatKind("C:\\\\work\\\\socket",entry)!=="unsupported-file")throw new Error("selection/traversal mismatch");
if(contentReads)throw new Error("special file content was read");'''
        subprocess.run([node, "-e", program], check=True)

    def test_powershell_non_link_reparse_rules_are_executable(self) -> None:
        powershell = os.environ.get("WAYFINDER_POWERSHELL_RUNTIME") or shutil.which("pwsh")
        if not powershell:
            self.skipTest("PowerShell unavailable; executable helper check not run")
        ps_source = (RUNTIME_ROOT / "scripts/adapters/wayfinder-powershell.ps1").read_text(encoding="utf-8")
        helper = ps_source[ps_source.index("function Get-WfFileType"):ps_source.index("function Get-WfMarkdownCues")]
        program = helper + r'''
function Get-Item { [pscustomobject]@{ Attributes=[IO.FileAttributes]::ReparsePoint; LinkTarget=$script:Target } }
$script:Target=$null; if ((Get-WfFileType 'socket') -ne 'unsupported-file') { exit 2 }
$script:Target='target'; if ((Get-WfFileType 'link') -ne 'symlink') { exit 3 }
'''
        subprocess.run([powershell, "-NoLogo", "-NoProfile", "-Command", program], check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
