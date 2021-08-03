__all__ = ['Buyer']
__author__ = "Jeremy Saklad"

from enum import Enum

from data.costs import Cost
from objects.action import Action

class Buyer(Enum):
    """An action that converts a skeleton into revenue."""

    A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES = Action(
            "Sell a complete skeleton to the Bone Hoarder",
            cost = Cost.ACTION.value
            )

    A_NAIVE_COLLECTOR = Action(
            "Sell your Skeleton to a Naive Collector",
            cost = Cost.ACTION.value
            )

    A_FAMILIAR_BOHEMIAN_SCULPTRESS = Action(
            "Sell your Skeleton to the Sculptress",
            cost = Cost.ACTION.value
            )

    A_PEDAGOGICALLY_INCLINED_GRANDMOTHER = Action(
            "Sell your skeleton to a Pedagogically Inclined Grandmother",
            cost = Cost.ACTION.value
            )

    A_THEOLOGIAN_OF_THE_OLD_SCHOOL = Action(
            "Sell your Skeleton to the Theologian of the Old School",
            cost = Cost.ACTION.value
            )

    AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD = Action(
            "Sell your skeleton to an Enthusiast of the Ancient World",
            cost = Cost.ACTION.value
            )

    MRS_PLENTY = Action(
            "Sell a complete skeleton to Mrs Plenty",
            cost = Cost.ACTION.value
            )

    A_TENTACLED_SERVANT = Action(
            "Sell him your amalgamous skeleton",
            cost = Cost.ACTION.value
            )

    AN_INVESTMENT_MINDED_AMBASSADOR = Action(
            "Sell your skeleton to the Ambassador",
            cost = Cost.ACTION.value
            )

    A_TELLER_OF_TERRORS = Action(
            "Sell your skeleton to the Teller of Terrors",
            cost = Cost.ACTION.value
            )

    A_TENTACLED_ENTREPRENEUR = Action(
            "Sell to the Tentacled Entrepreneur",
            cost = Cost.ACTION.value
            )

    AN_AUTHOR_OF_GOTHIC_TALES = Action(
            "Sell to an Author of Gothic Tales",
            cost = Cost.ACTION.value
            )

    A_ZAILOR_WITH_PARTICULAR_INTERESTS = Action(
            "Sell your skeleton to a Zailor",
            cost = Cost.ACTION.value
            )

    A_RUBBERY_COLLECTOR = Action(
            "Sell to an Enthusiast of a Rubbery Menace",
            cost = Cost.ACTION.value
            )

    A_CONSTABLE = Action(
            "Sell to a Constable",
            cost = Cost.ACTION.value
            )

    AN_ENTHUSIAST_IN_SKULLS = Action(
            "Sell to the Cranial Enthusiast",
            cost = Cost.ACTION.value
            )

    A_DREARY_MIDNIGHTER = Action(
            "Sell to the Dreary Midnighter",
            cost = Cost.ACTION.value
            )

    A_COLOURFUL_PHANTASIST_BAZAARINE = Action(
            "Sell an amalgamous skeleton as a work of Bazaarine art",
            cost = Cost.ACTION.value
            )

    A_COLOURFUL_PHANTASIST_NOCTURNAL = Action(
            "Sell a menacing skeleton as a work of Nocturnal art",
            cost = Cost.ACTION.value
            )

    A_COLOURFUL_PHANTASIST_CELESTIAL = Action(
            "Sell an antique skeleton as a work of Celestial art",
            cost = Cost.ACTION.value
            )

    AN_INGENUOUS_MALACOLOGIST = Action(
            "Sell him a tentacle-laden skeleton",
            cost = Cost.ACTION.value
            )

    AN_ENTERPRISING_BOOT_SALESMAN = Action(
            "Sell to the Enterprising Boot Salesman",
            cost = Cost.ACTION.value
            )

    THE_DUMBWAITER_OF_BALMORAL = Action(
            "Export the Skeleton of a Neathy Bird",
            cost = Cost.ACTION.value
            )

    THE_CARPENTERS_GRANDDAUGHTER = Action(
            "Impress her with your own constructions",
            cost = Cost.ACTION.value
            )

    THE_TRIFLING_DIPLOMAT_ANTIQUITY = Action(
            "Sell the Diplomat an antique skeleton",
            cost = Cost.ACTION.value
            )

    THE_TRIFLING_DIPLOMAT_BIRD = Action(
            "Sell the Diplomat a fossil bird",
            cost = Cost.ACTION.value
            )

    THE_TRIFLING_DIPLOMAT_FISH = Action(
            "Sell the Diplomat a fossil fish",
            cost = Cost.ACTION.value
            )

    THE_TRIFLING_DIPLOMAT_INSECT = Action(
            "Sell the Diplomat a fossil insect",
            cost = Cost.ACTION.value
            )

    def __str__(self):
        return str(self.value)
