from logging import Logger, getLogger

from cleo.io.inputs.option import Option
from cleo.io.io import IO
from poetry.console.application import Application

from yamp.commands.base import YampBaseCommand
from yamp.monorepo import YampMonorepo
from yamp.utils import try_set_project_key


class SetProjectsVersionHandler:
    def __init__(
        self,
        new_version: str,
        monorepo: YampMonorepo,
        io: IO,
        dry_run: bool = False,
        logger: Logger | None = None,
    ):
        self.logger = logger or getLogger(str(None))
        self.io = io
        self.new_version = new_version
        self.monorepo = monorepo
        self.dry_run = dry_run

    def handle(self) -> int:
        new_version = self.new_version

        self.io.write_line(f"<info>Target Version</info>: {new_version}<comment></comment>")

        self.io.write_line("<info>Set Versions:</info>")

        for proj_name, proj in self.monorepo.projects.items():
            old_version = proj.version
            self.io.write_line(
                f"  - <info>{proj_name}</info>: {old_version} => <comment>{new_version}</comment>"
            )

            if self.dry_run:
                self.logger.debug("SKIP '%s': dry-run enabled.", proj_name)
                continue

            if try_set_project_key(proj.pyproject, "version", new_version):
                proj.pyproject.save()
            else:
                self.io.write_error_line(f"Failed to set version for: {proj_name}")
        return 0


class SetProjectsVersionCommand(YampBaseCommand):
    name = "set-projects-version"

    def __init__(self, application: Application):
        super().__init__(application)

    def configure(self):
        self.options.append(
            Option(
                name="--version-override",
                flag=False,
                requires_value=True,
                description="If provided, overrides the version from the root pyproject.toml",
            )
        )
        super().configure()

    def handle(self) -> int:
        super().handle()

        dry_run = self.is_dryrun()

        new_version = self.monorepo.get_command_version(command=self)

        if not new_version:
            self.line_error("Cannot retrieve monorepo version.")
            return -1

        handler = SetProjectsVersionHandler(
            new_version=new_version,
            monorepo=self.monorepo,
            io=self.io,
            dry_run=dry_run,
            logger=self.logger,
        )

        return handler.handle()
