import functools
import enum
import os

from enum import auto
from ortools.sat.python import cp_model

# This multiplier is applied to the profit margin to avoid losing precision due to rounding.
PROFIT_MARGIN_MULTIPLIER = 10000000

# This is the highest number of attribute to calculate fractional exponents for.
MAXIMUM_ATTRIBUTE = 100

# This is a constant used to calculate difficulty checks. You almost certainly do not need to change this.
DIFFICULTY_SCALER = 0.6

# This is the effective level of Shadowy used for attempting to sell.
SHADOWY_LEVEL = 300

# The maximum number of pennies that should be invested in this skeleton.
MAXIMUM_COST = cp_model.INT32_MAX

# The maximum Exhaustion that this skeleton should generate.
MAXIMUM_EXHAUSTION = 4


# The number of pennies needed to produce a quality.
class Cost(enum.Enum):
    # This is your baseline EPA: the pennies you could generate using an action for a generic grind.
    ACTION = 400

    # Antique Mystery
    ANTIQUE_MYSTERY = 1250

    # Favours: Bohemians
    # Various opportunity cards
    BOHEMIAN_FAVOURS = ACTION

    # Bone Fragment
    BONE_FRAGMENT = 1

    # Cartographer's Hoard
    CARTOGRAPHERS_HOARD = 31250

    # Favours: The Church
    # Various opportunity cards
    CHURCH_FAVOURS = ACTION

    # Collection Note: There's a 'Package' in London
    # Station VIII Lab
    COLLECTION_NOTE = ACTION

    # Volume of Collated Research
    COLLATED_RESEARCH = 250

    # Deep-Zee Catch
    # Spear-fishing at the bottom of the Evenlode, 7 at a time
    DEEP_ZEE_CATCH = ACTION/7

    # Crustacean Pincer
    # Ealing Gardens Butcher, 2 at a time
    CRUSTACEAN_PINCER = (ACTION + DEEP_ZEE_CATCH)/2

    # Femur of a Surface Deer
    # Dumbwaiter of Balmoral, 25 at a time
    DEER_FEMUR = ACTION/25

    # Favours: The Docks
    # Various opportunity cards
    DOCK_FAVOURS = ACTION

    # Eyeless Skull
    # No consistent source
    EYELESS_SKULL = cp_model.INT32_MAX/2

    # Holy Relic of the Thigh of Saint Fiacre
    # Jericho Locks statue, 2 at a time
    FIACRE_THIGH = (ACTION + 4*CHURCH_FAVOURS)/2

    # Fin Bones, Collected
    # Hunt and dissect Pinewood Shark, 40 at a time
    FIN_BONES = (11*ACTION)/40

    # Amber-Crusted Fin
    # Helicon House
    AMBER_FIN = ACTION + 10*FIN_BONES

    # Five-Pointed Ribcage
    # Upwards
    FIVE_POINTED_RIBCAGE = 9*ACTION + CARTOGRAPHERS_HOARD

    # Esteem of the Guild
    # Jericho Parade, 2 at a time
    GUILD_ESTEEM = (ACTION + 5*DOCK_FAVOURS)/2

    # Skull in Coral
    # Persephone, 1-2 at a time
    CORAL_SKULL = 1.5*(2*ACTION + 3*GUILD_ESTEEM)

    # Headless Skeleton
    # These are accumulated while acquiring other qualities.
    HEADLESS_SKELETON = 0

    # Hinterland Scrip
    HINTERLAND_SCRIP = 50

    # Fossilised Forelimb
    # Anning and Daughters
    FOSSILISED_FORELIMB = 50*HINTERLAND_SCRIP

    # Hedonist
    # Handsome Townhouse, 3cp at a time
    HEDONIST_CP = ACTION/3

    # Human Arm
    # These are accumulated while acquiring other qualities.
    HUMAN_ARM = 0

    # Crate of Incorruptible Biscuits
    INCORRUPTIBLE_BISCUITS = 250

    # Inkling of Identity
    INKLING_OF_IDENTITY = 10

    # A Custom-Engraved Skull
    # Feast of the Exceptional Rose, sent by one player and accepted by another
    ENGRAVED_SKULL = 2*ACTION + 200*INKLING_OF_IDENTITY

    # Ivory Humerus
    # Ealing Gardens statue, 2 at a time
    IVORY_HUMERUS = (ACTION + 4*BOHEMIAN_FAVOURS)/2

    # Jade Fragment
    JADE_FRAGMENT = 1

    # Femur of a Jurassic Beast
    # Brawling for yourself, large Bone Market crate, 12 at a time
    JURASSIC_FEMUR = (10*ACTION)/12

    # Knotted Humerus
    # These are accumulated while acquiring other qualities.
    KNOTTED_HUMERUS = 0

    # Nevercold Brass Sliver
    NEVERCOLD_BRASS = 1

    # Obsidian Chitin Tail
    # No consistent source
    OBSIDIAN_TAIL = cp_model.INT32_MAX/2

    # Parabolan Orange-apple
    # Parabolan Base-camp, electricity and hedonism, 2 at a time
    ORANGE_APPLE = (2*ACTION + 100*BONE_FRAGMENT + 21*HEDONIST_CP)/2

    # Ivory Femur
    # Bohemian Sculptress
    IVORY_FEMUR = ACTION + 750*BONE_FRAGMENT + 3*ORANGE_APPLE

    # Penny
    PENNY = 1

    # Bright Brass Skull
    # Merrigans Exchange
    BRASS_SKULL = 6250*PENNY

    # Pentagrammic Skull
    # Upwards
    PENTAGRAMMIC_SKULL = 9*ACTION

    # Hand-picked Peppercaps
    PEPPERCAPS = HINTERLAND_SCRIP

    # Knob of Scintillack
    SCINTILLACK = 250

    # Searing Enigma
    SEARING_ENIGMA = 6250

    # Carved Ball of Stygian Ivory
    STYGIAN_IVORY = 250

    # Preserved Surface Blooms
    SURFACE_BLOOMS = 250

    # Consignment of Scintillack Snuff
    # Laboratory Manufacturing
    SCINTILLACK_SNUFF = (ACTION + 8*SCINTILLACK + SURFACE_BLOOMS)/2

    # Elation at Feline Oration
    # Pinnock
    ELATION_AT_FELINE_ORATION = ACTION + 2*ANTIQUE_MYSTERY + COLLECTION_NOTE + 2*SCINTILLACK_SNUFF

    # Oil of Companionship
    # Station VIII Lab
    OIL_OF_COMPANIONSHIP = ACTION + ELATION_AT_FELINE_ORATION

    # Survey of the Neath's Bones
    # Laboratory Research
    SURVEY = 6*ACTION/25

    # Plaster Tail Bones
    # Carpenter's Granddaughter, 2 at a time
    PLASTER_TAIL_BONES = (ACTION + 10*SURVEY)/2

    # Human Ribcage
    # Ealing Gardens
    HUMAN_RIBCAGE = ACTION + 15*SURVEY

    # Palaeontological Discovery
    # Plain of Thirsty Grasses
    PALAEONTOLOGICAL_DISCOVERY = (ACTION + 140*SURVEY)/6

    # Helical Thighbone
    # Results of Excavation, 6 at a time
    HELICAL_THIGH = (2*PALAEONTOLOGICAL_DISCOVERY)/6

    # Leviathan Frame
    # Results of Excavation
    LEVIATHAN_FRAME = 25*PALAEONTOLOGICAL_DISCOVERY

    # Thorned Ribcage
    # Iron-Toothed Terror Bird
    THORNED_RIBCAGE = 6*ACTION

    # Flourishing Ribcage
    # Helicon House
    FLOURISHING_RIBCAGE = ACTION + HUMAN_RIBCAGE + THORNED_RIBCAGE

    # Time Remaining in the Woods
    # Compel Ghillie, 5 at a time
    TIME_REMAINING_IN_THE_WOODS = (ACTION + 4*COLLATED_RESEARCH)/5

    # Observation: Red Deer
    # Balmoral Woods
    DEER_OBSERVATION = 11*ACTION + 10*TIME_REMAINING_IN_THE_WOODS

    # Mammoth Ribcage
    # Keeper of the Marigold Menagerie
    MAMMOTH_RIBCAGE = ACTION + DEER_OBSERVATION

    # Observation: Fox
    # Balmoral Woods
    FOX_OBSERVATION = 10*ACTION + 8*TIME_REMAINING_IN_THE_WOODS

    # Doubled Skull
    # Keeper of the Marigold Menagerie
    DOUBLED_SKULL = ACTION + FOX_OBSERVATION

    # Observation: Grouse
    # Balmoral Woods
    GROUSE_OBSERVATION = 8*ACTION + 7*TIME_REMAINING_IN_THE_WOODS

    # Skeleton with Seven Necks
    # Keeper of the Marigold Menagerie
    SKELETON_WITH_SEVEN_NECKS = ACTION + GROUSE_OBSERVATION

    # Nodule of Trembling Amber
    TREMBLING_AMBER = 1250

    # Ribcage with a Bouquet of Eight Spines
    # Helicon House
    RIBCAGE_WITH_EIGHT_SPINES = ACTION + 3*SEARING_ENIGMA + THORNED_RIBCAGE + 3*TREMBLING_AMBER

    # Rubbery Skull
    # Flute Street, including travel due to quality cap
    RUBBERY_SKULL = 25*ACTION

    # Rumour of the Upper River
    RUMOUR_OF_THE_UPPER_RIVER = 250

    # Jet Black Stinger
    # Hunting with Sophia's, 5 at a time
    BLACK_STINGER = (ACTION + 5*RUMOUR_OF_THE_UPPER_RIVER)/5

    # Prismatic Frame
    # Expedition at Station VIII
    PRISMATIC_FRAME = ACTION + OIL_OF_COMPANIONSHIP + 98*RUMOUR_OF_THE_UPPER_RIVER

    # Unidentified Thigh Bone
    # These are accumulated while acquiring other qualities.
    UNIDENTIFIED_THIGH = 0

    # Nodule of Warm Amber
    WARM_AMBER = 10

    # Albatross Wing
    # Ealing Gardens Butcher, 2 at a time
    ALBATROSS_WING = (ACTION + 2000*BONE_FRAGMENT + 25*WARM_AMBER)/2

    # Bat Wing
    # Ealing Gardens Butcher, 2 at a time
    BAT_WING = (ACTION + 100*BONE_FRAGMENT + 2*WARM_AMBER)/2

    # Horned Skull
    # Ealing Gardens Butcher
    HORNED_SKULL = ACTION + 1000*BONE_FRAGMENT + 5*WARM_AMBER

    # Plated Skull
    # Ealing Gardens Butcher
    PLATED_SKULL = ACTION + 1750*BONE_FRAGMENT + INCORRUPTIBLE_BISCUITS + 25*WARM_AMBER

    # Sabre-toothed Skull
    # Ealing Gardens Butcher
    SABRE_TOOTHED_SKULL = ACTION + 4900*BONE_FRAGMENT + 125*WARM_AMBER

    # Wing of a Young Terror Bird
    # Ealing Gardens Butcher, 2 at a time
    TERROR_BIRD_WING = (ACTION + 100*BONE_FRAGMENT + 25*WARM_AMBER)/2

    # Tomb-Lion's Tail
    # Ealing Gardens Butcher
    TOMB_LION_TAIL = ACTION + 200*BONE_FRAGMENT + 2*WARM_AMBER

    # Warbler Skeleton
    # Ealing Gardens Butcher
    WARBLER_SKELETON = ACTION + 130*BONE_FRAGMENT + 2*WARM_AMBER

    # Withered Tentacle
    # Helicon House, 3 at a time
    WITHERED_TENTACLE = (ACTION + 5*WARM_AMBER)/3


