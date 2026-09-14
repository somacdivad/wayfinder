#!/usr/bin/env python3
"""Deterministic regression tests for candidate revision 9 Windows corrections."""

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
import socket
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
adapter = load_module("wayfinder_revision_9_adapter", ADAPTER_PATH)
sys.path.insert(0, str(RUNNER_PATH.parent))
try:
    runner = load_module("wayfinder_revision_9_runner", RUNNER_PATH)
finally:
    sys.path.pop(0)


class FakeCall:
    def __init__(self, result):
        self.result = result
        self.calls = []
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        self.calls.append(args)
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
    def test_local_socket_or_fifo_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "special"
            live = runner.create_special_file_fixture(path, windows=False)
            try:
                self.assertEqual(adapter._relative_kind(path), "unsupported-file")
            finally:
                runner.cleanup_special_file_fixture(path, live)
            self.assertFalse(path.exists())

    def test_windows_socket_lifetime_and_explicit_failure(self) -> None:
        class FakeSocket:
            def __init__(self, fail=False):
                self.fail = fail
                self.closed = False

            def bind(self, value):
                if self.fail:
                    raise OSError("provider unavailable")
                Path(value).touch()

            def close(self):
                self.closed = True

        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "special"
            fake = FakeSocket()
            with mock.patch.object(runner.socket, "socket", return_value=fake):
                live = runner.create_special_file_fixture(path, windows=True)
            self.assertIs(live, fake)
            self.assertTrue(path.exists())
            self.assertFalse(fake.closed)
            runner.cleanup_special_file_fixture(path, live)
            self.assertTrue(fake.closed)
            self.assertFalse(path.exists())
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "special"
            fake = FakeSocket(fail=True)
            with mock.patch.object(runner.socket, "socket", return_value=fake):
                with self.assertRaises(runner.CaseFailure):
                    runner.create_special_file_fixture(path, windows=True)
            self.assertTrue(fake.closed)
            self.assertFalse(path.exists())

    def test_node_and_powershell_non_link_reparse_rules_are_executable(self) -> None:
        node = os.environ["WAYFINDER_NODE_RUNTIME"]
        node_source = (RUNTIME_ROOT / "scripts/adapters/wayfinder-node.mjs").read_text(encoding="utf-8")
        helper = node_source[node_source.index("function windowsDirent"):node_source.index("function physicalDirectory")]
        program = f'''const fs={{lstatSync:()=>({{isSymbolicLink:()=>false,isDirectory:()=>false,isFile:()=>true}}),readdirSync:()=>[]}};
const path=require("path").win32;const process={{platform:"win32"}};{helper}
const entry={{isSymbolicLink:()=>true}};
fs.readlinkSync=()=>{{throw Object.assign(new Error("not a link"),{{code:"EINVAL"}})}};
if(lstatKind("C:\\\\work\\\\socket",entry)!=="unsupported-file")process.exit(2);
fs.readlinkSync=()=>"target";if(lstatKind("C:\\\\work\\\\link",entry)!=="symlink")process.exit(3);'''
        subprocess.run([node, "-e", program], check=True)

        powershell = os.environ["WAYFINDER_POWERSHELL_RUNTIME"]
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
