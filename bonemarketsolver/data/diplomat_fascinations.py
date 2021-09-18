__all__ = ['DiplomatFascination']
__author__ = "Jeremy Saklad"

from enum import Enum

from .buyers import Buyer

DiplomatFascination = Enum(
        'DiplomatFascination',
        ( (diplomat.name[22:], diplomat) for diplomat in Buyer
            if diplomat.name.startswith('THE_TRIFLING_DIPLOMAT_') ),
        module = __name__
        )
DiplomatFascination.__doc__ = "The current fascination of the Trifling Diplomat."
DiplomatFascination.__slots__ = '_value_', '_name_', '__objclass__'
