"""
MateBot command executor for history
"""

import json
import time
import tempfile

from matebot_sdk import schemas
from hopfenmatrix.matrix import MatrixRoom, RoomMessageText

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.types import natural as natural_type
from ..parsing.util import Namespace


class HistoryCommand(BaseCommand):
    """
    Command executor for history
    """

    def __init__(self):
        super().__init__(
            "history",
            "Use this command to get an overview of your transactions.<br/>"
            "You can specify the number of most recent transactions (by default "
            "<code>10</code>) which will be returned by the bot. Using a huge number will "
            "just print all your transactions.<br/>"
            "You may also export the whole history of your personal transactions as file "
            "to download. Currently supported formats are <code>csv</code> and <code>json</code>. "
            "Just add one of those two format specifiers after the command. Note "
            "that this variant is restricted to your personal chat with the bot."
        )

        self.parser.add_argument(
            "length",
            nargs="?",
            default=10,
            type=natural_type
        )
        self.parser.new_usage().add_argument(
            "export",
            nargs="?",
            type=lambda x: str(x).lower(),
            choices=("json", "csv")
        )

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        if args.export is None:
            await self._handle_report(args, bot, room, event)
        else:
            await self._handle_export(args, bot, room, event)

    @staticmethod
    async def _handle_export(args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        if len(room.users) > 2:
            await bot.reply("This command can only be used in private chat.", room, event)
            return

        user = await bot.sdk.get_user_by_app_alias(event.sender)
        transactions = await bot.sdk.get_transactions_of_user(user)

        if len(transactions) == 0:
            await bot.reply("You don't have any registered transactions yet.", room, event)
            return

        if args.export == "json":
            text = json.dumps([t.dict() for t in transactions], indent=2)

        else:  # args.export == "csv"
            await bot.reply("Exporting to CSV is currently not implemented.", room, event)
            # text = ";".join(logs[0].keys())
            # for log in logs:
            #     text += "\n" + ";".join(map(str, log.values()))
            return

        with tempfile.NamedTemporaryFile(mode="w+b") as file:
            file.write(text.encode("utf-8"))
            file.seek(0)

            await bot.send_file(file.name, room, description=f"transactions.{args.export}")

    @staticmethod
    async def _handle_report(args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        user = await bot.sdk.get_user_by_app_alias(event.sender)

        def format_transaction(transaction: schemas.Transaction) -> str:
            timestamp = time.strftime('%d.%m.%Y %H:%M', time.localtime(transaction.timestamp))
            direction = ["<<", ">>"][transaction.sender.id == user.id]
            partner = bot.sdk.get_username([transaction.sender, transaction.receiver][transaction.sender.id == user.id])
            amount = transaction.amount / 100
            if transaction.sender.id == user.id:
                amount = -amount
            return f"{timestamp}: {amount:>+7.2f}: me {direction} {partner:<16} :: {transaction.reason}"

        logs = [format_transaction(t) for t in await bot.sdk.get_transactions_of_user(user)][-args.length:]
        if len(logs) == 0:
            await bot.reply("You don't have any registered transactions yet.", room, event)
            return
        if len(logs) > 10 and len(room.users) > 2:
            await bot.reply(
                "Your requested transaction logs are too long. Try a smaller number of "
                "entries or execute this command in private chat again.", room, event
            )
            return

        log = "\n".join(logs)
        text = f"<i>Transaction history for {bot.sdk.get_username(user)}</i>:<br/>\n<pre>\n{log}\n</pre>\n"
        await bot.reply(text, room, event, send_as_notice=False)
