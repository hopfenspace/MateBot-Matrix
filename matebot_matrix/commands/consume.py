"""
MateBot command executor for consume
"""

import random as _random

from hopfenmatrix.matrix import MatrixRoom, RoomMessageText
from matebot_sdk.schemas import Consumable

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.util import Namespace
from ..parsing.types import natural as natural_type, extended_consumable_type


class ConsumeCommand(BaseCommand):
    """
    Command executor for consume
    """

    def __init__(self):
        super().__init__(
            "consume",
            "Use this command to consume consumable goods.<br/>"
            "The first argument <code>consumable</code> determines which good you want to consume, "
            "while the optional second argument <code>number</code> determines the number of "
            "consumed goods (defaulting to a single one). Use the special consumable "
            "<code>?</code> to get a list of the consumable goods currently available."
        )

        self.parser.add_argument("consumable", type=extended_consumable_type)
        self.parser.add_argument("number", default=1, type=natural_type, nargs="?")

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        sender = await bot.sdk.get_user_by_app_alias(event.sender)
        consumable = args.consumable

        if isinstance(consumable, str) and consumable == "?":
            lines = "".join([
                f"<li>{c.symbol} <b>{c.name}</b> (price: {c.price / 100:.2f}€, stock: {c.stock}): {c.description}</li>"
                if c.description else
                f"<li>{c.symbol} <b>{c.name}</b> (price: {c.price / 100:.2f}€, stock: {c.stock})</li>"
                for c in await bot.sdk.get_consumables()
            ])
            await bot.reply(f"The following consumables are currently available:<br/><ul>{lines}</ul>", room, event)

        elif isinstance(consumable, Consumable):
            await bot.sdk.consume(consumable, args.number, sender)
            msg = _random.choice(consumable.messages) + consumable.symbol * args.number
            await bot.reply(msg, room, event)

        else:
            raise RuntimeError(f"Invalid consumable: {consumable!r} {type(consumable)}")
