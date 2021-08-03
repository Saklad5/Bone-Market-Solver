__all__ = ['OccasionalBuyer']
__author__ = "Jeremy Saklad"

from enum import Enum

from data.buyers import Buyer

class OccasionalBuyer(Enum):
    """Which of several unusual buyers are available."""

    AN_ENTHUSIAST_IN_SKULLS = [Buyer.AN_ENTHUSIAST_IN_SKULLS]

    A_DREARY_MIDNIGHTER = [Buyer.A_DREARY_MIDNIGHTER]

    A_COLOURFUL_PHANTASIST = [
            Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE,
            Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL,
            Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL,
            ]

    AN_INGENUOUS_MALACOLOGIST = [Buyer.AN_INGENUOUS_MALACOLOGIST]

    AN_ENTERPRISING_BOOT_SALESMAN = [Buyer.AN_ENTERPRISING_BOOT_SALESMAN]
