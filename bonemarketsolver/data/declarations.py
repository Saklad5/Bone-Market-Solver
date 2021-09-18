__all__ = ['Declaration']
__author__ = "Jeremy Saklad"

from enum import Enum

from .costs import Cost
from ..objects.action import Action

class Declaration(Enum):
    """An action that is taken after all adjustments have been made to a skeleton."""

    __slots__ = '_value_', '_name_', '__objclass__'

    AMPHIBIAN = Action(
            "Declare your (Skeleton Type) a completed Amphibian",
            cost = Cost.ACTION.value
            )

    APE = Action(
            "Declare your (Skeleton Type) a completed Ape",
            cost = Cost.ACTION.value
            )

    BIRD = Action(
            "Declare your (Skeleton Type) a completed Bird",
            cost = Cost.ACTION.value
            )

    CHIMERA = Action(
            "Declare your (Skeleton Type) a completed Chimera",
            cost = Cost.ACTION.value,
            implausibility = 3
            )

    CURATOR = Action(
            "Declare your (Skeleton Type) a completed Curator",
            cost = Cost.ACTION.value
            )

    FISH = Action(
            "Declare your (Skeleton Type) a completed Fish",
            cost = Cost.ACTION.value
            )

    HUMANOID = Action(
            "Declare your (Skeleton Type) a completed Humanoid",
            cost = Cost.ACTION.value
            )

    INSECT = Action(
            "Declare your (Skeleton Type) a completed Insect",
            cost = Cost.ACTION.value
            )

    MONKEY = Action(
            "Declare your (Skeleton Type) a completed Monkey",
            cost = Cost.ACTION.value
            )

    REPTILE = Action(
            "Declare your (Skeleton Type) a completed Reptile",
            cost = Cost.ACTION.value
            )

    SPIDER = Action(
            "Declare your (Skeleton Type) a completed Spider",
            cost = Cost.ACTION.value
            )

    def __str__(self):
        return str(self.value)
