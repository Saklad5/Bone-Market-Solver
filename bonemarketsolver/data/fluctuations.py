__all__ = ['Fluctuation']
__author__ = "Jeremy Saklad"

from enum import Enum

class Fluctuation(Enum):
    """Which skeleton attribute is currently boosted."""

    __slots__ = '_value_', '_name_', '__objclass__'

    ANTIQUITY = 1
    AMALGAMY = 2
    MENACE = 3
