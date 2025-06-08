import contextlib
from collections.abc import Generator
from functools import cached_property
from logging import Logger, getLogger

from cleo.io.io import IO
from cleo.io.null_io import NullIO
from poetry.core.constraints.version import Version
from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.pyproject.toml import PyProjectTOML
from poetry.repositories.repository_pool import RepositoryPool

from yamp.utils import get_project_key


class YampProject:
    def __init__(
        self,
        pyproject: PyProjectTOML,
        io: IO | None = None,
        logger: Logger | None = None,
    ):
        self.pyproject = pyproject
        self.io = io or NullIO()
        self.logger = logger or getLogger(str(None))

    @property
    def version(self) -> str:
        return get_project_key(self.pyproject, "version")  # type: ignore

    @cached_property
    def name(self) -> str:
        return get_project_key(self.pyproject, "name")

    @cached_property
    def poetry(self) -> Poetry:
        return self.create_poetry(self.io)

    @contextlib.contextmanager
    def package_version_override(self, version: str | Version) -> Generator[None, None, None]:
        """A context manager to temporarly override the package version."""
        if isinstance(version, str):
            version = Version.parse(version)

        curr_version = self.poetry.package.version
        self.poetry.package.version = version
        self.logger.debug(
            "Override package version for '%s': %s -> %s",
            self.name,
            curr_version,
            version,
        )
        yield
        self.poetry.package.version = curr_version
        self.logger.debug(
            "Revert package version for '%s': %s -> %s",
            self.name,
            version,
            curr_version,
        )

    def create_poetry(self, io: IO | None = None) -> Poetry:
        return Factory().create_poetry(
            cwd=self.pyproject.path.parent,
            io=io or self.io,
        )

    def copy_repos_from(self, other_pool: RepositoryPool):
        self_pool = self.poetry.pool
        for repo in other_pool.all_repositories:
            # TODO: exclude "PyPI" by default ?
            if self_pool.has_repository(repo.name):
                self.io.write_line(
                    f"<warning>Repository '{repo.name}' already added to '{self.name}'</warning>"
                )
                continue

            priority = other_pool.get_priority(repo.name)
            self_pool.add_repository(repo, priority=priority)