# Adds a fully-reified implication using an intermediate Boolean variable.
def NewIntermediateBoolVar(self, name, expression, domain):
    intermediate = self.NewBoolVar(name)
    self.AddLinearExpressionInDomain(expression, domain).OnlyEnforceIf(intermediate)
    self.AddLinearExpressionInDomain(expression, domain.Complement()).OnlyEnforceIf(intermediate.Not())
    return intermediate

setattr(cp_model.CpModel, 'NewIntermediateBoolVar', NewIntermediateBoolVar)
del NewIntermediateBoolVar


# Adds an approximate exponentiation equality using a lookup table.
# Set `upto` to a value that is unlikely to come into play.
def AddApproximateExponentiationEquality(self, target, var, exp, upto):
    return self.AddAllowedAssignments([target, var], [(int(base**exp), base) for base in range(upto + 1)])

setattr(cp_model.CpModel, 'AddApproximateExponentiationEquality', AddApproximateExponentiationEquality)
del AddApproximateExponentiationEquality


# Adds a multiplication equality for any number of terms using intermediate variables.
def AddGeneralMultiplicationEquality(self, target, *variables):
    # This is used for producing unique names for intermediate variables.
    term_index = 1

    def function(a, b):
        nonlocal term_index
        intermediate = self.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, '{} term {}'.format(target.Name(), term_index))
        term_index += 1
        self.AddMultiplicationEquality(intermediate, [a, b])
        return intermediate

    product = functools.reduce(function, variables)
    return self.Add(target == product)

