import logging
from functools import cached_property

from cleo.commands.command import Command
from cleo.formatters.style import Style
from cleo.io.inputs.option import Option
from poetry.console.application import Application

from yamp.monorepo import YampMonorepo


class YampBaseCommand(Command):
    name = "set-projects-version"

    def __init__(self, application: Application):
        super().__init__()
        self.root_application = application
        self.logger = logging.getLogger("yamp.command")

    @cached_property
    def monorepo(self) -> YampMonorepo:
        return YampMonorepo(self.root_application.poetry, io=self.io)

    def configure(self) -> None:
        self.options.append(
            Option(
                name="--dry-run",
                requires_value=False,
                flag=True,
                description="If appliable, no changes will be made.",
            )
        )
        super().configure()

    def _setup_styles(self):
        self.io.output.formatter.set_style("warning", Style("yellow"))
        self.io.output.formatter.set_style("warning-bold", Style("yellow", options=["bold"]))

    def _setup_logging(self):
        logger = logging.getLogger("yamp")

        null_logger = logging.getLogger(str(None))
        null_logger.handlers.clear()
        null_logger.propagate = False
        null_logger.addHandler(logging.NullHandler())

        level = logging.NOTSET

        if self.io.is_verbose():
            level = logging.WARNING

        if self.io.is_very_verbose():
            level = logging.INFO

        if self.io.is_debug():
            level = logging.DEBUG

        logger.setLevel(level)

        if self.io.output.is_quiet():
            logger.disabled = True

    def handle(self) -> int:
        self._setup_styles()
        self._setup_logging()
        return 0

    def is_dryrun(self, print_warning: bool = True) -> bool:
        dry_run = self.option("dry-run")

        if dry_run and print_warning:
            self.line(
                "<warning-bold>DRY-RUN</warning-bold>: <warning>no changes will be made!</warning>"
            )

        return dry_run
