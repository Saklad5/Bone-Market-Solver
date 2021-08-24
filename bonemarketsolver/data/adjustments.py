__all__ = ['Adjustment']
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


def _implausibility(stat: int):
    chance = _narrow_challenge_6(stat)

    if chance == 1:
        return 0
    else:
        failure_actions = (1 / chance) - 1
        implausibility = 2 * failure_actions
        return implausibility


class Adjustment(Enum):
    """An action that is taken after all parts have been added to a skeleton."""

    CARVE_AWAY_AGE = Action(
            "Carve away some evidence of age",
            cost = Cost.ACTION.value / _narrow_challenge_6(Char.MITHRIDACY.value),
            antiquity = -2,
            implausibility = _implausibility(Char.MITHRIDACY.value)
            )

    DISGUISE_AMALGAMY = Action(
            "Disguise the amalgamy of this piece",
            cost = 25*Cost.JADE_FRAGMENT.value + Cost.ACTION.value / _narrow_challenge_6(Char.KATALEPTIC_TOXICOLOGY.value),
            amalgamy = -2,
            implausibility = _implausibility(Char.KATALEPTIC_TOXICOLOGY.value)
            )

    MAKE_LESS_DREADFUL = Action(
            "Make your skeleton less dreadful",
            cost = Cost.ACTION.value / _narrow_challenge_6(Char.KATALEPTIC_TOXICOLOGY.value),
            menace = -2,
            implausibility = _implausibility(Char.KATALEPTIC_TOXICOLOGY.value)
            )

    def __str__(self):
        return str(self.value)
