__all__ = ['Torso']
__author__ = "Jeremy Saklad"

from enum import Enum

from .costs import Cost
from ..objects.action import Action

class Torso(Enum):
    """An action that initiates a skeleton."""

    __slots__ = '_value_', '_name_', '__objclass__'

    HEADLESS_HUMANOID = Action(
            "Reassemble your Headless Humanoid",
            cost = Cost.ACTION.value + Cost.HEADLESS_SKELETON.value,
            torso_style = 10,
            value = 250,
            skulls_needed = 1,
            arms = 2,
            legs = 2
            )

    # Licentiate
    VICTIM_SKELETON = Action(
           "Supply a skeleton of your own",
           cost = Cost.ACTION.value,
           torso_style = 10,
           value = 250,
           skulls_needed = 1,
           arms = 2,
           legs = 2
           )

    HUMAN_RIBCAGE = Action(
            "Build on the Human Ribcage",
            cost = Cost.ACTION.value + Cost.HUMAN_RIBCAGE.value,
            torso_style = 15,
            value = 1250,
            skulls_needed = 1,
            limbs_needed = 4
            )

    THORNED_RIBCAGE = Action(
            "Make something of your Thorned Ribcage",
            cost = Cost.ACTION.value + Cost.THORNED_RIBCAGE.value,
            torso_style = 20,
            value = 1250,
            skulls_needed = 1,
            limbs_needed = 4,
            tails_needed = 1,
            amalgamy = 1,
            menace = 1
            )

    SKELETON_WITH_SEVEN_NECKS = Action(
            "Build on the Skeleton with Seven Necks",
            cost = Cost.ACTION.value + Cost.SKELETON_WITH_SEVEN_NECKS.value,
            torso_style = 30,
            value = 6250,
            skulls_needed = 7,
            limbs_needed = 2,
            legs = 2,
            amalgamy = 2,
            menace = 1
            )

    FLOURISHING_RIBCAGE = Action(
            "Build on the Flourishing Ribcage",
            cost = Cost.ACTION.value + Cost.FLOURISHING_RIBCAGE.value,
            torso_style = 40,
            value = 1250,
            skulls_needed = 2,
            limbs_needed = 6,
            tails_needed = 1,
            amalgamy = 2
            )

    MAMMOTH_RIBCAGE = Action(
            "Build on the Mammoth Ribcage",
            cost = Cost.ACTION.value + Cost.MAMMOTH_RIBCAGE.value,
            torso_style = 50,
            value = 6250,
            skulls_needed = 1,
            limbs_needed = 4,
            tails_needed = 1,
            antiquity = 2
            )

    RIBCAGE_WITH_A_BOUQUET_OF_EIGHT_SPINES = Action(
            "Build on the Ribcage with the Eight Spines",
            cost = Cost.ACTION.value + Cost.RIBCAGE_WITH_EIGHT_SPINES.value,
            torso_style = 60,
            value = 31250,
            skulls_needed = 8,
            limbs_needed = 4,
            tails_needed = 1,
            amalgamy = 1,
            menace = 2
            )

    LEVIATHAN_FRAME = Action(
            "Build on the Leviathan Frame",
            cost = Cost.ACTION.value + Cost.LEVIATHAN_FRAME.value,
            torso_style = 70,
            value = 31250,
            skulls_needed = 1,
            limbs_needed = 2,
            tails = 1,
            antiquity = 1,
            menace = 1
            )

    PRISMATIC_FRAME = Action(
            "Build on the Prismatic Frame",
            cost = Cost.ACTION.value + Cost.PRISMATIC_FRAME.value,
            torso_style = 80,
            value = 31250,
            skulls_needed = 3,
            limbs_needed = 3,
            tails_needed = 3,
            amalgamy = 2,
            antiquity = 2
            )

    FIVE_POINTED_FRAME = Action(
            "Build on the Five-Pointed Frame",
            cost = Cost.ACTION.value + Cost.FIVE_POINTED_RIBCAGE.value,
            torso_style = 100,
            value = 31250,
            skulls_needed = 5,
            limbs_needed = 5,
            amalgamy = 2,
            menace = 1
            )

    SEGMENTED_RIBCAGE = Action(
            "Build on a Segmented Ribcage",
            cost = Cost.ACTION.value + Cost.SEGMENTED_RIBCAGE.value,
            torso_style = 45,
            value = 250,
            skulls_needed = 1,
            limbs_needed = 2,
            tails_needed = 1,
            segments = 1,
            )

    def __str__(self):
        return str(self.value)
