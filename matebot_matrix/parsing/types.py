"""
Collection of parser argument types.
See :class:`mate_bot.parsing.actions.Action`'s type parameter
"""

import re
from typing import Union

from matebot_sdk.schemas import Consumable, User
from matebot_sdk.exceptions import UserAPIException

from ..bot import MateBot
from ..commands.base import BaseCommand


__amount_pattern = re.compile(r"^(\d+)(?:[,.](\d)(\d)?)?$")
# Regex explanation:
# It matches any non-zero number of digits with an optional , or . followed by exactly one or two digits
# If there is a , or . then the first decimal is required
#
# The match's groups:
# 1st group: leading number, 2nd group: 1st decimal, 3rd group: 2nd decimal


__user_reference_pattern = re.compile(r"^<a .*href=\"https://matrix.to/#/(@\S+:\S+\.\w\w+)\".*>(.+)</a>$")
# Regex explanation:
# Any opening & closing HTML <a> tag with the 'href' attribute and some
# valid-looking target and at least one character in its tag body
#
# The match's groups:
# 1st group: the username that was annotated, 2nd group: content of the HTML tag (probably human-readable name)


def string(arg: str, **_) -> str:
    """
    Return the string as-is

    :param arg: string to be parsed
    :type arg: str
    :return: same string
    :rtype: str
    """

    return str(arg)


def lowercase(arg: str, **_) -> str:
    """
    Return the lowercase string

    :param arg: string to be parsed
    :type arg: str
    :return: string in lowercase
    :rtype: str
    """

    return str(arg).lower()


def uppercase(arg: str, **_) -> str:
    """
    Return the uppercase string

    :param arg: string to be parsed
    :type arg: str
    :return: string in uppercase
    :rtype: str
    """

    return str(arg).upper()


def amount(arg: str, **_) -> int:
    """
    Convert the string into an amount of money

    A maximum allowed amount, this function accepts, is set in the config.

    :param arg: string to be parsed
    :type arg: str
    :return: Amount of money in cent
    :rtype: int
    :raises ValueError: when the arg seems to be no valid amount or is too big
    """

    match = __amount_pattern.match(arg)
    if match is None:
        raise ValueError("Doesn't match an amount's regex")

    val = int(match.group(1)) * 100
    if match.group(2):
        val += int(match.group(2)) * 10
    if match.group(3):
        val += int(match.group(3))

    if val == 0:
        raise ValueError("An amount can't be zero")

    return val


def natural(arg: str, **_) -> int:
    """
    Convert the string into a natural number (positive integer)

    :param arg: string to be parsed
    :type arg: str
    :return: only positive integers
    :rtype: int
    :raises ValueError: when the string seems to be no integer or is not positive
    """

    result = int(arg)
    if result <= 0:
        raise ValueError("Not a positive integer.")
    return result


async def user(arg: str, bot: MateBot) -> User:
    """
    Convert the string into a MateBot user as defined in the ``state`` package

    :param arg: string to be parsed
    :type arg: str
    :param bot: MateBot to allow querying the API server
    :type arg: matebot_matrix.bot.MateBot
    :return: fully functional MateBot user
    :rtype: User
    :raises ValueError: when username is ambiguous or the argument wasn't a mention
    """

    try:
        match = __user_reference_pattern.match(arg.lower())
        if match is None:
            return await bot.sdk.get_user_by_app_alias(arg.lower())
        return await bot.sdk.get_user_by_app_alias(match.group(1))
    except UserAPIException as exc:
        raise ValueError(exc.message) from exc


def command(arg: str, **_) -> BaseCommand:
    """
    Convert the string into a command with this name

    :param arg: the desired command's name
    :type arg: str
    :return: the command
    :rtype: BaseCommand
    :raises ValueError: when the command is unknown
    """

    try:
        from ..commands import COMMANDS
        return COMMANDS[arg.lower()]
    except KeyError:
        raise ValueError(f"{arg} is an unknown command")


async def extended_consumable_type(arg: str, bot: MateBot) -> Union[Consumable, str]:
    """
    Convert the string into a consumable schema, if found, or the special string "?"

    :param arg: the desired consumable's name
    :type arg: str
    :param bot: MateBot to allow querying the API server
    :type arg: matebot_matrix.bot.MateBot
    :return: the found consumable schema or the fixed special string "?"
    :rtype: Union[matebot_sdk.schemas.Consumable, str]
    :raises ValueError: when the consumable wasn't found or the string isn't "?"
    """

    if arg.strip() == "?":
        return "?"
    for consumable in await bot.sdk.get_consumables():
        if consumable.name.lower() == arg.lower():
            return consumable
    raise ValueError(f"{arg} is no known consumable")
