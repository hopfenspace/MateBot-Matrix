from .bot import MateBot
from .commands import COMMANDS


def main():
    bot = MateBot()
    bot.set_auto_join()

    for name in COMMANDS:
        cmd = COMMANDS[name]
        bot.register_command(cmd, name, description=cmd.description, command_syntax=cmd.usage)

    bot.run()


if __name__ == "__main__":
    main()
