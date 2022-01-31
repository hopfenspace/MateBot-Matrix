import asyncio
import inspect
import logging
import collections
from typing import Awaitable, Callable, Dict, List, Optional, Tuple

from matebot_sdk.base import CallbackUpdate

from .bot import MateBot


CALLBACK_TYPE = Callable[[CallbackUpdate, str, int, MateBot, logging.Logger, ...], Optional[Awaitable[None]]]
STORAGE_TYPE = Dict[
    Tuple[CallbackUpdate, Optional[str]],
    List[Tuple[CALLBACK_TYPE, tuple, dict]]
]


class APICallbackDispatcher:
    def __init__(self, bot: MateBot):
        self.bot = bot
        self.logger = logging.getLogger("api-callback")
        self._storage: STORAGE_TYPE = collections.defaultdict(list)

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