setattr(cp_model.CpModel, 'AddGeneralMultiplicationEquality', AddGeneralMultiplicationEquality)
del AddGeneralMultiplicationEquality


# A way to convert a skeleton into revenue.
class Buyer(enum.Enum):
    A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES = auto()
    A_NAIVE_COLLECTOR = auto()
    A_FAMILIAR_BOHEMIAN_SCULPTRESS = auto()
    A_PEDAGOGICALLY_INCLINED_GRANDMOTHER = auto()
    A_THEOLOGIAN_OF_THE_OLD_SCHOOL = auto()
    AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD = auto()
    MRS_PLENTY = auto()
    A_TENTACLED_SERVANT = auto()
    AN_INVESTMENT_MINDED_AMBASSADOR = auto()
    A_TELLER_OF_TERRORS = auto()
    A_TENTACLED_ENTREPRENEUR = auto()
    AN_AUTHOR_OF_GOTHIC_TALES = auto()
    A_ZAILOR_WITH_PARTICULAR_INTERESTS = auto()
    A_RUBBERY_COLLECTOR = auto()
    A_CONSTABLE = auto()
    AN_ENTHUSIAST_IN_SKULLS = auto()
    A_DREARY_MIDNIGHTER = auto()
    THE_DUMBWAITER_OF_BALMORAL = auto()

BUYER = Buyer.AN_ENTHUSIAST_IN_SKULLS

# An action that affects a skeleton's qualities.
class Action:
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


