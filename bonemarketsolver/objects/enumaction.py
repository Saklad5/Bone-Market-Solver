__all__ = ['EnumAction']
__author__ = "Jeremy Saklad"

from argparse import Action

class EnumAction(Action):
    def __init__(self, **kwargs):
        # Pop off the type value
        enum = kwargs.pop('type', None)

        nargs = kwargs.get('nargs')

        # Generate choices from the Enum
        kwargs.setdefault('choices', tuple(member.name.lower() for member in enum))

        super(EnumAction, self).__init__(**kwargs)

        self._enum = enum
        self._nargs = nargs

    def __call__(self, parser, namespace, values, option_string=None):
        if self._nargs is None or self._nargs == '?':
            # Convert value back into an Enum
            enum = self._enum[values.upper()]

            setattr(namespace, self.dest, enum)
        else:
            # Convert values back into Enums
            enums = [self._enum[value.upper()] for value in values]

            items = getattr(namespace, self.dest, list()) + enums
            setattr(namespace, self.dest, items)
