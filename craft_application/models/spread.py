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


class SpreadBaseModel(CraftBaseModel):
    def model_post_init(self, __context):
        none_items = []
        for k, v in self.__dict__.items():
            if v is None:
                none_items.append(k)

        for k in none_items:
            k.replace("_", "-")
            delattr(self, k)


# Simplified spread configuration


class SimpleSpreadSystem(CraftBaseModel):
    """Simplified spread system configuration."""

    workers: int | None = None


class SimpleSpreadBackend(CraftBaseModel):
    """Simplified spread backend configuration."""

    type: str
    systems: list[dict[str, SimpleSpreadSystem | None]]


class SimpleSpreadSuite(CraftBaseModel):
    """Simplified spread suite configuration."""

    summary: str
    systems: list[str]
    environment: dict[str, str] | None = {}
    prepare: str | None = None
    restore: str | None = None
    prepare_each: str | None = None
    restore_each: str | None = None
    kill_timeout: str | None = None


class SimpleSpreadYaml(CraftBaseModel):
    """Simplified spread project configuration."""

    backends: dict[str, SimpleSpreadBackend]
    suites: dict[str, SimpleSpreadSuite]
    exclude: list[str] | None = None
    prepare: str | None = None
    restore: str | None = None
    prepare_each: str | None = None
    restore_each: str | None = None
    kill_timeout: str | None = None


# Processed full-form spread configuration


class SpreadSystem(SpreadBaseModel):
    """Processed spread system configuration."""

    username: str
    password: str
    workers: int | None = None

    @classmethod
    def from_simple(cls, simple: SimpleSpreadSystem) -> Self:
        """Create a spread system configuration from the simplified version."""
        workers = simple.workers if simple else 1
        return cls(
            workers=workers,
            username="spread",
            password="spread",  # noqa: S106 (possible hardcoded password)
        )


class SpreadBackend(SpreadBaseModel):
    """Processed spread backend configuration."""

    type: str
    allocate: str | None = None
    discard: str | None = None
    systems: list[dict[str, SpreadSystem]] = []
    prepare: str | None = None
    restore: str | None = None
    prepare_each: str | None = None
    restore_each: str | None = None

    @classmethod
    def from_simple(cls, simple: SimpleSpreadBackend) -> Self:
        """Create a spread backend configuration from the simplified version."""
        return cls(
            type=simple.type,
            allocate=simple.allocate,
            discard=simple.discard,
            systems=cls.systems_from_simple(simple.systems),
            prepare=simple.prepare,
            restore=simple.restore,
            prepare_each=simple.prepare_each,
            restore_each=simple.restore_each,
        )

    @staticmethod
    def systems_from_simple(
        simple: list[dict[str, SimpleSpreadSystem | None]],
    ) -> list[dict[str, SpreadSystem]]:
        systems: list[dict[str, SpreadSystem]] = []
        for item in simple:
            entry: dict[str, SpreadSystem] = {}
            for name, ssys in item.items():
                entry[name] = SpreadSystem.from_simple(ssys)
            systems.append(entry)

        return systems


class SpreadSuite(SpreadBaseModel):
    """Processed spread suite configuration."""

    summary: str
    systems: list[str]
    environment: dict[str, str] | None
    prepare: str | None
    restore: str | None
    prepare_each: str | None
    restore_each: str | None
    kill_timeout: str | None = None

    @classmethod
    def from_simple(cls, simple: SimpleSpreadSuite) -> Self:
        """Create a spread suite configuration from the simplified version."""
        return cls(
            summary=simple.summary,
            systems=simple.systems,
            environment=simple.environment,
            prepare=simple.prepare,
            restore=simple.restore,
            prepare_each=simple.prepare_each,
            restore_each=simple.restore_each,
            kill_timeout=simple.kill_timeout,  # TODO: add time limit
        )


class SpreadYaml(SpreadBaseModel):
    """Processed spread project configuration."""

    project: str
    environment: dict[str, str]
    backends: dict[str, SpreadBackend]
    suites: dict[str, SpreadSuite]
    exclude: list[str]
    path: str
    prepare: str | None
    restore: str | None
    prepare_each: str | None
    restore_each: str | None
    kill_timeout: str

    @classmethod
    def from_simple(
        cls,
        simple: SimpleSpreadYaml,
        *,
        craft_backend: SpreadBackend,
    ) -> Self:
        """Create the spread configuration from the simplified version."""
        return cls(
            project="craft-test",
            environment={
                "SUDO_USER": "",
                "SUDO_UID": "",
                "LANG": "C.UTF-8",
                "LANGUAGE": "en",
            },
            backends=cls._backends_from_simple(simple.backends, craft_backend),
            suites=cls._suites_from_simple(simple.suites),
            exclude=simple.exclude or [".git", ".tox"],
            path="/home/spread/proj",
            prepare=simple.prepare,
            restore=simple.restore,
            prepare_each=simple.prepare_each,
            restore_each=simple.restore_each,
            kill_timeout=simple.kill_timeout or "1h",  # TODO: add time limit
        )

    @staticmethod
    def _backends_from_simple(
        simple: dict[str, SimpleSpreadBackend], craft_backend: SpreadBackend
    ) -> dict[str, SpreadBackend]:
        backends: dict[str, SpreadBackend] = {}
        for name, backend in simple.items():
            if name == "craft":
                craft_backend.systems = SpreadBackend.systems_from_simple(
                    backend.systems
                )
                backends[name] = craft_backend
            else:
                backends[name] = SpreadBackend.from_simple(backend)

        return backends

    @staticmethod
    def _suites_from_simple(
        simple: dict[str, SimpleSpreadSuite]
    ) -> dict[str, SpreadSuite]:
        suites: dict[str, SpreadSuite] = {}
        for name, suite in simple.items():
            suites[name] = SpreadSuite.from_simple(suite)

        return suites
