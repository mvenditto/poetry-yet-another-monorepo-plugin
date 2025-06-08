from cleo.io.inputs.option import Option
from poetry.console.application import Application
from poetry.console.commands.build import BuildCommand, BuildHandler, BuildOptions
from poetry.core.constraints.version import Version
from poetry.factory import Factory
from poetry.utils.env import EnvManager

from yamp.commands.base import YampBaseCommand
from yamp.commands.set_projects_version import SetProjectsVersionHandler


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

        targets = self.monorepo.projects.values()

        dry_run = self.is_dryrun()

        for proj in targets:
            self.line(f"  - <comment>{proj.pyproject.path.parent}</comment>")

        exit_codes = []

        raw_version = self.monorepo.get_command_version(self)

        if not raw_version:
            self.line_error("Failed to extract a valid version.")
            return -2

        version = Version.parse(raw_version)

        self.line("")
        self.line(f"Pinning to <c1>version</c1> => <c2>{version}</c2>")

        for proj in targets:
            self.line("")
            poetry = proj.poetry
            self.monorepo.prepare_project(proj)

            with proj.package_version_override(version):
                env = EnvManager(poetry, io=self.io).get()
                self.line(f"Target <c1>{proj.pyproject.path.parent}</c1>")

                build_handler = BuildHandler(
                    poetry=poetry,
                    env=env,  # type: ignore
                    io=self.io,
                )

                build_options = BuildOptions(
                    clean=self.option("clean"),
                    formats=self._prepare_formats(self.option("format")),  # type: ignore[arg-type]
                    output=self.option("output"),
                    config_settings=self._prepare_config_settings(
                        local_version=self.option("local-version"),
                        config_settings=self.option("config-settings"),
                        io=self.io,
                    ),
                )

                exit_code = build_handler.build(options=build_options)

            self.line(f"Completed with <c1>exit-code</c1>: <c2>{exit_code}</c2>")

            exit_codes.append(exit_code)

        if all([x == 0 for x in exit_codes]):
            if self.option("sync-versions"):
                self.line("")
                self.line(f"Syncing to <c1>version</c1> => <c2>{version}</c2>")

                sync_versions_handler = SetProjectsVersionHandler(
                    new_version=raw_version,
                    monorepo=self.monorepo,
                    logger=self.logger,
                    io=self.io,
                    dry_run=dry_run,
                )
                return sync_versions_handler.handle()
            return 0

        return -1
