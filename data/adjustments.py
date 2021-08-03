from enum import Enum

from data.costs import Cost
from objects.action import Action

class Adjustment(Enum):
    """An action that is taken after all parts have been added to a skeleton."""

    CARVE_AWAY_AGE = Action(
            "Carve away some evidence of age",
            cost = Cost.ACTION.value,
            antiquity = -2
            )

    DISGUISE_AMALGAMY = Action(
            "Disguise the amalgamy of this piece",
            cost = Cost.ACTION.value + 25*Cost.JADE_FRAGMENT.value,
            amalgamy = -2
            )

    MAKE_LESS_DREADFUL = Action(
            "Make your skeleton less dreadful",
            cost = Cost.ACTION.value,
            menace = -2
            )

    def __str__(self):
        return str(self.value)
