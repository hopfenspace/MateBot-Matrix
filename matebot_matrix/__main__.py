import logging

from .bot import MateBot
from .commands import COMMANDS, DEFAULT_COMMAND
from .callback import APICallbackDispatcher, get_callback_app


THREAD_JOIN_TIMEOUT: float = 1.0


def main():
    bot = MateBot()
    bot.set_auto_join()

    # TODO: integrate specific log level adjustments in the configuration
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    for name in COMMANDS:
        cmd = COMMANDS[name]
        bot.register_command(cmd, name, description=cmd.description, command_syntax=cmd.usage)
    bot.register_command(DEFAULT_COMMAND, "*", make_default=True)

    dispatcher = APICallbackDispatcher(bot)
    app = get_callback_app(dispatcher, logging.getLogger("callback"))
    if bot.config.api.callback.username or bot.config.api.callback.password:
        bot.logger.warning("Username & password authentication for callbacks is not supported yet!")
    dispatcher.start_async_thread(app, bot.config.api.callback.address, bot.config.api.callback.port)
    bot.run()
    dispatcher.event_thread_running.set()
    dispatcher.event_thread.join(THREAD_JOIN_TIMEOUT)


if __name__ == "__main__":
    main()