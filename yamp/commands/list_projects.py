from poetry.console.application import Application

from yamp.commands.base import YampBaseCommand
from yamp.utils import print_table


class ListProjectsCommand(YampBaseCommand):
    name = "list-projects"

    def __init__(self, application: Application):
        super().__init__(application)

    def handle(self) -> int:
        super().handle()
        print_table(
            self,
            {
                "Working Directory": self.monorepo.workdir,
                "Source Directory": self.monorepo.projects_dir,
                "Projects": "",
            },
        )

        for p in self.monorepo.projects.values():
            rel_path = p.pyproject.path.relative_to(self.monorepo.workdir)
            self.line(f"  - <comment>{rel_path} ({p.version})</comment>")

        return 0
