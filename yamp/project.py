from pathlib import Path

from poetry.pyproject.toml import PyProjectTOML

from yamp.utils import get_project_key


class YampProject:
    def __init__(self, path: Path):
        self.pyproject = PyProjectTOML(path)

    @property
    def version(self) -> str:
        return get_project_key(self.pyproject, "version")  # type: ignore
