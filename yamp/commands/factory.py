from .build_projects_pinned import BuildProjectsPinnedCommand
from .list_projects import ListProjectsCommand
from .set_projects_version import SetProjectsVersionCommand


def command_factory(command_name: str):
    return {
        ListProjectsCommand.name: lambda app: ListProjectsCommand(app),
        SetProjectsVersionCommand.name: lambda app: SetProjectsVersionCommand(app),
        BuildProjectsPinnedCommand.name: lambda app: BuildProjectsPinnedCommand(app),
    }[command_name]
