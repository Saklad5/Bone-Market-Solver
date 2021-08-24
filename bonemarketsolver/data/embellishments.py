__all__ = ['Embellishment']
__author__ = "Jeremy Saklad"

from enum import Enum

from .costs import Cost
from ..objects.action import Action
from ..read_char import *
from ..challenge_functions import narrow_challenge


def _convincing_history_cost():
    chance = narrow_challenge(6, Char.KATALEPTIC_TOXICOLOGY.value)

    if chance == 1:
        cost = 3*Cost.REVISIONIST_NARRATIVE.value + Cost.ACTION.value
    else:
        actions = 1 / chance
        cost = actions * Cost.ACTION.value
        cost += Cost.REVISIONIST_NARRATIVE.value * (3 + actions - 1)
    return cost


class Embellishment(Enum):
    """An action is taken after a declaration has been made for a skeleton."""

    MORE_PLAUSIBLE = Action(
            "Make it seem just a bit more plausible",
            cost = Cost.ACTION.value + Cost.REVISIONIST_NARRATIVE.value,
            implausibility = -1
            )

    CONVINCING_HISTORY = Action(
            "Invest great time and skill in coming up with a convincing history",
            cost = _convincing_history_cost(),
            implausibility = -5
            )

    def __str__(self):
        return str(self.value)
