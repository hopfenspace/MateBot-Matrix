import asyncio
import inspect
import logging
import threading
import collections
from typing import Awaitable, Callable, Dict, List, Optional, Tuple

from aiohttp import web
from matebot_sdk.base import CallbackUpdate

from .bot import MateBot


ASYNC_SLEEP_DURATION: float = 0.5
CALLBACK_TYPE = Callable[[CallbackUpdate, str, int, MateBot, logging.Logger, ...], Optional[Awaitable[None]]]
STORAGE_TYPE = Dict[
    Tuple[CallbackUpdate, Optional[str]],
    List[Tuple[CALLBACK_TYPE, tuple, dict]]
]


class APICallbackDispatcher:
    def __init__(self, bot: MateBot):
        self.bot = bot
        self.logger = logging.getLogger("callback")
        self._storage: STORAGE_TYPE = collections.defaultdict(list)

        self.event_thread: Optional[threading.Thread] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.event_thread_running: threading.Event = threading.Event()
        self.event_thread_started: threading.Event = threading.Event()

    def register(self, event: Tuple[CallbackUpdate, Optional[str]], func: CALLBACK_TYPE, *args, **kwargs):
        self._storage[event].append((func, args, kwargs))

    def dispatch(self, method: CallbackUpdate, model: str, model_id: int):
        for event in self._storage:
            if event[0] == method and (event[1] is None or event[1] == model):
                for handler in self._storage.get(event):
                    func, args, kwargs = handler
                    try:
                        result = func(method, model, model_id, self.bot, self.logger, *args, **kwargs)
                        if result is not None:
                            if not inspect.isawaitable(result):
                                raise TypeError(
                                    f"{func} should return Optional[Awaitable[None]], but got {type(result)}"
                                )
                            asyncio.run_coroutine_threadsafe(result, loop=self.bot.loop).result()
                    except Exception as exc:
                        self.logger.warning(f"{type(exc).__name__} in API callback handler for event {event}")
                        raise

    async def run_async(self, app: web.Application, host: str, port: int):
        self.event_loop = asyncio.get_event_loop()
        self.logger.debug(f"Event loop {self.event_loop} of {threading.current_thread()} has been attached to {self}")
        self.event_thread_started.set()

        self.logger.debug("Starting callback server...")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        self.logger.debug(f"Sleeping until {self.event_thread_running} gets set...")
        while not self.event_thread_running.is_set():
            await asyncio.sleep(ASYNC_SLEEP_DURATION)

        self.logger.debug("Stopping callback server...")
        await site.stop()
        self.logger.debug(f"Closing async runner thread {threading.current_thread()}...")

    def start_async_thread(self, app: web.Application, host: str, port: int, daemon: bool = True, name: str = None):
        if self.event_thread is not None:
            raise RuntimeError("Server thread already running")
        self.event_thread = threading.Thread(
            target=lambda: asyncio.run(self.run_async(app, host, port)),
            name=name,
            daemon=daemon
        )
        self.event_thread.start()
        self.logger.info("Started callback server thread")


def get_callback_app(dispatcher: APICallbackDispatcher, logger: logging.Logger):
    async def process(request: web.Request) -> web.Response:
        methods = {
            "create": CallbackUpdate.CREATE,
            "update": CallbackUpdate.UPDATE,
            "delete": CallbackUpdate.DELETE
        }
        action = str(request.match_info["operation"]).lower()
        model = str(request.match_info["model"]).lower()
        model_id = int(request.match_info["model_id"])
        logger.debug(f"Incoming callback query: '{action.upper()} {model} {model_id}'")
        dispatcher.dispatch(methods[action], model, model_id)
        return web.Response()

    app = web.Application()
    app.add_routes([web.get(r"/{operation}/{model}/{model_id:\d+}", process)])
    return app
