from dataclasses import dataclass, field


@dataclass(frozen=True)
class YampConfig:
    projects_dir: str = "src"
    """The directory where projects are located."""

    projects_inherit_repos: bool = field(default=False)
    """If True projects inherit repositories defined in the root pyproject.toml."""

    exclude_projects: list[str] = field(default_factory=list)
    """If a project name matches any of the patterns, it gets excluded."""
