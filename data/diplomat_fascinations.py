__all__ = ['DiplomatFascination']
__author__ = "Jeremy Saklad"

from enum import Enum

from data.buyers import Buyer

DiplomatFascination = Enum(
        'DiplomatFascination',
        ( (diplomat.name[22:], diplomat) for diplomat in Buyer
            if diplomat.name.startswith('THE_TRIFLING_DIPLOMAT_') ),
        module = __name__
        )
DiplomatFascination.__doc__ = "The current fascination of the Trifling Diplomat."
