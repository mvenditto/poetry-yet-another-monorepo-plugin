from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.poetry import Poetry

from yamp.commands.factory import command_factory


class YampPlugin(ApplicationPlugin):
    def __init__(self):
        self.poetry: Poetry
        self.application: Application

    def _register_command(self, application: Application, command_name: str):
        application.command_loader.register_factory(
            command_name=command_name,
            factory=lambda: command_factory(command_name)(self.application),
        )

    def activate(self, application: Application):
        self.application = application

        self._register_command(application, "list-projects")
        self._register_command(application, "set-projects-version")
        self._register_command(application, "build-projects-pinned")

        self.poetry = application.poetry
