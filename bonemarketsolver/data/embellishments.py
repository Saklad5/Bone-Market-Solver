__all__ = ['Embellishment']
__author__ = "Jeremy Saklad"

from enum import Enum

from .costs import Cost
from ..objects.action import Action

class Embellishment(Enum):
    """An action is taken after a declaration has been made for a skeleton."""

    __slots__ = '_value_', '_name_', '__objclass__'

    MORE_PLAUSIBLE = Action(
            "Make it seem just a bit more plausible",
            cost = Cost.ACTION.value + Cost.REVISIONIST_NARRATIVE.value,
            implausibility = -1
            )

    CONVINCING_HISTORY = Action(
            "Invest great time and skill in coming up with a convincing history",
            cost = Cost.ACTION.value + 3*Cost.REVISIONIST_NARRATIVE.value,
            implausibility = -5
            )

    def __str__(self):
        return str(self.value)
