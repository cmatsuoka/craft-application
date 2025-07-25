#  This file is part of craft-application.
#
#  Copyright 2023-2024 Canonical Ltd.
#
#  This program is free software: you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License version 3, as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
#  SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Integration tests for provider service."""

import contextlib
import subprocess

import craft_platforms
import craft_providers
import pytest


@pytest.mark.parametrize(
    "base_name",
    [
        pytest.param(
            craft_platforms.DistroBase("ubuntu", "24.10"),
            id="ubuntu_latest",
            marks=pytest.mark.skip(
                reason="Skipping Oracular test for now; see https://github.com/canonical/craft-providers/issues/598"
            ),
        ),
        pytest.param(craft_platforms.DistroBase("ubuntu", "24.04"), id="ubuntu@24.04"),
        pytest.param(craft_platforms.DistroBase("ubuntu", "22.04"), id="ubuntu@22.04"),
        pytest.param(craft_platforms.DistroBase("almalinux", "9"), id="almalinux@9"),
    ],
)
@pytest.mark.parametrize(
    "name",
    [
        pytest.param("lxd", marks=pytest.mark.lxd),
        pytest.param("multipass", marks=pytest.mark.multipass),
    ],
)
# The LXD tests can be flaky, erroring out with a BaseCompatibilityError:
# "Clean incompatible instance and retry the requested operation."
# This is due to an upstream LXD bug that appears to still be present in LXD 5.14:
# https://github.com/canonical/lxd/issues/11422
@pytest.mark.flaky(reruns=3, reruns_delay=2)
@pytest.mark.slow
def test_provider_lifecycle(
    snap_safe_tmp_path, app_metadata, provider_service, state_service, name, base_name
):
    """Set up an instance and allow write access to the project and state directories."""
    if name == "multipass" and base_name.distribution != "ubuntu":
        pytest.skip("multipass only provides ubuntu images")
    provider_service.get_provider(name)

    arch = craft_platforms.DebianArchitecture.from_host()
    build_info = craft_platforms.BuildInfo("foo", arch, arch, base_name)
    instance = provider_service.instance(build_info, work_dir=snap_safe_tmp_path)
    executor = None
    try:
        with instance as executor:
            # the provider service must allow writes in the state service directory
            executor.execute_run(
                ["touch", f"{state_service._managed_state_dir}/test.txt"],
                check=True,
            )
            executor.execute_run(
                ["touch", str(app_metadata.managed_instance_project_path / "test")],
                check=True,
            )
            proc_result = executor.execute_run(
                ["cat", "/root/.bashrc"],
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            )
    finally:
        if executor is not None:
            with contextlib.suppress(craft_providers.ProviderError):
                executor.delete()

    assert (snap_safe_tmp_path / "test").exists()
    assert proc_result.stdout.startswith("#!/bin/bash")


@pytest.mark.parametrize("base", [craft_platforms.DistroBase("ubuntu", "22.04")])
@pytest.mark.parametrize(
    "proxy_vars",
    [
        {
            "http_proxy": "http://craft-application-test.local:0",
            "https_proxy": "https://craft-application-test.local:0",
            "no_proxy": "::1,127.0.0.1,0.0.0.0,canonical.com",
        },
    ],
)
@pytest.mark.parametrize("provider_name", [pytest.param("lxd", marks=pytest.mark.lxd)])
@pytest.mark.slow
def test_proxy_variables_forwarded(
    monkeypatch, snap_safe_tmp_path, provider_service, base, proxy_vars, provider_name
):
    for var, content in proxy_vars.items():
        monkeypatch.setenv(var, content)
    arch = craft_platforms.DebianArchitecture.from_host()
    build_info = craft_platforms.BuildInfo("foo", arch, arch, base)
    provider_service.get_provider(provider_name)
    executor = None

    provider_service.setup()
    try:
        with provider_service.instance(
            build_info, work_dir=snap_safe_tmp_path
        ) as executor:
            proc_result = executor.execute_run(
                ["env"], text=True, stdout=subprocess.PIPE, check=True
            )
    finally:
        if executor is not None:
            with contextlib.suppress(craft_providers.ProviderError):
                executor.delete()

    instance_env = {}
    for line in proc_result.stdout.splitlines():
        name, value = line.split("=", maxsplit=1)
        instance_env[name] = value

    for var, content in proxy_vars.items():
        assert instance_env.get(var) == content


@pytest.mark.slow
@pytest.mark.parametrize("fetch", [False, True])
def test_run_managed(provider_service, fake_services, fetch, snap_safe_tmp_path):
    base = craft_platforms.DistroBase("ubuntu", "24.04")
    arch = craft_platforms.DebianArchitecture.from_host()
    build_info = craft_platforms.BuildInfo("foo", arch, arch, base)

    fetch_service = fake_services.get("fetch")
    fetch_service.set_policy("permissive")

    provider_service._work_dir = snap_safe_tmp_path

    provider_service.run_managed(
        build_info, enable_fetch_service=fetch, command=["echo", "hi"]
    )
