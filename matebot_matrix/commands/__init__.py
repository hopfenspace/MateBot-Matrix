"""
Collection of command executors
"""

from .balance import BalanceCommand
from .consume import ConsumeCommand
from .default import DefaultCommand
from .help import HelpCommand
from .start import StartCommand


COMMANDS = {
    cmd.name: cmd for cmd in [
        BalanceCommand(),
        ConsumeCommand(),
        HelpCommand(),
        StartCommand()
    ]
}

DEFAULT_COMMAND = DefaultCommand()

__all__ = ["COMMANDS", "DEFAULT_COMMAND"]
