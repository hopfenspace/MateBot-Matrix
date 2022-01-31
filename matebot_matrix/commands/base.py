"""
MateBot command handling base library
"""

import logging
from typing import Optional

from hopfenmatrix.matrix import MatrixRoom, RoomMessageText
from matebot_sdk.exceptions import APIException, APIConnectionException, UserAPIException

from ..bot import MateBot
from ..err import ParsingError
from ..parsing.util import Namespace
from ..parsing.parser import CommandParser


class BaseCommand:
    """
    Base class for all MateBot commands executed by the CommandHandler

    It handles argument parsing and exception catching. Some specific
    implementation should be a subclass of this class. It must add
    arguments to the parser in the constructor and overwrite the run method.

    A minimal working example class may look like this:

    .. code-block::

        class ExampleCommand(BaseCommand):
            def __init__(self):
                super().__init__("example", "Example command")
                self.parser.add_argument("number", type=int)

            async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
                await bot.reply("<br/>".join(["Example!"] * max(1, args.number)), room, event)

    :param name: name of the command (without the bot prefix)
    :type name: str
    :param description: a multiline string describing what the command does, formatted with HTML
    :type description: str
    :param usage: an optional single line string showing the basic syntax
    :type usage: Optional[str]
    """

    def __init__(self, name: str, description: str, usage: Optional[str] = None):
        self.name = name
        self._usage = usage
        self.description = description
        self.logger = logging.getLogger(f"commands.{self.name}")
        self.parser = CommandParser(self.name)

    @property
    def usage(self) -> str:
        """
        Get the usage string of a command
        """

        if self._usage is None:
            return f"!{self.name} {self.parser.default_usage}"
        else:
            return self._usage

    async def run(self, args: Namespace, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        """
        Perform command-specific actions

        This method should be overwritten in actual commands to perform the desired action.

        :param args: parsed namespace containing the arguments
        :type args: argparse.Namespace
        :param bot: the Matrix Bot to use while processing the command
        :type bot: matebot_matrix.bot.MateBot
        :param room: room the message came in
        :type room: nio.MatrixRoom
        :param event: incoming message event
        :type event: nio.RoomMessageText
        :return: None
        :raises NotImplementedError: because this method should be overwritten by subclasses
        """

        raise NotImplementedError("Overwrite the BaseCommand.run() method in a subclass")

    async def __call__(self, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> None:
        """
        Parse arguments of the incoming event and execute the .run() method

        This method is the callback method used by `AsyncClient.add_callback_handler`.

        :param bot: the Matrix Bot to use while processing the command
        :type bot: matebot_matrix.bot.MateBot
        :param room: room the message came in
        :type room: nio.MatrixRoom
        :param event: incoming message event
        :type event: nio.RoomMessageText
        :return: None
        """

        try:
            self.logger.debug(f"{type(self).__name__} by {event.sender}")
            args = await self.parser.parse(event, bot)
            self.logger.debug(f"Parsed command's arguments: {args}")
            await self.run(args, bot, room, event)

        except ParsingError as exc:
            await bot.reply(str(exc), room, event)

        except APIConnectionException as exc:
            self.logger.exception(f"API connectivity problem @ {type(self).__name__} ({exc.exc})")
            await bot.reply(f"<i>I'm having networking problems.</i><br/>{exc.message}", room, event)

        except UserAPIException as exc:
            self.logger.debug(f"{type(exc).__name__}: {exc.message} ({exc.status}, {exc.details})")
            await bot.reply(exc.message, room, event)

        except APIException as exc:
            self.logger.warning(f"APIException @ {type(self).__name__} ({exc.status}, {exc.details})", exc_info=True)
            await bot.reply(f"The command couldn't be executed.<br/>{exc.message}", room, event, send_as_notice=False)

    '''
    async def get_sender(self, bot: MateBot, room: MatrixRoom, event: RoomMessageText) -> User:
        self.logger.debug(event.sender)

        # event attributes & methods: 'body', 'decrypted', 'event_id', 'flattened', 'format', 'formatted_body', 'from_dict', 'parse_decrypted_event', 'parse_encrypted_event', 'parse_event', 'room_id', 'sender', 'sender_key', 'server_timestamp', 'session_id', 'source', 'stripped_body', 'transaction_id', 'verified'

        sender = await bot.sdk.get_user_by_app_alias(str(event.sender))
        try:
            user = User.get(event.sender)
        except ValueError:
            user = User.new(event.sender)
            await api.send_reply(f"Welcome {user}, please enjoy your drinks", room, event, send_as_notice=True)

            if room.room_id != config.room:
                user.external = True

        display_name = (await api.client.get_displayname(user.matrix_id)).displayname
        if display_name != user.display_name:
            user.display_name = display_name
            user.push()

        if room.room_id == config.room and user.external:
            user.external = False
            await api.send_reply(f"{user}, you are now an internal.", room, event, send_as_notice=True)

        return user

    async def ensure_permissions(
            self,
            user: User,
            level: int,
            api: MateBot,
            event: RoomMessageText,
            room: MatrixRoom
    ) -> bool:
        """
        Ensure that a user is allowed to perform an operation that requires specific permissions

        The parameter ``level`` is a constant and determines the required
        permission level. It's not calculated but rather interpreted:

          * ``ANYONE`` means that any user is allowed to perform the task
          * ``VOUCHED`` means that any internal user or external user with voucher is allowed
          * ``INTERNAL`` means that only internal users are allowed
          * ``TRUSTED`` means that only internal users with vote permissions are allowed

        .. note::

            This method will automatically reply to the incoming message when
            the necessary permissions are not fulfilled. Use the return value
            to determine whether you should simply quit further execution of
            your method (returned ``False``) or not (returned ``True``).

        :param user: MateBotUser that tries to execute a specific command
        :type user: MateBotUser
        :param level: minimal required permission level to be allowed to perform some action
        :type level: int
        :param api: api to reply with
        :type api: hopfenmatrix.api_wrapper.ApiWrapper
        :param event: event to reply to
        :type event: nio.RoomMessageText
        :param room: room to reply in
        :type room: nio.MatrixRoom
        :return: whether further access should be allowed (``True``) or not
        :rtype: bool
        """
        if level == VOUCHED and user.external and user.creditor is None:
            msg = (
                f"You can't perform {self.name}. You are an external user "
                "without creditor. For security purposes, every external user "
                "needs an internal voucher. Use /help for more information."
            )

        elif level == INTERNAL and user.external:
            msg = (
                f"You can't perform {self.name}. You are an external user. "
                "To perform this command, you must be marked as internal user. "
                "Send any command to an internal chat to update your privileges."
            )

        elif level == TRUSTED and not user.permission:
            msg = (
                f"You can't perform {self.name}. You don't have permissions to vote."
            )

        else:
            return True

        await api.send_reply(msg, room, event, send_as_notice=True)
        return False
    '''
