import os
import re
from collections.abc import Mapping
from logging import getLogger
from pathlib import Path
from typing import Any, Final

from cleo.commands.command import Command
from poetry.console.application import Application
from poetry.pyproject.toml import PyProjectTOML

from yamp.config import YampConfig
from yamp.project import YampProject
from yamp.utils import get_project_key

_DEFAULT_CONFIG: Final[dict[str, Any]] = {
    "projects_dir": "projects",
    "exclude_projects": [],
}


class YampMonorepo:
    def __init__(self, application: Application):
        self.application = application
        self.poetry = self.application.poetry
        self.logger = getLogger("yamp")
        self.config = self._load_config()
        self.root_pyproject = self._load_root_pyproject()
        self.projects = self._load_projects()

    @property
    def workdir(self) -> Path:
        return self.root_pyproject.path.parent

    @property
    def projects_dir(self) -> Path:
        return Path(self.workdir, self.config.projects_dir)

    @property
    def version(self) -> str:
        return get_project_key(self.root_pyproject, "version")  # type: ignore

    def get_command_version(self, command: Command | None) -> str | None:
        version = self.version
        version_override_opt: str | None = None

        if command:
            version_override_opt = command.option("version-override")

        version_override_env = os.environ.get("YAMP_VERSION_OVERRIDE")

        if version_override_opt:
            self.logger.debug("Option '--version-override' was set to %s", version_override_opt)
            version = version_override_opt
        elif version_override_env:
            self.logger.debug(
                "ENV var. 'YAMP_VERSION_OVERRIDE' was set to %s", version_override_env
            )
            version = version_override_env
        else:
            self.logger.debug("Version from root pyproject.toml is %s", version)

        return version

    def _load_config(self):
        pyproject_config = self.application.poetry.pyproject.data

        local_config: dict[str, Any] = pyproject_config.get("tool", {}).get(
            "poetry-yet-another-monorepo-plugin", {}
        )

        self.logger.debug("Local config: %s", local_config)

        merged_config = {**_DEFAULT_CONFIG, **local_config}

        final_config = {k.replace("-", "_"): v for k, v in merged_config.items()}

        self.logger.debug("Final config: %s", final_config)

        return YampConfig(**final_config)

    def _load_root_pyproject(self) -> PyProjectTOML:
        cwd = os.getcwd()
        root_pyproject_path = Path(cwd, "pyproject.toml")
        self.logger.info("Init monorepo: cwd=%s", cwd)
        self.logger.info("Init monorepo: root_pyproject=%s", root_pyproject_path)

        if not root_pyproject_path.exists():
            raise FileExistsError(f"yamp: Failed to load {root_pyproject_path}")

        return PyProjectTOML(root_pyproject_path)

    def _load_projects(self) -> Mapping[str, YampProject]:
        projects_dir = Path(os.getcwd(), self.config.projects_dir)

        self.logger.info("Loading projects: projects-dir=%s", projects_dir)

        if not projects_dir.exists() or not projects_dir.is_dir():
            raise Exception(
                f"projects-dir ({projects_dir}) does not exists or it is not a directory."
            )

        projects = {}

        for proj_path in projects_dir.iterdir():
            if not proj_path.is_dir():
                self.logger.warning("SKIP %s: not a directory.", proj_path)
                continue

            pyproject_path = Path(proj_path, "pyproject.toml")

            proj_name = proj_path.name

            if not pyproject_path.exists():
                self.logger.warning(
                    "SKIP '%s': pyproject.toml expected but not found at %s.",
                    proj_name,
                    pyproject_path,
                )
                continue

            exclude_pattern = None
            for pattern in self.config.exclude_projects or []:
                self.logger.debug(
                    "Checking exclude pattern '%s' against project '%s'", pattern, proj_name
                )
                if re.match(pattern, proj_name):
                    exclude_pattern = pattern
                    break

            if exclude_pattern is not None:
                self.logger.debug(
                    "Project '%s' skipped because it matched exlcude pattern: %s",
                    proj_name,
                    exclude_pattern,
                )
                continue

            try:
                projects[proj_name] = YampProject(pyproject_path)
                self.logger.info("Found project: %s", pyproject_path)
            except:  # noqa
                self.logger.exception("Failed to load: %s", pyproject_path)

        return projects
