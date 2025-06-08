from logging import Logger, getLogger

from cleo.io.inputs.option import Option
from cleo.io.io import IO
from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand, BuildHandler, BuildOptions
from poetry.core.constraints.version import Version
from poetry.factory import Factory
from poetry.utils.env import EnvManager

from yamp.commands.base import YampBaseCommand
from yamp.commands.set_projects_version import SetProjectsVersionHandler
from yamp.monorepo import YampMonorepo


class BuildProjectsPinnedHandler:
    def __init__(
        self,
        raw_version: str,
        sync_versions: bool,
        monorepo: YampMonorepo,
        clean: bool,
        output: str,
        formats: list[str],
        dry_run: bool,
        config_settings: dict[str, str],
        io: IO,
        logger: Logger | None = None,
    ):
        self.raw_version = raw_version
        self.sync_versions = sync_versions
        self.clean = clean
        self.output = output
        self.formats = formats
        self.config_settings = config_settings
        self.logger = logger or getLogger(str(None))
        self.monorepo = monorepo
        self.dry_run = dry_run
        self.io = io

    def build(self) -> int:
        targets = self.monorepo.projects.values()

        for proj in targets:
            self.io.write_line(f"  - <comment>{proj.pyproject.path.parent}</comment>")

        exit_codes = []

        version = Version.parse(self.raw_version)

        self.io.write_line("")
        self.io.write_line(f"Pinning to <c1>version</c1> => <c2>{version}</c2>")

        for proj in targets:
            self.io.write_line("")
            poetry = proj.poetry
            self.monorepo.prepare_project(proj)

            with proj.package_version_override(version):
                env = EnvManager(poetry, io=self.io).get()
                self.io.write_line(f"Target <c1>{proj.pyproject.path.parent}</c1>")

                build_handler = BuildHandler(
                    poetry=poetry,
                    env=env,  # type: ignore
                    io=self.io,
                )

                build_options = BuildOptions(
                    clean=self.clean,
                    formats=self.formats,  # type: ignore[arg-type]
                    output=self.output,
                    config_settings=self.config_settings,
                )

                exit_code = build_handler.build(options=build_options)

            self.io.write_line(f"Completed with <c1>exit-code</c1>: <c2>{exit_code}</c2>")

            exit_codes.append(exit_code)

        if all([x == 0 for x in exit_codes]):
            if self.sync_versions:
                self.io.write_line("")
                self.io.write_line(f"Syncing to <c1>version</c1> => <c2>{version}</c2>")

                sync_versions_handler = SetProjectsVersionHandler(
                    new_version=self.raw_version,
                    monorepo=self.monorepo,
                    logger=self.logger,
                    io=self.io,
                    dry_run=self.dry_run,
                )
                return sync_versions_handler.handle()
            return 0

        return -1


class BuildProjectsPinnedCommand(YampBaseCommand, BuildCommand):
    name = "build-projects-pinned"

    def __init__(self, application: Application):
        super().__init__(application)
        self.factory = Factory()

    def configure(self) -> None:
        self.options.extend(
            [
                Option(
                    name="--version-override",
                    flag=False,
                    requires_value=True,
                    description="If provided, overrides the version from the root pyproject.toml",
                ),
                Option(
                    name="--sync-versions",
                    flag=True,
                    requires_value=False,
                    description="Sync the version of every project to the build version.",
                ),
            ]
        )
        super().configure()

    @staticmethod
    def _indent(s: str) -> str:
        return "\n  ".join(s.splitlines())

    def handle(self) -> int:
        YampBaseCommand.handle(self)

        self.line("<info>Building</info>: ")

        raw_version = self.monorepo.get_command_version(self)

        if not raw_version:
            self.line_error("Failed to extract a valid version.")
            return -2

        dry_run = self.is_dryrun()

        config_settings = self._prepare_config_settings(
            local_version=self.option("local-version"),
            config_settings=self.option("config-settings"),
            io=self.io,
        )

        handler = BuildProjectsPinnedHandler(
            raw_version=raw_version,
            sync_versions=self.option("sync-versions"),
            clean=self.option("clean"),
            output=self.option("output"),
            formats=self._prepare_formats(self.option("format")),
            config_settings=config_settings,
            monorepo=self.monorepo,
            io=self.io,
            dry_run=dry_run,
            logger=self.logger,
        )

        return handler.build()
