from typing import Any

from cleo.commands.command import Command
from poetry.pyproject.toml import PyProjectTOML


def print_table(command: Command, data: dict[str, Any]):
    longest = max(len(k) for k in data.keys())
    for k, v in data.items():
        command.line(f"<info>{k:<{longest}}</info>: <comment>{v}</comment>")


def get_project_key(pyproject: PyProjectTOML, key: str):
    """Retrieves a key in the [project] or [tool.poetry] table.

    Remarks:
        If present, try to get the key from the [project] table
        otherwise fallback to the [poetry.tool] table for retro-compatibility.

    Raises:
      KeyError if 'key' is not present in either table.
    """
    data = pyproject.data

    if not data:
        raise ValueError("Failed to read pyproject.toml data.")

    project = data.get("project")

    if project:
        value = project.get(key)
        if value:
            return value

    poetry = data.get("tool", {}).get("poetry", {})

    if key not in poetry:
        raise KeyError(
            f"Neither 'project.{key}' nor 'tool.poetry.{key}' exists in {pyproject.path}"
        )

    return poetry[key]


def try_set_project_key(pyproject: PyProjectTOML, key: str, value: Any) -> bool:
    data = pyproject.data

    if not data:
        raise ValueError("Failed to read pyproject.toml data.")

    project = data.get("project")

    if project:
        project[key] = value
        return True

    tool = data.get("tool")

    if not tool or "poetry" not in tool:
        return False

    tool["poetry"][key] = value
    return True
