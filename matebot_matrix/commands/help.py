"""
MateBot command executor for help
"""

from hopfenmatrix.callbacks import CommandCallback
from hopfenmatrix.matrix import MatrixRoom, RoomMessageText
from matebot_sdk.exceptions import UserAPIException

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.util import Namespace
from ..parsing.types import command as command_type, string


class HelpCommand(BaseCommand):
    """
    Command executor for help
    """

    def __init__(self):
        super().__init__(
            "help",
            "The <code>help</code> command prints the help page for any "
            "command. If no argument is passed, it will print its "
            "usage and a list of all available commands."
        )

        self.parser.add_argument("command", type=command_type, nargs="?")
        self.parser.add_argument("catchall", type=string, nargs="*", metavar="text")

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        if args.command:
            usages = "<br/>".join(map(
                lambda usage: f"<code>{bot.config.matrix.command_prefix} {args.command.name} {usage}</code>",
                args.command.parser.usages
            ))
            msg = f"Help on command <b>{args.command.name}</b><br/><br/><em>Usages:</em><br/>{usages}" \
                  f"<br/><br/><em>Description:</em><br/>{args.command.description}<br/>"

        else:
            try:
                user = await bot.sdk.get_user_by_app_alias(event.sender)
            except UserAPIException:
                user = None

            def get_name(cmd: CommandCallback) -> str:
                if isinstance(cmd.accepted_aliases, str):
                    return f"<b>{cmd.accepted_aliases}</b>"
                return f"<b>{', '.join(cmd.accepted_aliases)}</b>"

            def get_syntax(cmd: CommandCallback) -> str:
                # TODO: add support for commands with multiple usages
                return (cmd.command_syntax or "") and f"<code>{cmd.command_syntax}</code>"

            commands = [
                f"<li>{get_name(command)}:<br/>{get_syntax(command)}<br/>{command.description}</li>"
                for command in bot.command_callbacks
                if command.accepted_aliases != "*"
            ]

            msg = f"{bot.config.matrix.bot_description}<br/><br/><code>{self.usage}</code><br/>" \
                  f"<br/><em>List of commands:</em><br/><ul>{''.join(commands)}</ul>"

            if user:
                if user.external:
                    msg += "<br/>You are an external user. Some commands may be restricted."

                    if user.creditor is None:
                        msg += (
                            "<br/>You don't have any creditor. Your possible interactions "
                            "with the bot are very limited for security purposes. You "
                            "can ask some internal user to act as your voucher. To "
                            "do this, the internal user needs to execute <code>vouch add "
                            "{your username}</code>. Afterwards, you may use this bot."
                        )

            else:
                msg += "<br/><b>You are currently not registered.</b><br/>Please see the " \
                       "help page of the <code>start</code> command to see how you register yourself."

        await bot.reply(msg, room, event)
