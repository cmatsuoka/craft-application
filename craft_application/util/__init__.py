# This file is part of craft_application.
#
# Copyright 2023-2024 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Utilities for craft-application."""

from craft_application.util.callbacks import get_unique_callbacks
from craft_application.util.docs import render_doc_url
from craft_application.util.logging import setup_loggers
from craft_application.util.paths import (
    get_filename_from_url_path,
    get_managed_logpath,
    get_managed_pack_state_path,
    get_work_dir,
    get_home_temporary_directory,
)
from craft_application.util.platforms import (
    get_host_architecture,
    convert_architecture_deb_to_platform,
    get_host_base,
    is_valid_architecture,
    get_hostname,
    is_managed_mode,
)
from craft_application.util.retry import retry
from craft_application.util.snap_config import (
    SnapConfig,
    get_snap_config,
    is_running_from_snap,
)
from craft_application.util.string import humanize_list, strtobool
from craft_application.util.system import get_parallel_build_count
from craft_application.util.yaml import dump_yaml, safe_yaml_load
from craft_application.util.cli import format_timestamp

__all__ = [
    "get_unique_callbacks",
    "render_doc_url",
    "setup_loggers",
    "get_filename_from_url_path",
    "get_managed_logpath",
    "get_managed_pack_state_path",
    "get_work_dir",
    "get_home_temporary_directory",
    "get_host_architecture",
    "convert_architecture_deb_to_platform",
    "get_snap_config",
    "is_running_from_snap",
    "is_valid_architecture",
    "SnapConfig",
    "humanize_list",
    "strtobool",
    "get_host_base",
    "dump_yaml",
    "safe_yaml_load",
    "retry",
    "get_parallel_build_count",
    "get_hostname",
    "is_managed_mode",
    "format_timestamp",
]
