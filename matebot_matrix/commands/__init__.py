"""
Collection of command executors
"""

from .balance import BalanceCommand


COMMANDS = {
    cmd.name: cmd for cmd in [
        BalanceCommand()
    ]
}

__all__ = ["COMMANDS"]
