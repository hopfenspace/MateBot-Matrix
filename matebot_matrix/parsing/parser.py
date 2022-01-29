"""
MateBot's CommandParser
"""

import typing
import inspect
import html.parser
from typing import List

from nio import RoomMessageText

from .util import Namespace, Representable
from .usage import CommandUsage
from .actions import Action
from .formatting import plural_s
from ..bot import MateBot
from ..err import ParsingError


class CommandParser(Representable):
    """
    Class for parsing telegram messages into python objects.

    :param name: the command name the parser is for.
        This is used in error messages.
    :type name: str
    """

    def __init__(self, name: str):
        # Add initial default usage
        self._name = name
        self._usages = [CommandUsage()]

    @property
    def usages(self) -> typing.List[CommandUsage]:
        """
        Return list of usage objects
        """

        return self._usages

    @property
    def default_usage(self) -> CommandUsage:
        """
        Return the default usage added in constructor
        """

        return self._usages[0]

    def add_argument(self, *args, **kwargs) -> Action:
        """
        Add an argument to the default usage

        See `CommandUsage.add_argument` for type signature
        """

        return self._usages[0].add_argument(*args, **kwargs)

    def new_usage(self) -> CommandUsage:
        """
        Initialize, add and return a new usage object
        """

        self._usages.append(CommandUsage())
        return self._usages[-1]

    async def parse(self, msg: RoomMessageText, bot: MateBot) -> Namespace:
        """
        Parse a telegram message into a namespace.

        This just combines the _split and _parse function.

        :param msg: message to parse
        :type msg: telegram.Message
        :param bot: MateBot to allow querying the API server
        :type bot: matebot_matrix.bot.MateBot
        :return: parsed arguments
        :rtype: Namespace
        """

        # Split message into argument strings
        arg_strings = _split_message(msg)

        # Remove bot command
        arg_strings = arg_strings[1:]

        # Parse
        return await self._parse(arg_strings, bot)

    async def _parse(self, arg_strings: typing.List[str], bot: MateBot) -> Namespace:
        """
        Internal function for parsing from a list of strings.

        :param arg_strings: a list of strings to parse
        :type arg_strings: List[str]
        :return: parsed arguments
        :rtype: Namespace
        """

        errors = []
        for usage in self._usages:
            if usage.min_arguments > len(arg_strings):
                errors.append(ParsingError(
                    f"requires at least {usage.min_arguments} argument{plural_s(usage.min_arguments)}."
                ))
                continue
            elif usage.max_arguments < len(arg_strings):
                errors.append(ParsingError(
                    f"allows at most {usage.max_arguments} argument{plural_s(usage.max_arguments)}."
                ))
                continue
            else:
                # Try the remaining ones
                try:
                    return await self._parse_usage(usage, arg_strings, bot)
                except ParsingError as err:
                    errors.append(err)
                continue

        # If you enter here, then all usages broke
        # Combine their error messages into one
        else:
            if len(self._usages):
                msg = ""
            else:
                msg = "No usage applies:"

            for usage, error in zip(self._usages, errors):
                msg += f"\n`/{self._name} {usage}` {error}"
            raise ParsingError(msg)

    async def _parse_usage(self, usage: CommandUsage, arg_strings: typing.List[str], bot: MateBot) -> Namespace:
        """
        Try to parse the arguments with a usage

        :param usage: the usage to parse the arguments with
        :type usage: CommandUsage
        :param arg_strings: argument strings to parse
        :type arg_strings: List[str]
        :param bot: MateBot to allow querying the API server
        :type bot: matebot_matrix.bot.MateBot
        :return: parsed arguments
        :rtype: Namespace
        """

        # Shortcut out if there are no actions
        if len(usage.actions) == 0:
            return Namespace()

        # Initialize namespace and populate it with the defaults
        namespace = Namespace()
        for action in usage.actions:
            setattr(namespace, action.dest, action.default)

        async def consume_action(local_action: Action, strings: typing.List[str]):
            """
            Use an action to consume as many argument strings as possible
            """

            values = []
            error = None

            while len(strings) > 0:
                string = strings.pop(0)

                try:
                    # Try converting the argument string
                    if inspect.iscoroutinefunction(local_action.type):
                        value = await local_action.type(string, bot=bot)
                    else:
                        value = local_action.type(string, bot=bot)

                    # Check choices
                    if action.choices is not None and value not in action.choices:
                        raise ValueError(f"{value} is not an available choice, choose from "
                                         + ", ".join(map(lambda x: f"`{x}`", action.choices)))

                    # Add converted to list
                    values.append(value)

                    # Action can take more -> next string
                    if len(values) < local_action.max_args:
                        continue
                    else:
                        break

                except ValueError as err:
                    # Save error for later
                    error = err

                    # Put back unprocessed string
                    strings.insert(0, string)

                    break

            # Action isn't satisfied -> error
            if local_action.min_args > len(values):
                if error is not None:
                    raise ParsingError(str(error))
                else:
                    raise ParsingError(f"Missing argument{plural_s(local_action.min_args-len(values))}")

            # Action is satisfied -> finish with action
            else:
                # Process action
                if action.nargs is None:
                    local_action(namespace, values[0])
                elif action.nargs == "?":
                    if len(values) > 0:
                        local_action(namespace, values[0])
                else:
                    local_action(namespace, values)

        # Copy arg_strings to have a local list to mutate
        left_strings = list(arg_strings)

        for action in usage.actions:
            await consume_action(action, left_strings)

        if len(left_strings) > 0:
            raise ParsingError(f"Unrecognized argument{plural_s(left_strings)}: {', '.join(left_strings)}")

        return namespace


def _split_message(event: RoomMessageText) -> List[str]:
    """
    Split a room message text into a list of strings

    This function keeps <a> tags and their attributes in formatted HTML
    intact and also removes all other HTML tags and attributes. If no
    formatted message is found, the plain text version will be split.

    Note that nested <a> tags are not well supported, as they should
    not be found in the protocol anyways. For example, the following
    formatted text '<a>1<a>2</a>3</a>' would yield the list of strings
    ['<a>2</a>', '<a>3</a>'], i.e. the "1" would be discarded.

    :param event: event to process
    :type event: nio.RoomMessageText
    :return: list of argument strings
    :rtype: List[str]
    """

    class MatrixReferenceElement:
        def __init__(self, attrs: List[tuple], data: str):
            self.attrs = attrs
            self.data = data

    class MatrixFormattedMessageParser(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.elements = []
            self.open_tags = []

        @staticmethod
        def _format_attr(attr: tuple) -> str:
            return f"{attr[0]}=\"{attr[1]}\""

        def error(self, message):
            raise ValueError(message)

        def handle_starttag(self, tag: str, attrs: List[tuple]):
            if tag.lower() == "a":
                self.open_tags.append(MatrixReferenceElement(attrs, ""))

        def handle_endtag(self, tag: str):
            if tag.lower() == "a":
                if self.open_tags:
                    entry = self.open_tags.pop()
                    attrs = ' '.join(map(self._format_attr, entry.attrs))
                    space = " " if attrs else ""
                    self.elements.append(f"<a{space}{attrs}>{entry.data}</a>")
                else:
                    raise ValueError("HTML parser error: unopened tag")

        def handle_data(self, data):
            if not self.open_tags:
                self.elements.extend(data.split())
            else:
                self.open_tags[-1].data = data

    if event.formatted_body:
        p = MatrixFormattedMessageParser()
        p.feed(event.formatted_body)
        if p.open_tags:
            raise ValueError("HTML parser error: unclosed tag")
        return p.elements

    else:
        return event.stripped_body.split()
