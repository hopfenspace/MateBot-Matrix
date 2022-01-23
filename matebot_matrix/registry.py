"""
MateBot registry of available executors

Every dictionary in this module stores the executors
for exactly one handler type. The key type for every
dictionary is a string. However, some dictionaries
want to use this keys as patterns/filters for the
handlers, too. The following list covers the four
different module's attributes and describes their use:

  - ``commands`` is the only pool of executors that uses
    the name of the command as key and does therefore not
    filter incoming commands in the handler class. The
    class ``CommandHandler`` is used for all values, while
    the type of all values is ``BaseCommand`` or a subclass.
"""

commands: dict = {}
