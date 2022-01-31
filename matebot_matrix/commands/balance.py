"""
MateBot command executor for balance
"""

from hopfenmatrix.matrix import MatrixRoom, RoomMessageText

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.types import user as user_type
from ..parsing.util import Namespace


class BalanceCommand(BaseCommand):
    """
    Command executor for balance
    """

    def __init__(self):
        super().__init__(
            "balance",
            "Use this command to show a user's balance.<br/>"
            "When you use this command without arguments, the bot will "
            "reply with your current amount of money stored in your virtual "
            "wallet. If you specify a username or mention someone as an argument, "
            "the balance of this user is returned instead of yours.",
        )

        self.parser.add_argument("user", type=user_type, nargs="?")

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        if args.user:
            msg = f"Balance of {bot.sdk.get_username(args.user)} is: {args.user.balance / 100 : .2f}€"
        else:
            user = await bot.sdk.get_user_by_app_alias(event.sender)
            msg = f"Your balance is: {user.balance / 100 :.2f}€"

        await bot.reply(msg, room, event)
