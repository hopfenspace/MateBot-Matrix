"""
Collection of command executors
"""

from .balance import BalanceCommand
from .consume import ConsumeCommand
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

__all__ = ["COMMANDS"]
