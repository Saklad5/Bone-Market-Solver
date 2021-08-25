__all__ = ['Skull']
__author__ = "Jeremy Saklad"

from enum import Enum

from .costs import Cost
from ..objects.action import Action
from ..challenge_functions import narrow_challenge, mean_outcome
from ..read_char import Char

class Skull(Enum):
    """An action that is taken immediately after starting a skeleton."""

    BAPTIST_SKULL = Action(
            "Duplicate the skull of John the Baptist, if you can call that a skull",
            cost = Cost.ACTION.value * 1 / narrow_challenge(6, Char.ARTISAN_OF_RED_SCIENCE.value) + 500*Cost.BONE_FRAGMENT.value + 10*Cost.PEPPERCAPS.value,
            value = 1250,
            skulls_needed = -1,
            skulls = 1,
            counter_church = 1
            )

    BRASS_SKULL = Action(
            "Affix a Bright Brass Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.BRASS_SKULL.value + mean_outcome(200*Cost.NEVERCOLD_BRASS.value, 0, narrow_challenge(6, Char.MITHRIDACY.value)),
            value = mean_outcome(6500, 6000, narrow_challenge(6, Char.MITHRIDACY.value)),
            skulls_needed = -1,
            skulls = 1,
            implausibility = mean_outcome(2, 6, narrow_challenge(6, Char.MITHRIDACY.value)),
            )

    # TODO
    CORAL_SKULL = Action(
            "Affix a Skull in Coral to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.CORAL_SKULL.value + Cost.SCINTILLACK.value,
            value = 1750,
            skulls_needed = -1,
            skulls = 1,
            amalgamy = 2
            )

    DOUBLED_SKULL = Action(
            "Affix a Doubled Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.DOUBLED_SKULL.value,
            value = 6250,
            skulls_needed = -1,
            skulls = 2,
            amalgamy = 1,
            antiquity = mean_outcome(2, 1, narrow_challenge(4, Char.MONSTROUS_ANATOMY.value))
            )

    # Adds Exhaustion
    ENGRAVED_SKULL = Action(
            "Affix a Custom-Engraved Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.ENGRAVED_SKULL.value,
            value = 10000,
            skulls_needed = -1,
            skulls = 1,
            exhaustion = 2,
            implausibility = mean_outcome(0, 2, narrow_challenge(4, Char.MITHRIDACY.value)),
            )

    EYELESS_SKULL = Action(
            "Affix an Eyeless Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.EYELESS_SKULL.value,
            value = 3000,
            skulls_needed = -1,
            skulls = 1,
            menace = 2
            )

    HORNED_SKULL = Action(
            "Affix a Horned Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.HORNED_SKULL.value,
            value = 1250,
            skulls_needed = -1,
            skulls = 1,
            antiquity = 1,
            menace = mean_outcome(2, 1, narrow_challenge(6, Char.MONSTROUS_ANATOMY.value))
            )

    # Seeking the Name of Mr. Eaten
    OWN_SKULL = Action(
            "Duplicate your own skull and affix it here",
            cost = Cost.ACTION.value * 1 / narrow_challenge(6, Char.ARTISAN_OF_RED_SCIENCE.value) + 1000*Cost.BONE_FRAGMENT.value,
            value = -250,
            skulls_needed = -1,
            skulls = 1
            )

    PENTAGRAMMIC_SKULL = Action(
            "Affix a Pentagrammic Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.PENTAGRAMMIC_SKULL.value,
            value = 1250,
            skulls_needed = -1,
            skulls = 1,
            amalgamy = 2,
            menace = 1
            )

    PLATED_SKULL = Action(
            "Affix a Plated Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.PLATED_SKULL.value,
            value = 2500,
            skulls_needed = -1,
            skulls = 1,
            menace = mean_outcome(2, 1, narrow_challenge(4, Char.MONSTROUS_ANATOMY.value))
            )

    RUBBERY_SKULL = Action(
            "Affix a Rubbery Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.RUBBERY_SKULL.value,
            value = 600,
            skulls_needed = -1,
            skulls = 1,
            amalgamy = 1
            )

    SABRE_TOOTHED_SKULL = Action(
            "Affix a Sabre-toothed Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.SABRE_TOOTHED_SKULL.value,
            value = 6250,
            skulls_needed = -1,
            skulls = 1,
            antiquity = 1,
            menace = mean_outcome(1, 0, narrow_challenge(6, Char.MONSTROUS_ANATOMY.value))
            )

    STYGIAN_IVORY = Action(
            "Use a Carved Ball of Stygian Ivory to cap off your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.STYGIAN_IVORY.value,
            value = 250,
            skulls_needed = -1,
            implausibility = mean_outcome(0, 2, narrow_challenge(6, Char.MITHRIDACY.value))
            )

    VAKE_SKULL = Action(
            "Duplicate the Vake's skull and use it to decorate your (Skeleton Type)",
            cost = Cost.ACTION.value + 6000*Cost.BONE_FRAGMENT.value + mean_outcome(0, Cost.ACTION.value + 300*Cost.BONE_FRAGMENT.value, narrow_challenge(6, Char.ARTISAN_OF_RED_SCIENCE.value)),
            value = 6500,
            skulls_needed = -1,
            skulls = 1,
            menace = 3
            )

    # Licentiate
    VICTIM_SKULL = Action(
            "Cap this with a victim’s skull",
            cost = Cost.ACTION.value,
            value = 250,
            skulls_needed = -1,
            skulls = 1
            )

    def __str__(self):
        return str(self.value)
