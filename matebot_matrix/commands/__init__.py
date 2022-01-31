"""
Collection of command executors
"""

from .balance import BalanceCommand
from .blame import BlameCommand
from .consume import ConsumeCommand
from .data import DataCommand
from .default import DefaultCommand
from .help import HelpCommand
from .send import SendCommand
from .start import StartCommand


COMMANDS = {
    cmd.name: cmd for cmd in [
        BalanceCommand(),
        BlameCommand(),
        ConsumeCommand(),
        DataCommand(),
        HelpCommand(),
        SendCommand(),
        StartCommand()
    ]
}

DEFAULT_COMMAND = DefaultCommand()

__all__ = ["COMMANDS", "DEFAULT_COMMAND"]
