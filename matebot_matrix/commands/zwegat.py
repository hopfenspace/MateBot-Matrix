"""
MateBot command executor for zwegat
"""

from matebot_sdk.base import PermissionLevel
from hopfenmatrix.matrix import MatrixRoom, RoomMessageText

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.util import Namespace


class ZwegatCommand(BaseCommand):
    """
    Command executor for zwegat
    """

    def __init__(self):
        super().__init__(
            "zwegat",
            "Use this command to show the central funds.<br/>"
            "This command can only be used by internal users.",
        )

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        user = await bot.sdk.get_user_by_app_alias(event.sender)

        check = bot.sdk.ensure_permissions(user, PermissionLevel.ANY_INTERNAL, "zwegat")
        if not check[0]:
            await bot.reply(check[1], room, event)
            return

        total = (await bot.sdk.get_community_user()).balance / 100
        if total >= 0:
            msg = f"Peter errechnet ein massives Vermögen von {total:.2f}€"
        else:
            msg = f"Peter errechnet Gesamtschulden von {-total:.2f}€"
        await bot.reply(msg, room, event)
