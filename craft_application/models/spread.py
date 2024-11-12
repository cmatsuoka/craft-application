# This file is part of craft-application.
#
# Copyright 2024 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Models representing spread projects."""


from typing_extensions import Self

from craft_application.models import CraftBaseModel

# Simplified spread configuration


class SimpleSpreadSystem(CraftBaseModel):
    """Simplified spread system configuration."""

    workers: int | None


class SimpleSpreadBackend(CraftBaseModel):
    """Simplified spread backend configuration."""

    type: str
    systems: list[dict[str, SimpleSpreadSystem]]


class SimpleSpreadSuite(CraftBaseModel):
    """Simplified spread suite configuration."""

    summary: str
    systems: list[str]
    environment: dict[str, str]


class SimpleSpreadYaml(CraftBaseModel):
    """Simplified spread project configuration."""

    backends: dict[str, SimpleSpreadBackend]
    suites: dict[str, SimpleSpreadSuite]
    exclude: list[str] | None
    kill_timeout: str | None


# Processed full-form spread configuration


class SpreadSystem(CraftBaseModel):
    """Processed spread system configuration."""

    username: str
    password: str
    workers: int | None

    @classmethod
    def from_simple(cls, simple: SimpleSpreadSystem) -> Self:
        """Create a spread system configuration from the simplified version."""
        return cls(
            workers=simple.workers,
            username="spread",
            password="spread",  # noqa: S106 (possible hardcoded password)
        )


class SpreadBackend(CraftBaseModel):
    """Processed spread backend configuration."""

    type: str
    allocate: str | None
    discard: str | None
    systems: list[dict[str, SpreadSystem]]

    @classmethod
    def from_simple(cls, simple: SimpleSpreadBackend, *, backend_type: str) -> Self:
        """Create a spread backend configuration from the simplified version."""
        if backend_type == "adhoc":
            allocate = '"$PROJECT_PATH"/spread/.extension allocate'
            discard = '"$PROJECT_PATH"/spread/.extension discard'
        else:
            allocate = None
            discard = None

        return cls(
            type=backend_type,
            allocate=allocate,
            discard=discard,
            systems=cls._systems_from_simple(simple.systems),
        )

    @staticmethod
    def _systems_from_simple(
        simple: list[dict[str, SimpleSpreadSystem]],
    ) -> list[dict[str, SpreadSystem]]:
        systems: list[dict[str, SpreadSystem]] = []
        for item in simple:
            entry: dict[str, SpreadSystem] = {}
            for name, ssys in item.items():
                entry[name] = SpreadSystem.from_simple(ssys)
            systems.append(entry)

        return systems


class SpreadSuite(CraftBaseModel):
    """Processed spread suite configuration."""

    summary: str
    systems: list[str]
    environment: dict[str, str]
    prepare: str
    restore: str
    prepare_each: str
    restore_each: str

    @classmethod
    def from_simple(cls, simple: SimpleSpreadSuite) -> Self:
        """Create a spread suite configuration from the simplified version."""
        return cls(
            summary=simple.summary,
            systems=simple.systems,
            environment=simple.environment,
            prepare='"$PROJECT_PATH"/spread/.extension suite-prepare',
            restore='"$PROJECT_PATH"/spread/.extension suite-restore',
            prepare_each='"$PROJECT_PATH"/spread/.extension suite-prepare-each',
            restore_each='"$PROJECT_PATH"/spread/.extension suite-restore-each',
        )


class SpreadYaml(CraftBaseModel):
    """Processed spread project configuration."""

    project: str
    environment: dict[str, str]
    backends: dict[str, SpreadBackend]
    suites: dict[str, SpreadSuite]
    exclude: list[str]
    path: str
    prepare: str
    restore: str
    prepare_each: str
    restore_each: str
    kill_timeout: str

    @classmethod
    def from_simple(
        cls,
        simple: SimpleSpreadYaml,
        *,
        backend_type: str,
    ) -> Self:
        """Create the spread configuration from the simplified version."""
        return cls(
            project="craft-test",
            environment={
                "SUDO_USER": "",
                "SUDO_UID": "",
                "LANG": "C.UTF-8",
                "LANGUAGE": "en",
                "PROJECT_PATH": "/home/spread/proj",
            },
            backends=cls._backends_from_simple(simple.backends, backend_type),
            suites=cls._suites_from_simple(simple.suites),
            exclude=simple.exclude or [".git", ".tox"],
            path="/home/spread/proj",
            prepare='"$PROJECT_PATH"/spread/.extension prepare',
            restore='"$PROJECT_PATH"/spread/.extension restore',
            prepare_each='"$PROJECT_PATH"/spread/.extension prepare-each',
            restore_each='"$PROJECT_PATH"/spread/.extension restore-each',
            kill_timeout=simple.kill_timeout or "1h",
        )

    @staticmethod
    def _backends_from_simple(
        simple: dict[str, SimpleSpreadBackend], backend_type: str
    ) -> dict[str, SpreadBackend]:
        backends: dict[str, SpreadBackend] = {}
        for name, backend in simple.items():
            backends[name] = SpreadBackend.from_simple(
                backend, backend_type=backend_type
            )

        return backends

    @staticmethod
    def _suites_from_simple(
        simple: dict[str, SimpleSpreadSuite]
    ) -> dict[str, SpreadSuite]:
        suites: dict[str, SpreadSuite] = {}
        for name, suite in simple.items():
            suites[name] = SpreadSuite.from_simple(suite)

        return suites
