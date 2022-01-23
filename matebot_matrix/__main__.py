import asyncio

from .bot import MateBot


def main():
    bot = MateBot()
    bot.set_auto_join()
    asyncio.run(bot.start_bot())


if __name__ == "__main__":
    main()
