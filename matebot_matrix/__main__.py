import asyncio
import logging

from matebot_sdk.sdk import AsyncSDK
from hopfenmatrix.matrix import MatrixBot

from .config import MateBotConfig


async def _run(bot: MatrixBot, sdk: AsyncSDK):
    await sdk.setup()
    await bot.start_bot()


def main():
    bot = MatrixBot(config_class=MateBotConfig)
    bot.set_auto_join()
    sdk_config = bot.config.api
    sdk = AsyncSDK(
        base_url=sdk_config.base_url,
        app_name=sdk_config.app_name,
        password=sdk_config.app_password,
        ca_path=sdk_config.ca_path,
        configuration=bot.config.client,
        callback=(sdk_config.callback.public_url, sdk_config.callback.username, sdk_config.callback.password),
        logger=logging.getLogger("sdk.client")
    )
    asyncio.run(_run(bot, sdk))


if __name__ == "__main__":
    main()
