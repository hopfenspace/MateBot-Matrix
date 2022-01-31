"""
Collection of command executors
"""

from .balance import BalanceCommand
from .help import HelpCommand
from .start import StartCommand


COMMANDS = {
    cmd.name: cmd for cmd in [
        BalanceCommand(),
        HelpCommand(),
        StartCommand()
    ]
}

__all__ = ["COMMANDS"]
