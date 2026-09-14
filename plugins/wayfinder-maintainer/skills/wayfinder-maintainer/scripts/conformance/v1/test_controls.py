"""Maintainer-only deterministic controls reserved by the conformance harness."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping


RFC3339_SECONDS = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
OPERATION_ID = re.compile(r"^wfinit-test-[a-z0-9]+(?:-[a-z0-9]+)*$")
FAILURE_BOUNDARY = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
INJECTION_KEYS = (
    "WAYFINDER_TEST_CLOCK",
    "WAYFINDER_TEST_OPERATION_ID",
    "WAYFINDER_TEST_FAILURE_BOUNDARY",
)


@dataclass(frozen=True)
class TestControls:
    clock: str | None
    operation_id: str | None
    failure_boundary: str | None

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> "TestControls":
        enabled = environment.get("WAYFINDER_TEST_MODE") == "1"
        supplied = [key for key in INJECTION_KEYS if environment.get(key)]
        if supplied and not enabled:
            raise ValueError("maintainer controls require WAYFINDER_TEST_MODE=1")
        if not enabled:
            return cls(None, None, None)
        clock = environment.get("WAYFINDER_TEST_CLOCK")
        operation_id = environment.get("WAYFINDER_TEST_OPERATION_ID")
        failure_boundary = environment.get("WAYFINDER_TEST_FAILURE_BOUNDARY")
        if clock is not None and not RFC3339_SECONDS.fullmatch(clock):
            raise ValueError("test clock must use UTC RFC 3339 whole seconds")
        if operation_id is not None and not OPERATION_ID.fullmatch(operation_id):
            raise ValueError("test operation id is outside its reserved namespace")
        if failure_boundary is not None and not FAILURE_BOUNDARY.fullmatch(failure_boundary):
            raise ValueError("test failure boundary must be a lowercase ASCII slug")
        return cls(clock, operation_id, failure_boundary)

    def as_dict(self) -> dict[str, str | None]:
        return {
            "clock": self.clock,
            "operationId": self.operation_id,
            "failureBoundary": self.failure_boundary,
        }
