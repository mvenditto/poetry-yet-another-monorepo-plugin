from dataclasses import dataclass, field


@dataclass(frozen=True)
class YampConfig:
    projects_dir: str = "src"

    exclude_projects: list[str] = field(default_factory=list)
    """If a project name matches any of the patterns, it gets excluded."""
