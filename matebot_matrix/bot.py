import logging
from typing import Optional, Type

from matebot_sdk.sdk import AsyncSDK
from hopfenmatrix.config import Config
from hopfenmatrix.matrix import MatrixBot

from .config import MateBotConfig


class MateBot(MatrixBot):
    def __init__(
            self,
            *,
            display_name: str = None,
            enable_initial_info: bool = False,
            config: Optional[Config] = None,
            config_path: str = "config.json",
            config_class: Type[Config] = MateBotConfig
    ):
        super().__init__(
            display_name=display_name,
            enable_initial_info=enable_initial_info,
            config=config,
            config_path=config_path,
            config_class=config_class
        )

        self.logger = logging.getLogger("bot")
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.sdk = AsyncSDK(
            base_url=self.config.api.base_url,
            app_name=self.config.api.app_name,
            password=self.config.api.app_password,
            ca_path=self.config.api.ca_path,
            configuration=self.config.client,
            callback=(
                self.config.api.callback.public_url,
                self.config.api.callback.username,
                self.config.api.callback.password
            ),
            logger=logging.getLogger("sdk")
        )

    def run(self):
        async def _run():
            self.loop = asyncio.get_event_loop()
            await self.sdk.setup()
            await self.start_bot()
            await self.sdk.close()

        self.logger.info("Starting bot...")
        try:
            asyncio.run(_run())
        except KeyboardInterrupt:
            pass
        self.logger.info("Stopped bot.")
