__all__ = ['Action']
__author__ = "Jeremy Saklad"

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Action:
    """An action that affects a skeleton's qualities."""

    __slots__ = '__dict__', 'name'

    name: str

    # Cost in pennies of using this action, including the value of the actions spent
    cost: float = field(metadata={'unit': 'pennies'})

    # Skeleton: Torso Style
    torso_style: int = None

    # Approximate Value of Your Skeleton in Pennies
    value: int = field(default=0, metadata={'unit': 'pennies'})

    # Skeleton: Skulls Needed
    skulls_needed: int = 0

    # Skeleton: Limbs Needed
    limbs_needed: int = 0

    # Skeleton: Tails Needed
    tails_needed: int = 0

    # Skeleton: Skulls
    skulls: int = 0

    # Skeleton: Arms
    arms: int = 0

    # Skeleton: Legs
    legs: int = 0

    # Skeleton: Tails
    tails: int = 0

    # Skeleton: Wings
    wings: int = 0

    # Skeleton: Fins
    fins: int = 0

    # Skeleton: Tentacles
    tentacles: int = 0

    # Skeleton: Amalgamy
    amalgamy: int = 0

    # Skeleton: Antiquity
    antiquity: int = 0

    # Skeleton: Menace
    menace: int = 0

    # Skeleton: Self-Evident Implausibility
    implausibility: int = 0

    # Skeleton: Support for a Counter-church Theology
    counter_church: int = 0

    # Bone Market Exhaustion
    exhaustion: int = 0

    def __str__(self):
        return str(self.name)
