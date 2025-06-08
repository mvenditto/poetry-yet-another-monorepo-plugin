# ruff: noqa

from pathlib import Path
from tests.helpers import fake_repos_fs, TEST_REPOS_ROOT, poetry_factory
from yamp.monorepo import YampMonorepo
from cleo.io.null_io import NullIO
from tests.defaults import DEFAULT_PROJ_VERSION

from yamp.commands.build_projects_pinned import BuildProjectsPinnedHandler
from poetry.utils.env import EnvManager  # type: ignore[missing-type-stubs]
from pytest import MonkeyPatch
from pyfakefs.fake_filesystem import FakeFilesystem

import re


def test_cmd_build_projects_pinned(monkeypatch: MonkeyPatch, poetry_factory):
    fs: FakeFilesystem
    poetry, fs = poetry_factory("test-repo-1")

    repo = YampMonorepo(poetry)

    for p in repo.projects.values():
        assert p.version == DEFAULT_PROJ_VERSION

    _get_env = EnvManager.get

    def get_env_real_fs(self: EnvManager):
        fs.pause()
        env = _get_env(self)  # type: ignore
        fs.resume()
        return env

    monkeypatch.setattr(EnvManager, "get", get_env_real_fs)

    expected_output_dir = "output"

    build_version = "1.2.3"

    handler = BuildProjectsPinnedHandler(
        raw_version=build_version,
        sync_versions=False,
        monorepo=repo,
        clean=True,
        output=expected_output_dir,
        formats=["wheel", "sdist"],
        dry_run=False,
        config_settings={},
        io=NullIO(),
        logger=None,
    )

    assert handler.build() == 0

    for proj in repo.projects.values():
        path = proj.poetry.pyproject_path.parent
        output_dir = Path(path, expected_output_dir)
        assert output_dir.exists()
        artifacts = list(output_dir.iterdir())
        assert len(artifacts) == 2
        for f in artifacts:
            assert build_version in f.name

    repo2 = YampMonorepo(poetry)

    for p in repo2.projects.values():
        assert p.version == DEFAULT_PROJ_VERSION


def test_cmd_build_projects_pinned_sync_versions(monkeypatch: MonkeyPatch, poetry_factory):
    fs: FakeFilesystem
    poetry, fs = poetry_factory("test-repo-1")

    repo = YampMonorepo(poetry)

    for p in repo.projects.values():
        assert p.version == DEFAULT_PROJ_VERSION

    _get_env = EnvManager.get

    def get_env_real_fs(self: EnvManager):
        fs.pause()
        env = _get_env(self)  # type: ignore
        fs.resume()
        return env

    monkeypatch.setattr(EnvManager, "get", get_env_real_fs)

    expected_output_dir = "output"

    build_version = "1.2.3"

    handler = BuildProjectsPinnedHandler(
        raw_version=build_version,
        sync_versions=True,
        monorepo=repo,
        clean=True,
        output=expected_output_dir,
        formats=["wheel", "sdist"],
        dry_run=False,
        config_settings={},
        io=NullIO(),
        logger=None,
    )

    assert handler.build() == 0

    for proj in repo.projects.values():
        path = proj.poetry.pyproject_path.parent
        output_dir = Path(path, expected_output_dir)
        assert output_dir.exists()
        artifacts = list(output_dir.iterdir())
        assert len(artifacts) == 2
        for f in artifacts:
            assert build_version in f.name

    repo2 = YampMonorepo(poetry)

    for p in repo2.projects.values():
        assert p.version == build_version
