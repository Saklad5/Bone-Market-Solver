__all__ = ['BlacklistAction']
__author__ = "Jeremy Saklad"

from argparse import Action

from ..data.adjustments import Adjustment
from ..data.appendages import Appendage
from ..data.buyers import Buyer
from ..data.declarations import Declaration
from ..data.embellishments import Embellishment
from ..data.skulls import Skull
from ..data.torsos import Torso

def convert_to_enum(value):
    split = value.split(".", 1)

    enum = globals()[split[0]]
    return enum[split[1]]

class BlacklistAction(Action):
    def __init__(self, **kwargs):
        nargs = kwargs.get('nargs')

        super(BlacklistAction, self).__init__(**kwargs)

        self._nargs = nargs

    def __call__(self, parser, namespace, values, option_string=None):
        if self._nargs is None or self._nargs == '?':
            # Convert value back into an Enum
            enum = convert_to_enum(value)

            setattr(namespace, self.dest, enum)
        else:
            # Convert values back into Enums
            enums = [convert_to_enum(value) for value in values]

            items = getattr(namespace, self.dest, list()) + enums
            setattr(namespace, self.dest, items)
