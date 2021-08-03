__all__ = ['Action']
__author__ = "Jeremy Saklad"

class Action:
    """An action that affects a skeleton's qualities."""

    def __init__(self, name, cost, torso_style = None, value = 0, skulls_needed = 0, limbs_needed = 0, tails_needed = 0, skulls = 0, arms = 0, legs = 0, tails = 0, wings = 0, fins = 0, tentacles = 0, amalgamy = 0, antiquity = 0, menace = 0, implausibility = 0, counter_church = 0, exhaustion = 0):
        self.name = name

        # Cost in pennies of using this action, including the value of the actions spent
        self.cost = cost

        # Skeleton: Torso Style
        self.torso_style = torso_style

        # Approximate Value of Your Skeleton in Pennies
        self.value = value

        # Skeleton: Skulls Needed
        self.skulls_needed = skulls_needed

        # Skeleton: Limbs Needed
        self.limbs_needed = limbs_needed

        # Skeleton: Tails Needed
        self.tails_needed = tails_needed

        # Skeleton: Skulls
        self.skulls = skulls

        # Skeleton: Arms
        self.arms = arms

        # Skeleton: Legs
        self.legs = legs

        # Skeleton: Tails
        self.tails = tails

        # Skeleton: Wings
        self.wings = wings

        # Skeleton: Fins
        self.fins = fins

        # Skeleton: Tentacles
        self.tentacles = tentacles

        # Skeleton: Amalgamy
        self.amalgamy = amalgamy

        # Skeleton: Antiquity
        self.antiquity = antiquity

        # Skeleton: Menace
        self.menace = menace

        # Skeleton: Self-Evident Implausibility
        self.implausibility = implausibility

        # Skeleton: Support for a Counter-church Theology
        self.counter_church = counter_church

        # Bone Market Exhaustion
        self.exhaustion = exhaustion

    def __str__(self):
        return str(self.name)
