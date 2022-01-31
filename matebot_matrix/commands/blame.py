"""
MateBot command executor for blame
"""

from matebot_sdk.base import PermissionLevel
from hopfenmatrix.matrix import MatrixRoom, RoomMessageText

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.util import Namespace


class BlameCommand(BaseCommand):
    """
    Command executor for blame
    """

    def __init__(self):
        super().__init__(
            "blame",
            "Use this command to show the user(s) with the highest debts.<br/>"
            "Put the user(s) with the highest debts to the pillory and make them "
            "settle their debts, e.g. by buying stuff like new bottle crates. "
            "This command can only be executed by internal users."
        )

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        sender = await bot.sdk.get_user_by_app_alias(event.sender)

        check = bot.sdk.ensure_permissions(sender, PermissionLevel.ANY_INTERNAL, "blame")
        if not check[0]:
            await bot.reply(check[1], room, event)
            return

        users = await bot.sdk.get_users()
        min_balance = min(users, key=lambda u: u.balance).balance
        debtors = [user for user in users if user.balance <= min_balance and user.balance < 0]
        if len(debtors) == 0:
            msg = "Good news! No one has to be blamed, all users have positive balances!"
        elif len(debtors) == 1:
            msg = f"The user with the highest debt is:<br/>{bot.sdk.get_username(debtors[0])}"
        else:
            msg = f"The users with the highest debts are:<br/>{', '.join(map(bot.sdk.get_username, debtors))}"

        await bot.reply(msg, room, event)
