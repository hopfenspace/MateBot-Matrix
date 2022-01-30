"""
MateBot command executor for send
"""

from hopfenmatrix.matrix import MatrixRoom, RoomMessageText
from matebot_sdk.exceptions import UserAPIException

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.util import Namespace
from ..parsing.types import amount as amount_type, user as user_type


class SendCommand(BaseCommand):
    """
    Command executor for send
    """

    def __init__(self):
        super().__init__(
            "send",
            "Use this command to send money to another user.\n\n"
            "Performing this command allows you to send money to someone else. "
            "Obviously, the receiver of your transaction has to be registered with "
            "this bot. For security purposes, the bot will ask you to confirm your "
            "proposed transaction before the virtual money will be transferred.\n\n"
            "The first and second argument, amount and receiver respectively, are "
            "mandatory. But you can add as many extra words as you want afterwards. "
            "Those are treated as description/reason for your transaction.",
            "Use this command to send money to another user.<br /><br />"
            "Performing this command allows you to send money to someone else. "
            "Obviously, the receiver of your transaction has to be registered with "
            "this bot. For security purposes, the bot will ask you to confirm your "
            "proposed transaction before the virtual money will be transferred.<br /><br />"
            "The first and second argument, <code>amount</code> and <code>receiver</code> respectively, are "
            "mandatory. But you can add as many extra words as you want afterwards. "
            "Those are treated as description/reason for your transaction."
        )

        self.parser.add_argument("amount", type=amount_type)
        self.parser.add_argument("receiver", type=user_type)
        self.parser.add_argument("reason", default="<no description>", nargs="*")

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        sender = await bot.sdk.get_user_by_app_alias(event.sender)

        self.logger.debug(args.receiver)
        if not args.receiver:
            self.logger.warning("No receiver!")
            return

        if isinstance(args.reason, list):
            reason = "send: " + " ".join(map(str, args.reason))
        else:
            reason = "send: " + str(args.reason)

        try:
            transaction = await bot.sdk.make_new_transaction(sender, args.receiver, args.amount, reason)
            await bot.send_reply(
                f"Okay, you sent {transaction.amount / 100 :.2f}€ to {bot.sdk.get_username(args.receiver)}",
                room.room_id,
                event
            )
        except UserAPIException as exc:
            self.logger.warning(f"{type(exc).__name__}: {exc.message} ({exc.status}, {exc.details})")
            await bot.send_reply(
                f"Your request couldn't be processed. No money has been transferred:\n{exc.message}",
                room.room_id,
                event
            )
