import asyncio
import logging

from .bot import MateBot
from .commands import COMMANDS


def main():
    logger = logging.getLogger(__name__)
    bot = MateBot()
    logger.debug("Starting bot...")
    bot.set_auto_join()

    print("commands =", COMMANDS)
    for cmd in COMMANDS:
        bot.register_command(COMMANDS[cmd], cmd, description=COMMANDS[cmd].description, command_syntax=COMMANDS[cmd].usage)

    try:
        asyncio.run(bot.start_bot())
    except KeyboardInterrupt:
        pass
    logger.debug("Exiting gracefully.")


if __name__ == "__main__":
    main()
