import asyncio

from .bot import MateBot
from .commands import COMMANDS


def main():
    bot = MateBot()
    bot.set_auto_join()

    for cmd in COMMANDS:
        bot.register_command(cmd, cmd.name, description=cmd.description, command_syntax=cmd.usage)

    asyncio.run(bot.start_bot())


if __name__ == "__main__":
    main()
