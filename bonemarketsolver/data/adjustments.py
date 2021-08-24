__all__ = ['Adjustment']
__author__ = "Jeremy Saklad"

from enum import Enum

from .costs import Cost
from ..objects.action import Action
from ..read_char import Char
from ..challenge_functions import narrow_challenge, mean_outcome


class Adjustment(Enum):
    """An action that is taken after all parts have been added to a skeleton."""

    CARVE_AWAY_AGE = Action(
            "Carve away some evidence of age",
            cost = Cost.ACTION.value / narrow_challenge(6, Char.MITHRIDACY.value),
            antiquity = -2,
            implausibility = mean_outcome(0, 2, narrow_challenge(6, Char.MITHRIDACY.value))
            )

    DISGUISE_AMALGAMY = Action(
            "Disguise the amalgamy of this piece",
            cost = 25*Cost.JADE_FRAGMENT.value + Cost.ACTION.value / narrow_challenge(6, Char.KATALEPTIC_TOXICOLOGY.value),
            amalgamy = -2,
            implausibility = mean_outcome(0, 2, narrow_challenge(6, Char.KATALEPTIC_TOXICOLOGY.value))
            )

    MAKE_LESS_DREADFUL = Action(
            "Make your skeleton less dreadful",
            cost = Cost.ACTION.value / narrow_challenge(6, Char.KATALEPTIC_TOXICOLOGY.value),
            menace = -2,
            implausibility = mean_outcome(0, 2, narrow_challenge(6, Char.KATALEPTIC_TOXICOLOGY.value))
            )

    def __str__(self):
        return str(self.value)
