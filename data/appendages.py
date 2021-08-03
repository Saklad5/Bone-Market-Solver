__all__ = ['Appendage']
__author__ = "Jeremy Saklad"

from enum import Enum

from data.costs import Cost
from objects.action import Action

class Appendage(Enum):
    """An action that is taken once all skulls are added to a skeleton."""

    # Cost from this scales with limbs and is partially implemented separately
    ADD_JOINTS = Action(
            "Add four more joints to your skeleton",
            cost = Cost.ACTION.value + Cost.TREMBLING_AMBER.value,
            limbs_needed = 4,
            amalgamy = 2
            )

    ALBATROSS_WING = Action(
            "Put an Albatross Wing on your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.ALBATROSS_WING.value,
            value = 1250,
            limbs_needed = -1,
            wings = 1,
            amalgamy = 1
            )

    AMBER_FIN = Action(
            "Attach the Amber-Crusted Fin to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.AMBER_FIN.value,
            value = 1500,
            limbs_needed = -1,
            fins = 1,
            amalgamy = 1,
            menace = 1
            )

    BAT_WING = Action(
            "Add a Bat Wing to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.BAT_WING.value,
            value = 1,
            limbs_needed = -1,
            wings = 1,
            menace = -1
            )

    BLACK_STINGER = Action(
            "Apply a Jet Black Stinger to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.BLACK_STINGER.value,
            value = 50,
            tails_needed = -1,
            tails = 1,
            menace = 2
            )

    CRUSTACEAN_PINCER = Action(
            "Apply a Crustacean Pincer to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.CRUSTACEAN_PINCER.value,
            limbs_needed = -1,
            arms = 1,
            menace = 1
            )

    DEER_FEMUR = Action(
            "Apply the Femur of a Surface Deer to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.DEER_FEMUR.value,
            value = 10,
            limbs_needed = -1,
            legs = 1,
            menace = -1
            )

    # Counter-Church theology from this scales with torso style and is implemented separately
    FIACRE_THIGH = Action(
            "Affix Saint Fiacre's Thigh Relic to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.FIACRE_THIGH.value,
            value = 1250,
            limbs_needed = -1,
            legs = 1
            )

    FIN_BONES = Action(
            "Put Fins on your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.FIN_BONES.value,
            value = 50,
            limbs_needed = -1,
            fins = 1
            )

    FOSSILISED_FORELIMB = Action(
            "Apply a Fossilised Forelimb to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.FOSSILISED_FORELIMB.value,
            value = 2750,
            limbs_needed = -1,
            arms = 1,
            antiquity = 2
            )

    HELICAL_THIGH = Action(
            "Affix the Helical Thighbone to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.HELICAL_THIGH.value,
            value = 300,
            limbs_needed = -1,
            legs = 1,
            amalgamy = 2
            )

    HUMAN_ARM = Action(
            "Join a Human Arm to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.HUMAN_ARM.value,
            value = 250,
            limbs_needed = -1,
            arms = 1,
            menace = -1
            )

    IVORY_FEMUR = Action(
            "Apply an Ivory Femur to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.IVORY_FEMUR.value,
            value = 6500,
            limbs_needed = -1,
            legs = 1
            )

    IVORY_HUMERUS = Action(
            "Apply an Ivory Humerus to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.IVORY_HUMERUS.value,
            value = 1500,
            limbs_needed = -1,
            arms = 1
            )

    JURASSIC_THIGH = Action(
            "Apply a Jurassic Thigh Bone to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.JURASSIC_FEMUR.value,
            value = 300,
            limbs_needed = -1,
            legs = 1,
            antiquity = 1
            )

    KNOTTED_HUMERUS = Action(
            "Apply a Knotted Humerus to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.KNOTTED_HUMERUS.value,
            value = 300,
            limbs_needed = -1,
            arms = 1,
            amalgamy = 1
            )

    OBSIDIAN_TAIL = Action(
            "Apply an Obsidian Chitin Tail to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.OBSIDIAN_TAIL.value,
            value = 500,
            tails_needed = -1,
            tails = 1,
            amalgamy = 1
            )

    PLASTER_TAIL_BONES = Action(
            "Apply Plaster Tail Bones to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.PLASTER_TAIL_BONES.value,
            value = 250,
            tails_needed = -1,
            tails = 1,
            implausibility = 1
            )

    TERROR_BIRD_WING = Action(
            "Add the Wing of a Young Terror Bird to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.TERROR_BIRD_WING.value,
            value = 250,
            limbs_needed = -1,
            wings = 1,
            antiquity = 1,
            menace = 1
            )

    TOMB_LION_TAIL = Action(
            "Apply a Tomb-Lion's Tail to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.TOMB_LION_TAIL.value,
            value = 250,
            tails_needed = -1,
            tails = 1,
            antiquity = 1
            )

    UNIDENTIFIED_THIGH = Action(
            "Apply an Unidentified Thigh Bone to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.UNIDENTIFIED_THIGH.value,
            value = 100,
            limbs_needed = -1,
            legs = 1
            )

    WITHERED_TAIL = Action(
            "Apply a Withered Tentacle as a tail on your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.WITHERED_TENTACLE.value,
            value = 250,
            tails_needed = -1,
            tails = 1,
            antiquity = -1
            )

    WITHERED_TENTACLE = Action(
            "Put a Withered Tentacle on your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.WITHERED_TENTACLE.value,
            value = 250,
            limbs_needed = -1,
            tentacles = 1,
            antiquity = -1
            )

    REMOVE_TAIL = Action(
            "Remove the tail from your (Skeleton Type)",
            cost = Cost.ACTION.value,
            tails = -1
            )

    # This sets Skeleton: Tails Needed to 0 and is implemented separately
    SKIP_TAILS = Action(
            "Decide your Tailless Animal needs no tail",
            cost = Cost.ACTION.value
            )

    def __str__(self):
        return str(self.value)
