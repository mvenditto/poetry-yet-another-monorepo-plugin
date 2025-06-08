# ruff: noqa

from tests.helpers import fake_repos_fs, TEST_REPOS_ROOT, poetry_factory
from yamp.monorepo import YampMonorepo
from cleo.io.null_io import NullIO
from tests.defaults import DEFAULT_PROJ_VERSION

from yamp.commands.set_projects_version import SetProjectsVersionHandler


def test_cmd_set_projects_version(poetry_factory):
    poetry, _ = poetry_factory("test-repo-1")

    repo = YampMonorepo(poetry)

    for p in repo.projects.values():
        assert p.version == DEFAULT_PROJ_VERSION

    expected_version = "1.2.3"

    handler = SetProjectsVersionHandler(
        new_version=expected_version,
        monorepo=repo,
        dry_run=False,
        io=NullIO(),
    )
    assert handler.handle() == 0

    repo2 = YampMonorepo(poetry)

    for p in repo2.projects.values():
        assert p.version == expected_version


def test_cmd_set_projects_version_dryrun(poetry_factory):
    poetry, _ = poetry_factory("test-repo-1")

    repo = YampMonorepo(poetry)

    for p in repo.projects.values():
        assert p.version == DEFAULT_PROJ_VERSION

    expected_version = "1.2.3"

    handler = SetProjectsVersionHandler(
        new_version=expected_version,
        monorepo=repo,
        dry_run=True,
        io=NullIO(),
    )
    assert handler.handle() == 0

    repo2 = YampMonorepo(poetry)

    for p in repo2.projects.values():
        assert p.version == DEFAULT_PROJ_VERSION
