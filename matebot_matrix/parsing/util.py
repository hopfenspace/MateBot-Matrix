"""
Collection of simple utility classes
"""


class Representable(object):
    """
    Abstract base class that provides a nice ``__repr__`` method

    The ``__repr__`` method returns a string in the format:

    .. code-block::

        ClassName(
                pos1, pos2, ...,
                key1=value1, key2=value2, ...,
                **{'weird key 3': value3, 'weird key 4': value4}
            )

    (The whitespace is just for illustration)

    The attributes are determined by the methods ``_get_args`` and ``_get_kwargs``.
    Their default implementations uses ``__slots__`` or ``__dict__``
    """

    def __repr__(self):
        # Sort the keyword arguments by whether their name is an identifier or not
        id_args = {}
        non_id_args = {}
        for name, value in self._get_kwargs():
            if name.isidentifier():
                id_args[name] = value
            else:
                non_id_args[name] = value

        arg_strings = []
        # Add the positional arguments
        arg_strings.extend(map(repr, self._get_args()))
        # Add the identifier arguments
        arg_strings.extend(map(lambda pair: f"{pair[0]}={repr(pair[1])}", id_args.items()))
        # If any present, add non identifier arguments
        if non_id_args:
            arg_strings.append(f"**{repr(non_id_args)}")

        return f"{type(self).__name__}({', '.join(arg_strings)})"

    def _get_kwargs(self):
        if hasattr(self.__class__, "__slots__"):
            return sorted(((key, getattr(self, key)) for key in self.__slots__))
        else:
            return sorted(self.__dict__.items())

    def _get_args(self):
        return []


class Namespace(Representable):
    """
    Simple object for storing attributes.

    Implements:

    * equality by attribute names and values
    * a simple string representation (via Representable)
    * return None on undefined attribute
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        if not isinstance(other, Namespace):
            return TypeError("Can only compare Namespace to another Namespace")
        return vars(self) == vars(other)

    def __contains__(self, key):
        return key in self.__dict__

    def __getattr__(self, key: str) -> None:
        return None
