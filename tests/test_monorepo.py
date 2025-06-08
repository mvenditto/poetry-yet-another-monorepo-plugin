# ruff: noqa

from collections.abc import Callable
import os
import pytest

from pathlib import Path
from tests.scenarios import fake_repos_fs, TEST_REPOS_ROOT
from yamp.monorepo import YampMonorepo
from poetry.factory import Factory
from poetry.poetry import Poetry
from dataclasses import replace


@pytest.fixture
def poetry_factory(fake_repos_fs) -> Callable[[str], Poetry]:
    def factory(name: str):
        return Factory().create_poetry(cwd=Path(TEST_REPOS_ROOT, name))

    return factory


def test_monorepo_projects_are_loaded(poetry_factory):
    poetry = poetry_factory("test-repo-1")
    repo = YampMonorepo(poetry)
    for name in ("foo", "bar", "baz", "qux"):
        assert f"proj-{name}" in repo.projects


def test_monorepo_excludes_are_honored(poetry_factory):
    poetry = poetry_factory("test-repo-1")
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
    poetry = poetry_factory("test-repo-1")

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
