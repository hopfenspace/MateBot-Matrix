import logging

from .bot import MateBot
from .commands import COMMANDS
from .callback import APICallbackDispatcher, get_callback_app


def main():
    bot = MateBot()
    bot.set_auto_join()

    # TODO: integrate specific log level adjustments in the configuration
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    for name in COMMANDS:
        cmd = COMMANDS[name]
        if name == "help":
            bot.register_command(cmd, name, description=cmd.description, command_syntax=cmd.usage, make_default=True)
        else:
            bot.register_command(cmd, name, description=cmd.description, command_syntax=cmd.usage)

    dispatcher = APICallbackDispatcher(bot)
    app = get_callback_app(dispatcher, logging.getLogger("callback"))
    if bot.config.api.callback.username or bot.config.api.callback.password:
        bot.logger.warning("Username & password authentication for callbacks is not supported yet!")
    dispatcher.start_async_thread(app, bot.config.api.callback.address, bot.config.api.callback.port)
    bot.run()


if __name__ == "__main__":
    main()
