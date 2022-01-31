"""
Default MateBot command executor for any message that wasn't recognized as command
"""

from hopfenmatrix.matrix import MatrixRoom, RoomMessageText

from ..bot import MateBot


class DefaultCommand:
    """
    Command executor for any message that wasn't recognized
    """

    async def __call__(self, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        await bot.reply("<i>The default command is not implemented yet.</i>", room, event)
