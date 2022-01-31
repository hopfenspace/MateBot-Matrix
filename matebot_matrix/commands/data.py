"""
MateBot command executor for data
"""

import time

from hopfenmatrix.matrix import MatrixRoom, RoomMessageText

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.util import Namespace


class DataCommand(BaseCommand):
    """
    Command executor for data
    """

    def __init__(self):
        super().__init__(
            "data",
            "Use this command to get an overview of the data the bot has stored about you.<br/>"
            "This command can only be used in private chat to protect private data. "
            "To view your transactions, use the command <code>history</code> instead."
        )

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        if len(room.users) > 2:
            await bot.reply("This command can only be used in private chat.", room, event)
            return

        user = await bot.sdk.get_user_by_app_alias(event.sender)

        if user.external:
            relations = "Voucher user: None"
            if user.voucher_id is not None:
                voucher = await bot.sdk.get_user_by_id(user.voucher_id)
                relations = f"Voucher user: {bot.sdk.get_username(voucher)}"

        else:
            all_users = await bot.sdk.get_users()
            debtors = [bot.sdk.get_username(u) for u in all_users if u.voucher_id == user.id]
            relations = f"Debtor user{'s' if len(debtors) != 1 else ''}: {', '.join(debtors) or 'None'}"

        app = await bot.sdk.application
        apps = await bot.sdk.get_applications()
        other_aliases = [
            f'{a.app_username}@{[c for c in apps if c.id == a.application_id][0].name}'
            for a in user.aliases if a.application_id != app.id
        ]
        votes = await bot.sdk.get_votes()
        my_votes = [v for v in votes if v.user_id == user.id]
        created_communisms = await bot.sdk.get_communisms_by_creator(user)
        created_refunds = await bot.sdk.get_refunds_by_creator(user)
        open_created_communisms = [c for c in created_communisms if c.active]
        open_created_refunds = [r for r in created_refunds if r.active]

        result = (
            f"<i>Overview over currently stored data for {user.name}</i>:<br/><br/>\n<pre>\n"
            f"User ID: {user.id}\n"
            f"Matrix ID: {event.sender}\n"
            f"This room: {room.room_id}\n"
            f"Username: {user.name}\n"
            f"Balance: {user.balance / 100 :.2f}€\n"
            f"Permissions: {user.permission}\n"
            f"External user: {user.external}\n"
            f"{relations}\n"
            f"Created communisms: {len(created_communisms)} ({len(open_created_communisms)} open)\n"
            f"Created refunds: {len(created_refunds)} ({len(open_created_refunds)} open)\n"
            f"Votes in polls: {len(my_votes)}\n"
            f"Account created: {time.asctime(time.localtime(user.created))}\n"
            f"Last transaction: {time.asctime(time.localtime(user.accessed))}\n"
            f"App aliases: {', '.join([f'{a.app_username}' for a in user.aliases if a.application_id == app.id])}\n"
            f"Other aliases: {', '.join(other_aliases) or 'None'}"
            f"\n</pre>\n\nUse the <code>history</code> command to see your transaction log."
        )

        await bot.reply(result, room, event, send_as_notice=False)
