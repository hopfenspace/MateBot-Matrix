"""
MateBot command executor for start
"""

from hopfenmatrix.matrix import MatrixRoom, RoomMessageText

from .base import BaseCommand
from ..bot import MateBot
from ..parsing.util import Namespace
from ..parsing.types import string, lowercase


class StartCommand(BaseCommand):
    """
    Command executor for start
    """

    def __init__(self):
        super().__init__(
            "start",
            "Use this command once per user to start interacting with this bot.<br/>"
            "This command creates your user account in case you haven't used the bot in this "
            "app yet. Otherwise, this command might not be pretty useful.<br/>"
            "You may either use <code>start new [username]</code> to create a fresh user account "
            "with zero balance and no permissions, using the given optional username (setting "
            "a username is highly recommended). If you used the MateBot in some other application "
            "before, you should use <code>start existing {alias}</code> instead (where the alias "
            "should be copied from the other application to connect your accounts successfully). "
            "Note that you have to accept the newly connected link in the other application "
            "before it will be enabled for security purposes. The alias can typically "
            "be found in the output of the <code>data</code> command.<br/>"
            "Use <code>help</code> for more information about how to use this bot and its commands."
        )

        self.parser.add_argument("new", type=lowercase, choices=("new",))
        self.parser.add_argument("username", nargs="?", type=string, metavar="username")
        existing = self.parser.new_usage()
        existing.add_argument("existing", type=lowercase, choices=("existing",))
        existing.add_argument("alias", type=string, nargs=1, metavar="alias")

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        await bot.reply("This command is not yet implemented. Stay tuned.", room, event)
