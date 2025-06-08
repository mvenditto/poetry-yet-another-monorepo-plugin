# ruff: noqa

from tests.helpers import fake_repos_fs, TEST_REPOS_ROOT, poetry_factory
from yamp.monorepo import YampMonorepo
from dataclasses import replace


def test_monorepo_projects_are_loaded(poetry_factory):
    poetry, _ = poetry_factory("test-repo-1")
    repo = YampMonorepo(poetry)
    for name in ("foo", "bar", "baz", "qux"):
        assert f"proj-{name}" in repo.projects


def test_monorepo_excludes_are_honored(poetry_factory):
    poetry, _ = poetry_factory("test-repo-1")
    repo = YampMonorepo(poetry)

    for name in ("foo", "bar", "baz", "qux"):
        assert f"proj-{name}" in repo.projects

    cfg = poetry.pyproject.data["tool"]["poetry-yet-another-monorepo-plugin"]

    cfg["exclude-projects"] = [
        "^proj-b.*$",
    ]

    repo = YampMonorepo(poetry)

    for name in ("foo", "qux"):
        assert f"proj-{name}" in repo.projects

    for name in ("bar", "baz"):
        assert f"proj-{name}" not in repo.projects


def test_monorepo_repos_are_inherited(poetry_factory):
    poetry, _ = poetry_factory("test-repo-1")

    repo = YampMonorepo(poetry)

    for proj in repo.projects.values():
        repo.prepare_project(proj)
        pool = proj.poetry.pool
        assert not pool.has_repository("repo-a")
        assert not pool.has_repository("repo-b")
        assert not pool.has_repository("repo-c")

    repo.config = replace(repo.config, projects_inherit_repos=True)

    for proj in repo.projects.values():
        repo.prepare_project(proj)
        pool = proj.poetry.pool
        assert pool.has_repository("repo-a")
        assert pool.has_repository("repo-b")
        assert pool.has_repository("repo-c")