# Actions that initiate a skeleton.
class Torso(enum.Enum):
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
    # VICTIM_SKELETON = Action(
    #        "Supply a skeleton of your own",
    #        cost = Cost.ACTION.value,
    #        torso_style = 10,
    #        value = 250,
    #        skulls_needed = 1,
    #        arms = 2,
    #        legs = 2
    #        )

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

    LEVIATHAN_FRAME = Action("Build on the Leviathan Frame",
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

    def __str__(self):
        return str(self.value)


# Actions that are taken immediately after starting a skeleton.
class Skull(enum.Enum):
    BAPTIST_SKULL = Action(
            "Duplicate the skull of John the Baptist, if you can call that a skull",
            cost = Cost.ACTION.value + 500*Cost.BONE_FRAGMENT.value + 10*Cost.PEPPERCAPS.value,
            value = 1500,
            skulls_needed = -1,
            skulls = 1,
            counter_church = 2
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
    # ENGRAVED_SKULL = Action(
    #         "Affix a Custom-Engraved Skull to your (Skeleton Type)",
    #         cost = Cost.ACTION.value + Cost.ENGRAVED_SKULL.value,
    #         value = 10000,
    #         skulls_needed = -1,
    #         skulls = 1,
    #         exhaustion = 2
    #         )

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
    # OWN_SKULL = Action(
    #         "Duplicate your own skull and affix it here",
    #         cost = Cost.ACTION.value + 1000*Cost.BONE_FRAGMENT.value,
    #         value = -250,
    #         skulls_needed = -1,
    #         skulls = 1
    #         )

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

    VAKE_SKULL = Action(
            "Duplicate the Vake's skull and use it to decorate your (Skeleton Type)",
            cost = Cost.ACTION.value + 6000*Cost.BONE_FRAGMENT.value,
            value = 6500,
            skulls_needed = -1,
            skulls = 1,
            menace = 3
            )

    # Licentiate
    # VICTIM_SKULL = Action(
    #         "Cap this with a victim’s skull",
    #         cost = Cost.ACTION.value,
    #         value = 250,
    #         skulls_needed = -1,
    #         skulls = 1
    #         )

    def __str__(self):
        return str(self.value)

# Actions that are taken once all skulls are added to a skeleton.
class Appendage(enum.Enum):
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

    BLACK_STINGER = Action("Apply a Jet Black Stinger to your (Skeleton Type)",
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
            value = 150,
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


# Actions that are taken after all parts have been added to a skeleton.
class Adjustment(enum.Enum):
    CARVE_AWAY_AGE = Action(
            "Carve away some evidence of age",
            cost = Cost.ACTION.value,
            antiquity = -2
            )

    DISGUISE_AMALGAMY = Action(
            "Disguise the amalgamy of this piece",
            cost = Cost.ACTION.value + Cost.JADE_FRAGMENT.value,
            amalgamy = -2
            )

    MAKE_LESS_DREADFUL = Action(
            "Make your skeleton less dreadful",
            cost = Cost.ACTION.value,
            menace = -2
            )

    def __str__(self):
        return str(self.value)


# Which kind of skeleton is to be declared.
class Declaration(enum.Enum):
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

# The current value of Zoological Mania, which grants a 10% bonus to value for a certain declaration.
ZOOLOGICAL_MANIA = Declaration.AMPHIBIAN

# Which skeleton attribute is currently boosted.
class Fluctuation(enum.Enum):
    ANTIQUITY = 1
    AMALGAMY = 2

# The current value of Bone Market Fluctuations, which grants various bonuses to certain buyers.
BONE_MARKET_FLUCTUATIONS = Fluctuation.AMALGAMY 

def Solve():
    model = cp_model.CpModel()

    actions = {}

    # Torso
    for torso in Torso:
        actions[torso] = model.NewBoolVar(torso.value.name)

    # Skull
    for skull in Skull:
        actions[skull] = model.NewIntVar(0, cp_model.INT32_MAX, skull.value.name)

    # Appendage
    for appendage in Appendage:
        if appendage == Appendage.SKIP_TAILS:
            actions[appendage] = model.NewBoolVar(appendage.value.name)
        else:
            actions[appendage] = model.NewIntVar(0, cp_model.INT32_MAX, appendage.value.name)

    # Adjustment
    for adjustment in Adjustment:
        actions[adjustment] = model.NewIntVar(0, cp_model.INT32_MAX, adjustment.value.name)

    # Declaration
    for declaration in Declaration:
        actions[declaration] = model.NewBoolVar(declaration.value.name)

    # One torso
    model.Add(cp_model.LinearExpr.Sum([value for (key, value) in actions.items() if isinstance(key, Torso)]) == 1)

    # One declaration
    model.Add(cp_model.LinearExpr.Sum([value for (key, value) in actions.items() if isinstance(key, Declaration)]) == 1)

    # Value calculation
    original_value = model.NewIntVar(0, cp_model.INT32_MAX, 'original value')
    model.Add(original_value == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.value for action in actions.keys()]))

    multiplied_value = model.NewIntVar(0, cp_model.INT32_MAX*11, "multiplied value")
    model.Add(multiplied_value == original_value*11).OnlyEnforceIf(actions[ZOOLOGICAL_MANIA])
    model.Add(multiplied_value == original_value*10).OnlyEnforceIf(actions[ZOOLOGICAL_MANIA].Not())

    value = model.NewIntVar(0, cp_model.INT32_MAX, 'value')
    model.AddDivisionEquality(value, multiplied_value, 10)

    del original_value, multiplied_value


    # Torso Style calculation
    torso_style = model.NewIntVarFromDomain(cp_model.Domain.FromValues([torso.value.torso_style for torso in Torso]), 'torso_style')
    for torso, torso_variable in {key: value for (key, value) in actions.items() if isinstance(key, Torso)}.items():
        model.Add(torso_style == torso.value.torso_style).OnlyEnforceIf(torso_variable)

    # Skulls calculation
    skulls = model.NewIntVar(0, cp_model.INT32_MAX, 'skulls')
    model.Add(skulls == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.skulls for action in actions.keys()]))

    # Arms calculation
    arms = model.NewIntVar(0, cp_model.INT32_MAX, 'arms')
    model.Add(arms == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.arms for action in actions.keys()]))

    # Legs calculation
    legs = model.NewIntVar(0, cp_model.INT32_MAX, 'legs')
    model.Add(legs == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.legs for action in actions.keys()]))

    # Tails calculation
    tails = model.NewIntVar(0, cp_model.INT32_MAX, 'tails')
    model.Add(tails == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tails for action in actions.keys()]))

    # Wings calculation
    wings = model.NewIntVar(0, cp_model.INT32_MAX, 'wings')
    model.Add(wings == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.wings for action in actions.keys()]))

    # Fins calculation
    fins = model.NewIntVar(0, cp_model.INT32_MAX, 'fins')
    model.Add(fins == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.fins for action in actions.keys()]))

    # Tentacles calculation
    tentacles = model.NewIntVar(0, cp_model.INT32_MAX, 'tentacles')
    model.Add(tentacles == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tentacles for action in actions.keys()]))

    # Amalgamy calculation
    amalgamy = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'amalgamy')
    model.Add(amalgamy == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.amalgamy for action in actions.keys()]))

    # Antiquity calculation
    antiquity = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'antiquity')
    model.Add(antiquity == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.antiquity for action in actions.keys()]))

    # Menace calculation
    menace = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'menace')
    model.Add(menace == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.menace for action in actions.keys()]))

    # Implausibility calculation
    implausibility = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'implausibility')
    model.Add(implausibility == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.implausibility for action in actions.keys()]))


    # Counter-church calculation
    # Calculate amount of Counter-church from Holy Relics of the Thigh of Saint Fiacre
    holy_relic = actions[Appendage.FIACRE_THIGH]
    torso_style_divided_by_ten = model.NewIntVar(0, cp_model.INT32_MAX, 'torso style divided by ten')
    model.AddDivisionEquality(torso_style_divided_by_ten, torso_style, 10)
    holy_relic_counter_church = model.NewIntVar(0, cp_model.INT32_MAX, 'holy relic counter-church')
    model.AddMultiplicationEquality(holy_relic_counter_church, [holy_relic, torso_style_divided_by_ten])

    counter_church = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'counter-church')
    model.Add(counter_church == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.counter_church for action in actions.keys()]) + holy_relic_counter_church)

    del holy_relic, torso_style_divided_by_ten, holy_relic_counter_church


    # Exhaustion calculation
    exhaustion = model.NewIntVar(0, MAXIMUM_EXHAUSTION, 'exhaustion')

    # Exhaustion added by certain buyers
    added_exhaustion = model.NewIntVar(0, MAXIMUM_EXHAUSTION, 'added exhaustion')
    model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.exhaustion for action in actions.keys()]) + added_exhaustion)


    # Profit intermediate variables
    value_remainder = model.NewIntVar(0, cp_model.INT32_MAX, 'value remainder')
    primary_revenue = model.NewIntVar(0, cp_model.INT32_MAX, 'primary revenue')
    secondary_revenue = model.NewIntVar(0, cp_model.INT32_MAX, 'secondary revenue')
    total_revenue = model.NewIntVar(0, cp_model.INT32_MAX*2, 'total revenue')
    model.Add(total_revenue == cp_model.LinearExpr.Sum([primary_revenue, secondary_revenue]))


    # Cost
    # Calculate value of actions needed to sell the skeleton.
    difficulty_level = model.NewIntVar(0, cp_model.INT32_MAX, 'difficulty level')

    non_zero_difficulty_level = model.NewIntVar(1, cp_model.INT32_MAX, 'non-zero difficulty level')
    model.AddMaxEquality(non_zero_difficulty_level, [difficulty_level, 1])

    sale_actions_times_action_value = model.NewIntVar(0, cp_model.INT32_MAX, 'sale actions times action value')
    model.AddDivisionEquality(sale_actions_times_action_value, model.NewConstant(round(DIFFICULTY_SCALER*SHADOWY_LEVEL*Cost.ACTION.value)), non_zero_difficulty_level)
    abstract_sale_cost = model.NewIntVar(0, cp_model.INT32_MAX, 'abstract sale cost')
    model.AddDivisionEquality(abstract_sale_cost, Cost.ACTION.value**2, sale_actions_times_action_value)
    sale_cost = model.NewIntVar(0, cp_model.INT32_MAX, 'sale cost')
    model.AddMaxEquality(sale_cost, [abstract_sale_cost, Cost.ACTION.value])

    del non_zero_difficulty_level, sale_actions_times_action_value, abstract_sale_cost


    # Calculate cost of adding joints
    # This is a partial sum formula.
    add_joints_amber_cost = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost')

    add_joints = actions[Appendage.ADD_JOINTS]

    base_joints = model.NewIntVar(0, cp_model.INT32_MAX, 'base joints')
    model.Add(base_joints == cp_model.LinearExpr.ScalProd([value for (key, value) in actions.items() if isinstance(key, Torso)], [torso.value.limbs_needed for torso in Torso]))

    add_joints_amber_cost_multiple = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple')

    add_joints_amber_cost_multiple_first_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple first term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_first_term, 25, base_joints, base_joints, add_joints)

    add_joints_amber_cost_multiple_second_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple second term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_second_term, 100, base_joints, add_joints, add_joints)

    add_joints_amber_cost_multiple_third_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple third term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_third_term, 100, base_joints, add_joints)

    add_joints_amber_cost_multiple_fourth_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple fourth term')
    add_joints_amber_cost_multiple_fourth_term_numerator = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple fourth term numerator')
    add_joints_amber_cost_multiple_fourth_term_numerator_first_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple fourth term numerator first term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_fourth_term_numerator_first_term, 400, add_joints, add_joints, add_joints)
    model.Add(add_joints_amber_cost_multiple_fourth_term_numerator == add_joints_amber_cost_multiple_fourth_term_numerator_first_term + 200*add_joints)
    model.AddDivisionEquality(add_joints_amber_cost_multiple_fourth_term, add_joints_amber_cost_multiple_fourth_term_numerator, 3)
    del add_joints_amber_cost_multiple_fourth_term_numerator, add_joints_amber_cost_multiple_fourth_term_numerator_first_term

    add_joints_amber_cost_multiple_fifth_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple fifth term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_fifth_term, 200, add_joints, add_joints)

    model.Add(add_joints_amber_cost_multiple == add_joints_amber_cost_multiple_first_term + add_joints_amber_cost_multiple_second_term - add_joints_amber_cost_multiple_third_term + add_joints_amber_cost_multiple_fourth_term - add_joints_amber_cost_multiple_fifth_term)

    del add_joints_amber_cost_multiple_first_term, add_joints_amber_cost_multiple_second_term, add_joints_amber_cost_multiple_third_term, add_joints_amber_cost_multiple_fourth_term, add_joints_amber_cost_multiple_fifth_term

    model.AddGeneralMultiplicationEquality(add_joints_amber_cost, add_joints, add_joints_amber_cost_multiple, Cost.WARM_AMBER.value)

    del add_joints, add_joints_amber_cost_multiple


    cost = model.NewIntVar(0, MAXIMUM_COST, 'cost')
    model.Add(cost == cp_model.LinearExpr.ScalProd(actions.values(), [int(action.value.cost) for action in actions.keys()]) + add_joints_amber_cost + sale_cost)

    del sale_cost, add_joints_amber_cost


    # Type of skeleton
    skeleton_in_progress = model.NewIntVar(0, cp_model.INT32_MAX, 'skeleton in progress')

    # Chimera
    model.Add(skeleton_in_progress == 100) \
            .OnlyEnforceIf(actions[Declaration.CHIMERA])
    # Humanoid
    model.Add(skeleton_in_progress == 110) \
            .OnlyEnforceIf(actions[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('humanoid antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 0])))
    # Ancient Humanoid (UNCERTAIN)
    model.Add(skeleton_in_progress == 111) \
            .OnlyEnforceIf(actions[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('ancient humanoid antiquity', antiquity, cp_model.Domain.FromFlatIntervals([1, 5])))
    # Neanderthal
    model.Add(skeleton_in_progress == 112) \
            .OnlyEnforceIf(actions[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('neanderthal antiquity', antiquity, cp_model.Domain.FromFlatIntervals([6, cp_model.INT_MAX])))
    # Ape (UNCERTAIN)
    model.Add(skeleton_in_progress == 120) \
            .OnlyEnforceIf(actions[Declaration.APE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('ape antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Primordial Ape (UNCERTAIN)
    model.Add(skeleton_in_progress == 121) \
            .OnlyEnforceIf(actions[Declaration.APE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('primordial ape antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, cp_model.INT_MAX])))
    # Monkey
    model.Add(skeleton_in_progress == 125) \
            .OnlyEnforceIf(actions[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('monkey antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 0])))
    # Catarrhine Monkey (UNCERTAIN)
    model.Add(skeleton_in_progress == 126) \
            .OnlyEnforceIf(actions[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('catarrhine monkey 126 antiquity', antiquity, cp_model.Domain.FromFlatIntervals([1, 8])))
    # Catarrhine Monkey
    model.Add(skeleton_in_progress == 128) \
            .OnlyEnforceIf(actions[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('catarrhine monkey 128 antiquity', antiquity, cp_model.Domain.FromFlatIntervals([9, cp_model.INT_MAX])))
    # Crocodile
    model.Add(skeleton_in_progress == 160) \
            .OnlyEnforceIf(actions[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('crocodile antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Dinosaur
    model.Add(skeleton_in_progress == 161) \
            .OnlyEnforceIf(actions[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('dinosaur antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 4])))
    # Mesosaur (UNCERTAIN)
    model.Add(skeleton_in_progress == 162) \
            .OnlyEnforceIf(actions[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('mesosaur antiquity', antiquity, cp_model.Domain.FromFlatIntervals([5, cp_model.INT_MAX])))
    # Toad
    model.Add(skeleton_in_progress == 170) \
            .OnlyEnforceIf(actions[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('toad antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Primordial Amphibian
    model.Add(skeleton_in_progress == 171) \
            .OnlyEnforceIf(actions[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('primordial amphibian antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 4])))
    # Temnospondyl
    model.Add(skeleton_in_progress == 172) \
            .OnlyEnforceIf(actions[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('temnospondyl antiquity', antiquity, cp_model.Domain.FromFlatIntervals([5, cp_model.INT_MAX])))
    # Owl
    model.Add(skeleton_in_progress == 180) \
            .OnlyEnforceIf(actions[Declaration.BIRD]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('owl antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Archaeopteryx
    model.Add(skeleton_in_progress == 181) \
            .OnlyEnforceIf(actions[Declaration.BIRD]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('archaeopteryx antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 4])))
    # Ornithomimosaur (UNCERTAIN)
    model.Add(skeleton_in_progress == 182) \
            .OnlyEnforceIf(actions[Declaration.BIRD]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('ornithomimosaur antiquity', antiquity, cp_model.Domain.FromFlatIntervals([5, cp_model.INT_MAX])))
    # Lamprey
    model.Add(skeleton_in_progress == 190) \
            .OnlyEnforceIf(actions[Declaration.FISH]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('lamprey antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 0])))
    # Coelacanth (UNCERTAIN)
    model.Add(skeleton_in_progress == 191) \
            .OnlyEnforceIf(actions[Declaration.FISH]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('coelacanth antiquity', antiquity, cp_model.Domain.FromFlatIntervals([1, cp_model.INT_MAX])))
    # Spider (UNCERTAIN)
    model.Add(skeleton_in_progress == 200) \
            .OnlyEnforceIf(actions[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('spider antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Primordial Orb-Weaver (UNCERTAIN)
    model.Add(skeleton_in_progress == 201) \
            .OnlyEnforceIf(actions[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('primordial orb-weaver antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 7])))
    # Trigonotarbid
    model.Add(skeleton_in_progress == 203) \
            .OnlyEnforceIf(actions[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('trigonotarbid antiquity', antiquity, cp_model.Domain.FromFlatIntervals([8, cp_model.INT_MAX])))
    # Beetle (UNCERTAIN)
    model.Add(skeleton_in_progress == 210) \
            .OnlyEnforceIf(actions[Declaration.INSECT]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('beetle antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Primordial Beetle (UNCERTAIN)
    model.Add(skeleton_in_progress == 211) \
            .OnlyEnforceIf(actions[Declaration.INSECT]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('primordial beetle antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 6])))
    # Rhyniognatha
    model.Add(skeleton_in_progress == 212) \
            .OnlyEnforceIf(actions[Declaration.INSECT]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('rhyniognatha antiquity', antiquity, cp_model.Domain.FromFlatIntervals([7, cp_model.INT_MAX])))
    # Curator
    model.Add(skeleton_in_progress == 300) \
            .OnlyEnforceIf(actions[Declaration.CURATOR])


    # Humanoid requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.HUMANOID])
    model.Add(legs == 2).OnlyEnforceIf(actions[Declaration.HUMANOID])
    model.Add(arms == 2).OnlyEnforceIf(actions[Declaration.HUMANOID])
    model.Add(torso_style >= 10).OnlyEnforceIf(actions[Declaration.HUMANOID])
    model.Add(torso_style <= 20).OnlyEnforceIf(actions[Declaration.HUMANOID])
    for prohibited_quality in [tails, fins, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.HUMANOID])

    # Ape requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.APE])
    model.Add(arms == 4).OnlyEnforceIf(actions[Declaration.APE])
    model.Add(torso_style >= 10).OnlyEnforceIf(actions[Declaration.APE])
    model.Add(torso_style <= 20).OnlyEnforceIf(actions[Declaration.APE])
    for prohibited_quality in [legs, tails, fins, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.APE])

    # Monkey requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.MONKEY])
    model.Add(arms == 4).OnlyEnforceIf(actions[Declaration.MONKEY])
    model.Add(tails == 1).OnlyEnforceIf(actions[Declaration.MONKEY])
    model.Add(torso_style >= 10).OnlyEnforceIf(actions[Declaration.MONKEY])
    model.Add(torso_style <= 20).OnlyEnforceIf(actions[Declaration.MONKEY])
    for prohibited_quality in [legs, fins, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.MONKEY])

    # Bird requirements
    model.Add(legs == 2).OnlyEnforceIf(actions[Declaration.BIRD])
    model.Add(wings == 2).OnlyEnforceIf(actions[Declaration.BIRD])
    model.Add(torso_style >= 20).OnlyEnforceIf(actions[Declaration.BIRD])
    for prohibited_quality in [arms, fins]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.BIRD])
    model.Add(tails < 2).OnlyEnforceIf(actions[Declaration.BIRD])

    # Curator requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.CURATOR])
    model.Add(arms == 2).OnlyEnforceIf(actions[Declaration.CURATOR])
    model.Add(legs == 2).OnlyEnforceIf(actions[Declaration.CURATOR])
    model.Add(wings == 2).OnlyEnforceIf(actions[Declaration.CURATOR])
    for prohibited_quality in [fins, tails]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.CURATOR])

    # Reptile requirements
    model.Add(torso_style >= 20).OnlyEnforceIf(actions[Declaration.REPTILE])
    model.Add(tails == 1).OnlyEnforceIf(actions[Declaration.REPTILE])
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.REPTILE])
    for prohibited_quality in [fins, wings, arms]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.REPTILE])
    model.Add(legs < 5).OnlyEnforceIf(actions[Declaration.REPTILE])

    # Amphibian requirements
    model.Add(torso_style >= 20).OnlyEnforceIf(actions[Declaration.AMPHIBIAN])
    model.Add(legs == 4).OnlyEnforceIf(actions[Declaration.AMPHIBIAN])
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.AMPHIBIAN])

    for prohibited_quality in [tails, fins, wings, arms]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.AMPHIBIAN])

    # Fish requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.FISH])
    model.Add(fins >= 2).OnlyEnforceIf(actions[Declaration.FISH])
    model.Add(tails <= 1).OnlyEnforceIf(actions[Declaration.FISH])
    model.Add(torso_style >= 20).OnlyEnforceIf(actions[Declaration.FISH])
    for prohibited_quality in [arms, legs, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.FISH])

    # Insect requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.INSECT])
    model.Add(legs == 6).OnlyEnforceIf(actions[Declaration.INSECT])
    model.Add(torso_style >= 20).OnlyEnforceIf(actions[Declaration.INSECT])
    for prohibited_quality in [arms, fins, tails]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.INSECT])
    model.Add(wings < 5).OnlyEnforceIf(actions[Declaration.INSECT])

    # Spider requirements
    model.Add(legs == 8).OnlyEnforceIf(actions[Declaration.SPIDER])
    model.Add(tails <= 1).OnlyEnforceIf(actions[Declaration.SPIDER])
    model.Add(torso_style >= 20).OnlyEnforceIf(actions[Declaration.SPIDER])
    for prohibited_quality in [skulls, arms, wings, fins]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.SPIDER])

    # Skeleton must have no unfilled skulls
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.skulls_needed for action in actions.keys()]) == 0)

    # Skeleton must have no unfilled limbs
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.limbs_needed for action in actions.keys()]) == 0)

    # Skeleton must have no unfilled tails, unless they were skipped
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tails_needed for action in actions.keys()]) == 0).OnlyEnforceIf(actions[Appendage.SKIP_TAILS].Not())
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tails_needed for action in actions.keys()]) >= 0).OnlyEnforceIf(actions[Appendage.SKIP_TAILS])

    if BUYER == Buyer.A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES:
        model.Add(skeleton_in_progress >= 100)

        # Revenue
        model.Add(primary_revenue == value + 5)
        model.Add(secondary_revenue == 500)

        # Difficulty Level
        model.Add(difficulty_level == 40*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.A_NAIVE_COLLECTOR:
        model.Add(skeleton_in_progress >= 100)

        model.AddModuloEquality(value_remainder, value, 250)

        # Revenue
        model.Add(primary_revenue == value - value_remainder)
        model.Add(secondary_revenue == 0)

        # Difficulty Level
        model.Add(difficulty_level == 25*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity <= 0)

        model.AddModuloEquality(value_remainder, value, 250)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 1000)
        model.Add(secondary_revenue == 250*counter_church)

        # Difficulty Level
        model.Add(difficulty_level == 50*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER:
        model.Add(skeleton_in_progress >= 100)
        model.Add(menace <= 0)

        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 1000)
        model.Add(secondary_revenue == 0)
        
        # Difficulty Level
        model.Add(difficulty_level == 50*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL:
        model.Add(skeleton_in_progress >= 100)
        model.Add(amalgamy <= 0)

        model.AddModuloEquality(value_remainder, value, 250)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 1000)
        model.Add(secondary_revenue == 0)
        
        # Difficulty Level
        model.Add(difficulty_level == 50*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity > 0)

        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder)
        model.Add(secondary_revenue == 250*antiquity + (250 if BONE_MARKET_FLUCTUATIONS == Fluctuation.ANTIQUITY else 0))
        
        # Difficulty Level
        model.Add(difficulty_level == 45*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.MRS_PLENTY:
        model.Add(skeleton_in_progress >= 100)
        model.Add(menace > 0)

        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder)
        model.Add(secondary_revenue == 250*menace)
        
        # Difficulty Level
        model.Add(difficulty_level == 45*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.A_TENTACLED_SERVANT:
        model.Add(skeleton_in_progress >= 100)
        model.Add(amalgamy > 0)

        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 250*amalgamy + (250 if BONE_MARKET_FLUCTUATIONS == Fluctuation.AMALGAMY else 0))
        
        # Difficulty Level
        model.Add(difficulty_level == 45*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.AN_INVESTMENT_MINDED_AMBASSADOR:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity > 0)

        antiquity_squared = model.NewIntVar(0, cp_model.INT32_MAX, 'antiquity squared')
        model.AddMultiplicationEquality(antiquity_squared, [antiquity, antiquity])

        tailfeathers = model.NewIntVar(0, cp_model.INT32_MAX, 'tailfeathers')
        if BONE_MARKET_FLUCTUATIONS == Fluctuation.ANTIQUITY:
            model.AddApproximateExponentiationEquality(tailfeathers, antiquity, 2.2, MAXIMUM_ATTRIBUTE)
        else:
            model.Add(tailfeathers == antiquity_squared)

        model.AddModuloEquality(value_remainder, value, 50)
        extra_value = model.NewIntermediateBoolVar('extra value', value_remainder, cp_model.Domain.FromFlatIntervals([0, cp_model.INT_MAX]))

        # Revenue
        model.Add(primary_revenue == value + 50*extra_value + 250)
        model.Add(secondary_revenue == 250*tailfeathers)
        
        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Added Exhaustion
        model.AddDivisionEquality(added_exhaustion, antiquity_squared, 20)
    elif BUYER == Buyer.A_TELLER_OF_TERRORS:
        model.Add(skeleton_in_progress >= 100)
        model.Add(menace > 0)

        menace_squared = model.NewIntVar(0, cp_model.INT32_MAX, 'menace squared')
        model.AddMultiplicationEquality(menace_squared, [menace, menace])

        model.AddModuloEquality(value_remainder, value, 10)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 50)
        model.Add(secondary_revenue == 50*menace_squared)
        
        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Added Exhaustion
        model.AddDivisionEquality(added_exhaustion, menace_squared, 100)
    elif BUYER == Buyer.A_TENTACLED_ENTREPRENEUR:
        model.Add(skeleton_in_progress >= 100)
        model.Add(amalgamy > 0)

        amalgamy_squared = model.NewIntVar(0, cp_model.INT32_MAX, 'amalgamy squared')
        model.AddMultiplicationEquality(amalgamy_squared, [amalgamy, amalgamy])

        final_breaths = model.NewIntVar(0, cp_model.INT32_MAX, 'final breaths')
        if BONE_MARKET_FLUCTUATIONS == Fluctuation.AMALGAMY:
            model.AddApproximateExponentiationEquality(final_breaths, amalgamy, 2.2, MAXIMUM_ATTRIBUTE)
        else:
            model.Add(final_breaths == amalgamy_squared)

        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 50*final_breaths)
        
        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Added Exhaustion
        model.AddDivisionEquality(added_exhaustion, amalgamy_squared, 100)
    elif BUYER == Buyer.AN_AUTHOR_OF_GOTHIC_TALES:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity > 0)
        model.Add(menace > 0)

        antiquity_times_menace = model.NewIntVar(0, cp_model.INT32_MAX, 'antiquity times menace')
        model.AddMultiplicationEquality(antiquity_times_menace, [antiquity, menace])

        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 250*antiquity_times_menace + 250*(menace if BONE_MARKET_FLUCTUATIONS == Fluctuation.ANTIQUITY else 0))

        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Added Exhaustion
        model.AddDivisionEquality(added_exhaustion, antiquity_times_menace, 20)
    elif BUYER == Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity > 0)
        model.Add(amalgamy > 0)

        amalgamy_times_antiquity = model.NewIntVar(0, cp_model.INT32_MAX, 'amalgamy times antiquity')
        model.AddMultiplicationEquality(amalgamy_times_antiquity, [amalgamy, antiquity])

        model.AddModuloEquality(value_remainder, value, 10)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 250*amalgamy_times_antiquity + 250*(amalgamy if BONE_MARKET_FLUCTUATIONS == Fluctuation.ANTIQUITY else antiquity if BONE_MARKET_FLUCTUATIONS == Fluctuation.AMALGAMY else 0))

        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Added Exhaustion
        model.AddDivisionEquality(added_exhaustion, amalgamy_times_antiquity, 20)
    elif BUYER == Buyer.A_RUBBERY_COLLECTOR:
        model.Add(skeleton_in_progress >= 100)
        model.Add(amalgamy > 0)
        model.Add(menace > 0)

        amalgamy_times_menace = model.NewIntVar(0, cp_model.INT32_MAX, 'amalgamy times menace')
        model.AddMultiplicationEquality(amalgamy_times_menace, [amalgamy, menace])

        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 250*amalgamy_times_menace + 250*(menace if BONE_MARKET_FLUCTUATIONS == Fluctuation.AMALGAMY else 0))

        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Added Exhaustion
        model.AddDivisionEquality(added_exhaustion, amalgamy_times_menace, 20)
    elif BUYER == Buyer.A_CONSTABLE:
        model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([110, 119]))

        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 1000)
        model.Add(secondary_revenue == 0)

        # Difficulty Level
        model.Add(difficulty_level == 50*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.AN_ENTHUSIAST_IN_SKULLS:
        model.Add(skeleton_in_progress >= 100)
        model.Add(skulls >= 2)
        
        extra_skulls = model.NewIntVar(0, cp_model.INT32_MAX, 'extra skulls')
        model.Add(extra_skulls == skulls - 1)
        vital_intelligence = model.NewIntVar(0, cp_model.INT32_MAX, 'vital intelligence')
        model.AddApproximateExponentiationEquality(vital_intelligence, extra_skulls, 1.8, MAXIMUM_ATTRIBUTE)

        # Revenue
        model.Add(primary_revenue == value)
        model.Add(secondary_revenue == 1250*vital_intelligence)

        # Difficulty Level
        model.Add(difficulty_level == 60*implausibility)

        # Added Exhaustion
        model.AddDivisionEquality(added_exhaustion, vital_intelligence, 4)
    elif BUYER == Buyer.A_DREARY_MIDNIGHTER:
        model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([110, 299]))
        model.Add(amalgamy <= 0)
        model.Add(counter_church <= 0)

        model.AddModuloEquality(value_remainder, value, 3)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 300)
        model.Add(secondary_revenue == 250)

        # Difficulty Level
        model.Add(difficulty_level == 100*implausibility)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)
    elif BUYER == Buyer.THE_DUMBWAITER_OF_BALMORAL:
        model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([180, 189]))
        model.Add(value >= 250)

        model.AddModuloEquality(value_remainder, value, 250)

        # Revenue
        model.Add(primary_revenue == value - value_remainder)
        model.Add(secondary_revenue == 0)

        # Difficulty Level
        model.Add(difficulty_level == 200)

        # Added Exhaustion
        model.Add(added_exhaustion == 0)


    # Maximize profit margin
    net_profit = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'net profit')
    model.Add(net_profit == total_revenue - cost)

    # This is necessary to preserve some degree of precision after dividing
    multiplied_net_profit = model.NewIntVar(cp_model.INT32_MIN*PROFIT_MARGIN_MULTIPLIER, cp_model.INT32_MAX*PROFIT_MARGIN_MULTIPLIER, 'multiplied net profit')
    model.AddMultiplicationEquality(multiplied_net_profit, [net_profit, PROFIT_MARGIN_MULTIPLIER])

    absolute_multiplied_net_profit = model.NewIntVar(0, cp_model.INT32_MAX*PROFIT_MARGIN_MULTIPLIER, 'absolute multiplied net profit')
    model.AddAbsEquality(absolute_multiplied_net_profit, multiplied_net_profit)

    absolute_profit_margin = model.NewIntVar(cp_model.INT32_MIN*PROFIT_MARGIN_MULTIPLIER, cp_model.INT32_MAX*PROFIT_MARGIN_MULTIPLIER, 'absolute profit margin')
    model.AddDivisionEquality(absolute_profit_margin, absolute_multiplied_net_profit, total_revenue)

    profit_margin = model.NewIntVar(cp_model.INT32_MIN*PROFIT_MARGIN_MULTIPLIER, cp_model.INT32_MAX*PROFIT_MARGIN_MULTIPLIER, 'profit margin')

    positive_net_profit = model.NewIntermediateBoolVar('positive net profit', net_profit, cp_model.Domain.FromFlatIntervals([0, cp_model.INT_MAX]))
    model.Add(profit_margin == absolute_profit_margin).OnlyEnforceIf(positive_net_profit)
    model.Add(profit_margin == absolute_profit_margin*-1).OnlyEnforceIf(positive_net_profit.Not())

    del multiplied_net_profit, absolute_multiplied_net_profit, absolute_profit_margin, positive_net_profit

    
    model.Maximize(profit_margin)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = os.cpu_count()
    solver.parameters.log_search_progress = True

    status = solver.StatusName(solver.Solve(model))
    if status == "INFEASIBLE":
        raise RuntimeError("There is no satisfactory skeleton.")
    elif status == "FEASIBLE":
        print("WARNING: skeleton may be suboptimal.")
    elif status != "OPTIMAL":
        raise RuntimeError("Unknown status returned: {}.".format(status))

    for action in actions.keys():
        for _ in range(int(solver.Value(actions[action]))):
            print(action)

    print("\nProfit: £{:,.2f}".format(solver.Value(net_profit)/100))
    print("Profit Margin: {:+,.2%}".format(solver.Value(profit_margin)/PROFIT_MARGIN_MULTIPLIER))

    print("\nTotal Revenue: £{:,.2f}".format(solver.Value(total_revenue)/100))
    print("Primary Revenue: £{:,.2f}".format(solver.Value(primary_revenue)/100))
    print("Secondary Revenue: £{:,.2f}".format(solver.Value(secondary_revenue)/100))

    print("\nCost: £{:,.2f}".format(solver.Value(cost)/100))

    print("\nValue: £{:,.2f}".format(solver.Value(value)/100))
    print("Amalgamy: {:n}".format(solver.Value(amalgamy)))
    print("Antiquity: {:n}".format(solver.Value(antiquity)))
    print("Menace: {:n}".format(solver.Value(menace)))
    print("Counter-Church: {:n}".format(solver.Value(counter_church)))
    print("Implausibility: {:n}".format(solver.Value(implausibility)))

    print("\nExhaustion: {:n}".format(solver.Value(exhaustion)))

if __name__ == '__main__':
    Solve()
