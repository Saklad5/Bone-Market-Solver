__all__ = ['Skull']
__author__ = "Jeremy Saklad"

from enum import Enum

from .costs import Cost
from ..objects.action import Action

class Skull(Enum):
    """An action that is taken immediately after starting a skeleton."""

    BAPTIST_SKULL = Action(
            "Duplicate the skull of John the Baptist, if you can call that a skull",
            cost = Cost.ACTION.value + 500*Cost.BONE_FRAGMENT.value + 10*Cost.PEPPERCAPS.value,
            value = 1250,
            skulls_needed = -1,
            skulls = 1,
            counter_church = 1
            )

    BRASS_SKULL = Action(
            "Affix a Bright Brass Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.BRASS_SKULL.value + 200*Cost.NEVERCOLD_BRASS.value,
            value = 6500,
            skulls_needed = -1,
            skulls = 1,
            implausibility = 2
            )

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
            antiquity = 2
            )

    # Adds Exhaustion
    ENGRAVED_SKULL = Action(
            "Affix a Custom-Engraved Skull to your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.ENGRAVED_SKULL.value,
            value = 10000,
            skulls_needed = -1,
            skulls = 1,
            exhaustion = 2
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
            menace = 2
            )

    # Seeking the Name of Mr. Eaten
    OWN_SKULL = Action(
            "Duplicate your own skull and affix it here",
            cost = Cost.ACTION.value + 1000*Cost.BONE_FRAGMENT.value,
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
            menace = 2
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
            menace = 1
            )

    STYGIAN_IVORY = Action(
            "Use a Carved Ball of Stygian Ivory to cap off your (Skeleton Type)",
            cost = Cost.ACTION.value + Cost.STYGIAN_IVORY.value,
            value = 250,
            skulls_needed = -1
            )

    # Value and implausibility scale with repetition and are implemented separately
    VAKE_SKULL = Action(
            "Duplicate the Vake's skull and use it to decorate your (Skeleton Type)",
            cost = Cost.ACTION.value + 6000*Cost.BONE_FRAGMENT.value,
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
