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
            "Use this command to send money to another user.<br/>"
            "The receiver of your transaction has to be registered with this bot, too. "
            "<b>The bot won't ask for confirmation</b>, so be sure to enter the right values.<br/>"
            "The first and second argument, <code>amount</code> and <code>receiver</code> "
            "respectively, are mandatory. But you can add as many extra words as you want "
            "after those two arguments to specify a description/reason for your transaction."
        )

        self.parser.add_argument("amount", type=amount_type)
        self.parser.add_argument("receiver", type=user_type)
        self.parser.add_argument("reason", default="<no description>", nargs="*")

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        sender = await bot.sdk.get_user_by_app_alias(event.sender)

        if isinstance(args.reason, list):
            reason = "send: " + " ".join(map(str, args.reason))
        else:
            reason = "send: " + str(args.reason)

        try:
            transaction = await bot.sdk.make_new_transaction(sender, args.receiver, args.amount, reason)
            await bot.reply(
                f"<i>Okay, you sent {transaction.amount / 100 :.2f}€ to {bot.sdk.get_username(args.receiver)}</i>",
                room,
                event
            )
        except UserAPIException as exc:
            self.logger.warning(f"{type(exc).__name__}: {exc.message} ({exc.status}, {exc.details})")
            await bot.reply(
                f"<b>Your request couldn't be processed. No money has been transferred</b>:<br/><i>{exc.message}</i>",
                room,
                event,
                send_as_notice=False
            )
