__all__ = ['Embellishment']
__author__ = "Jeremy Saklad"

from enum import Enum

from .costs import Cost
from ..objects.action import Action
from ..read_char import *


def _narrow_challenge_6(stat: int):
    if 0 < stat < 11:
        chance = stat/10
    elif stat < 1:
        chance = .1
    else:
        chance = 1

    return chance


def _convincing_history_cost():
    chance = _narrow_challenge_6(Char.KATALEPTIC_TOXICOLOGY.value)

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
