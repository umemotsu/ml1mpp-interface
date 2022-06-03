import collections
import datetime

import click
from flask.cli import AppGroup


class Echo:
    @staticmethod
    def debug(msg):
        Echo._echo(msg, level="debug", fg="black")

    @staticmethod
    def info(msg):
        Echo._echo(msg, level="info", fg="green")

    @staticmethod
    def warning(msg):
        Echo._echo(msg, level="warning", fg="yellow")

    @staticmethod
    def error(msg):
        Echo._echo(msg, level="error", fg="magenta")

    @staticmethod
    def critical(msg):
        Echo._echo(msg, level="critical", fg="red")

    @staticmethod
    def _echo(msg, level, **kwargs):
        now = datetime.datetime.now().strftime("%m/%d %H:%M")
        msg = f"[{now}][{level:>8}] {msg}"

        click.secho(msg, **kwargs)


class OrderedAppGroup(AppGroup):
    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)

        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx):
        return self.commands

    def group(self, *args, **kwargs):
        kwargs.setdefault("cls", OrderedAppGroup)

        return super().group(*args, **kwargs)
