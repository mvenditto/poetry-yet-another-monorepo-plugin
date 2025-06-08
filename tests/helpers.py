import textwrap
from collections.abc import Callable
from pathlib import Path

import pytest
from poetry.factory import Factory
from poetry.poetry import Poetry
from pyfakefs.fake_filesystem import FakeFilesystem

from tests.defaults import DEFAULT_PROJ_VERSION

TEST_REPOS_ROOT = "/test-cases"
REPO_NAME = "test-repo-1"
PROJECTS_DIR = "projects"
PROJECT_NAMES = ("foo", "bar", "baz", "qux")

PROJECT_PYPROJECT_TEMPLATE = textwrap.dedent("""\
[project]
name = "proj-{{PROJECT-NAME}}"
version = "{{PROJECT-VERSION}}"
description = ""
authors = [
    {name = "test",email = "test@test.com"}
]
requires-python = ">=3.12"
dependencies = [
]

[tool.poetry]
packages = [{ include = "proj_{{PROJECT-NAME}}" }]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
""")

ROOT_PYPROJECT_CONTENT = textwrap.dedent("""\
[project]
name = "test-repo-1"
version = "0.0.1"
description = ""
authors = [
    {name = "test",email = "test@test.com"}
]
requires-python = ">=3.12"
dependencies = [
]

[tool.poetry.requires-plugins]
poetry-yet-another-monorepo-plugin = ">=0.1.0"

[[tool.poetry.source]]
name = "repo-a"
url = "https://pypi.a.org/simple/"
priority = "supplemental"

[[tool.poetry.source]]
name = "repo-b"
url = "https://pypi.b.org/simple/"
priority = "primary"

[[tool.poetry.source]]
name = "repo-c"
url = "https://pypi.c.org/simple/"
priority = "explicit"

[tool.poetry-yet-another-monorepo-plugin]
projects-dir = "projects"
projects-inherit-repos = false
exclude-projects = []

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"    
""")


def create_project_pyproject(name: str) -> str:
    return PROJECT_PYPROJECT_TEMPLATE.replace("{{PROJECT-NAME}}", name).replace(
        "{{PROJECT-VERSION}}", DEFAULT_PROJ_VERSION
    )


def create_project_structure(fakefs: FakeFilesystem, projects_root: Path, name: str):
    proj_root = projects_root / f"proj-{name}"
    proj_src = proj_root / f"proj_{name}"
    proj_pyproject_path = proj_root / "pyproject.toml"
    proj_pyproject_content = create_project_pyproject(name)
    fakefs.create_dir(proj_root)
    fakefs.create_dir(proj_src)
    fakefs.create_file(proj_src / "__init__.py")
    fakefs.create_file(proj_pyproject_path, contents=proj_pyproject_content)


@pytest.fixture
def fake_repos_fs(fs: FakeFilesystem):
    fakefs = fs
    if not fakefs:
        raise RuntimeError("Failed to get FakeFS.")

    # setup the fake filesystem using standard functions
    root = Path("/", "test-cases", REPO_NAME)
    root.mkdir(parents=True)

    fakefs.create_file(root / "pyproject.toml", contents=ROOT_PYPROJECT_CONTENT)
    projects_root = root / PROJECTS_DIR
    fakefs.create_dir(projects_root)

    for name in PROJECT_NAMES:
        create_project_structure(fakefs, projects_root, name)

    fs.add_real_paths(
        [
            str(Path(Path(__file__).parent.parent, ".venv")),
        ],
        read_only=True,
        lazy_dir_read=True,
    )

    return fs


@pytest.fixture
def poetry_factory(fake_repos_fs) -> Callable[[str], tuple[Poetry, FakeFilesystem]]:
    def factory(name: str) -> tuple[Poetry, FakeFilesystem]:
        return Factory().create_poetry(cwd=Path(TEST_REPOS_ROOT, name)), fake_repos_fs

    return factory
