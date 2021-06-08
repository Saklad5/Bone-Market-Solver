import functools
import enum
import os

from enum import auto
from ortools.sat.python import cp_model

# This multiplier is applied to the profit margin to avoid losing precision due to rounding.
PROFIT_MARGIN_MULTIPLIER = 10000000

# This is the highest number of attribute to calculate fractional exponents for.
MAXIMUM_ATTRIBUTE = 100

# The number of pennies that a single action (the game mechanic) is worth.
ACTION_VALUE = 400

# The number of pennies needed to produce a single Survey of the Neath's Bones.
SURVEY_VALUE = (ACTION_VALUE * 6) / 25

# This is a constant used to calculate difficulty checks. You almost certainly do not need to change this.
DIFFICULTY_SCALER = 0.6

# This is the effective level of Shadowy used for attempting to sell.
SHADOWY_LEVEL = 300

# The maximum number of pennies that should be invested in this skeleton.
MAXIMUM_COST = cp_model.INT32_MAX

# The maximum Exhaustion that this skeleton should generate.
MAXIMUM_EXHAUSTION = 4


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
    # Licentiate
    # LICENTIATE_SKELETON = Action("Supply a skeleton of your own", cost = ACTION_VALUE, torso_style = 10, value = 250, skulls_needed = 1, arms = 2, legs = 2)

    # Accumulated while trying to get other things
    HEADLESS_HUMANOID = Action("Reassemble your Headless Humanoid", cost = ACTION_VALUE, torso_style = 10, value = 250, skulls_needed = 1, arms = 2, legs = 2)

    # Ealing Gardens
    HUMAN_RIBCAGE = Action("Build on the Human Ribcage", cost = ACTION_VALUE*2 + SURVEY_VALUE*15, torso_style = 15, value = 1250, skulls_needed = 1, limbs_needed = 4)

    # Balmoral Woods (also gives Doubled Skull)
    THORNED_RIBCAGE = Action("Make something of your Thorned Ribcage", cost = 2000 + ACTION_VALUE*14, torso_style = 20, value = 1250, skulls_needed = 1, limbs_needed = 4, tails_needed = 1, amalgamy = 1, menace = 1)

    # Warbler Skeleton and Betrayer of Measures
    SKELETON_WITH_SEVEN_NECKS = Action("Build on the Skeleton with Seven Necks", cost = 1150 + ACTION_VALUE*18, torso_style = 30, value = 6250, skulls_needed = 7, limbs_needed = 2, legs = 2, amalgamy = 2, menace = 1)

    # Combination of Human Ribcage and Thorned Ribcage
    FLOURISHING_RIBCAGE = Action("Build on the Flourishing Ribcage", cost = 2000 + ACTION_VALUE*16 + SURVEY_VALUE*15, torso_style = 40, value = 1250, skulls_needed = 2, limbs_needed = 6, tails_needed = 1, amalgamy = 2)

    # Human Ribcage and Betrayer of Measures
    MAMMOTH_RIBCAGE = Action("Build on the Mammoth Ribcage", cost = ACTION_VALUE*18 + SURVEY_VALUE*15, torso_style = 50, value = 6250, skulls_needed = 1, limbs_needed = 4, tails_needed = 1, antiquity = 2)

    # Combination of Skeleton with Seven Necks and Thorned Ribcage
    RIBCAGE_WITH_A_BOUQUET_OF_EIGHT_SPINES = Action("Build on the Ribcage with the Eight Spines", cost = 25650 + ACTION_VALUE*32, torso_style = 60, value = 31250, skulls_needed = 8, limbs_needed = 4, tails_needed = 1, amalgamy = 1, menace = 2)

    # Skeleton with Seven Necks, 2 x Severed Chimaerical Head of the Vake, 2 x Counterfeit Head of John the Baptist, Carved Ball of Stygian Ivory, 2 x Plated Skull, 2 x Albatross Wing
    LEVIATHAN_FRAME = Action("Build on the Leviathan Frame", cost = 22150 + ACTION_VALUE*33, torso_style = 70, value = 31250, skulls_needed = 1, limbs_needed = 2, tails = 1, antiquity = 1, menace = 1)

    # Expedition at Station VII
    PRISMATIC_FRAME = Action("Build on the Prismatic Frame", cost = 29250 + ACTION_VALUE*5, torso_style = 80, value = 31250, skulls_needed = 3, limbs_needed = 3, tails_needed = 3, amalgamy = 2, antiquity = 2)

    # Upwards
    FIVE_POINTED_FRAME = Action("Build on the Five-Pointed Frame", cost = 31250 + ACTION_VALUE*10, torso_style = 100, value = 31250, skulls_needed = 5, limbs_needed = 5, amalgamy = 2, menace = 1)

    def __str__(self):
        return str(self.value)


# Which kind of skeleton is to be declared.
class Declaration(enum.Enum):
    CHIMERA = Action("Declare your (Skeleton Type) a completed Chimera", cost = ACTION_VALUE, implausibility = 3)
    HUMANOID = Action("Declare your (Skeleton Type) a completed Humanoid", cost = ACTION_VALUE)
    APE = Action("Declare your (Skeleton Type) a completed Ape", cost = ACTION_VALUE)
    MONKEY = Action("Declare your (Skeleton Type) a completed Monkey", cost = ACTION_VALUE)
    BIRD = Action("Declare your (Skeleton Type) a completed Bird", cost = ACTION_VALUE)
    CURATOR = Action("Declare your (Skeleton Type) a completed Curator", cost = ACTION_VALUE)
    REPTILE = Action("Declare your (Skeleton Type) a completed Reptile", cost = ACTION_VALUE)
    AMPHIBIAN = Action("Declare your (Skeleton Type) a completed Amphibian", cost = ACTION_VALUE)
    FISH = Action("Declare your (Skeleton Type) a completed Fish", cost = ACTION_VALUE)
    INSECT = Action("Declare your (Skeleton Type) a completed Insect", cost = ACTION_VALUE)
    SPIDER = Action("Declare your (Skeleton Type) a completed Spider", cost = ACTION_VALUE)

    def __str__(self):
        return str(self.value)

# Which skeleton attribute is currently boosted.
class Fluctuation(enum.Enum):
    ANTIQUITY = 1
    AMALGAMY = 2

def create_data_model():
    data = {}

    data['buyer'] = Buyer.AN_ENTHUSIAST_IN_SKULLS

    # The current value of Bone Market Fluctuations, which grants various bonuses to certain buyers.
    data['bone_market_fluctuations'] = Fluctuation.AMALGAMY 

    # The current value of Zoological Mania, which grants a 10% bonus to value for a certain declaration.
    data['zoological_mania'] = Declaration.AMPHIBIAN
    
    data['actions'] = [torso.value for torso in Torso] + [
            Action("Affix a Bright Brass Skull to your (Skeleton Type)", cost = 6450 + ACTION_VALUE, value = 6500, skulls_needed = -1, skulls = 1, implausibility = 2),
            # No consistent source
            # Action("Affix an Eyeless Skull to your (Skeleton Type)", cost = cp_model.INT32_MAX, value = 3000, skulls_needed = -1, skulls = 1, menace = 2),
            # Feast of the Exceptional Rose, 200 Inklings of Identity, action to send and receive it
            #Action("Affix a Custom-Engraved Skull to your (Skeleton Type)", cost = 2000 + ACTION_VALUE*2, value = 10000, skulls_needed = -1, skulls = 1, exhaustion = 2),
            Action("Affix a Horned Skull to your (Skeleton Type)", cost = 1050 + ACTION_VALUE*2, value = 1250, skulls_needed = -1, skulls = 1, antiquity = 1, menace = 2),
            Action("Affix a Sabre-toothed Skull to your (Skeleton Type)", cost = 6150 + ACTION_VALUE*2, value = 6250, skulls_needed = -1, skulls = 1, antiquity = 1, menace = 1),
            # Upwards
            Action("Affix a Pentagrammic Skull to your (Skeleton Type)", cost = ACTION_VALUE*10, value = 1250, skulls_needed = -1, skulls = 1, amalgamy = 2, menace = 1),
            Action("Affix a Plated Skull to your (Skeleton Type)", cost = 2250 + ACTION_VALUE*2, value = 2500, skulls_needed = -1, skulls = 1, menace = 2),
            # Flute Street, including travel due to quality cap
            Action("Affix a Rubbery Skull to your (Skeleton Type)", cost = ACTION_VALUE*26, value = 600, skulls_needed = -1, skulls = 1, amalgamy = 1),
            # Action("Duplicate your own skull and affix it here", cost = 1000 + ACTION_VALUE, value = -250, skulls_needed = -1, skulls = 1),
            Action("Duplicate the skull of John the Baptist, if you can call that a skull", cost = 1000 + ACTION_VALUE, value = 1500, skulls_needed = -1, skulls = 1, counter_church = 2),
            # Persephone, 6 actions (Favours: the Docks) for 2 Esteem of the Guild
            Action("Affix a Skull in Coral to your (Skeleton Type)", cost = ACTION_VALUE*25/3, value = 1750, skulls_needed = -1, skulls = 1, amalgamy = 2),
            Action("Duplicate the Vake's skull and use it to decorate your (Skeleton Type)", cost = 6000 + ACTION_VALUE, value = 6500, skulls_needed = -1, skulls = 1, menace = 3),
            # Action("Cap this with a victim’s skull", cost = ACTION_VALUE, value = 250, skulls_needed = -1, skulls = 1),
            # Balmoral Woods (also gives Thorned Ribcage)
            Action("Affix a Doubled Skull to your (Skeleton Type)", cost = 2000 + ACTION_VALUE*14, value = 6250, skulls_needed = -1, skulls = 2, amalgamy = 1, antiquity = 2),
            Action("Use a Carved Ball of Stygian Ivory to cap off your (Skeleton Type)", cost = 250 + ACTION_VALUE, value = 250, skulls_needed = -1),

            # 2 pincers at once
            Action("Apply a Crustacean Pincer to your (Skeleton Type)", cost = 25 + ACTION_VALUE*1.5, limbs_needed = -1, arms = 1, menace = 1),
            # Accumulated while trying to get other things
            Action("Apply a Knotted Humerus to your (Skeleton Type)", cost = ACTION_VALUE, value = 150, limbs_needed = -1, arms = 1, amalgamy = 1),
            # Ealing Gardens, 5 actions (Favours: Bohemians) for 2
            Action("Apply an Ivory Humerus to your (Skeleton Type)", cost = ACTION_VALUE*3.5, value = 1500, limbs_needed = -1, arms = 1),
            # Accumulated while trying to get other things
            Action("Join a Human Arm to your (Skeleton Type)", cost = ACTION_VALUE, value = 250, limbs_needed = -1, arms = 1, menace = -1),
            # Anning and Daughters
            Action("Apply a Fossilised Forelimb to your (Skeleton Type)", cost = 2500 + ACTION_VALUE, value = 2750, limbs_needed = -1, arms = 1, antiquity = 2),

            # 2 wings at once
            Action("Add the Wing of a Young Terror Bird to your (Skeleton Type)", cost = 175 + ACTION_VALUE*1.5, value = 250, limbs_needed = -1, wings = 1, antiquity = 1, menace = 1),
            # 2 wings at once
            Action("Put an Albatross Wing on your (Skeleton Type)", cost = 1125 + ACTION_VALUE*1.5, value = 1250, limbs_needed = -1, wings = 1, amalgamy = 1),
            # 2 wings at once
            Action("Add a Bat Wing to your (Skeleton Type)", cost = 60 + ACTION_VALUE*1.5, value = 1, limbs_needed = -1, wings = 1, menace = -1),

            # Dumbwaiter of Balmoral, 25 at a time
            Action("Apply the Femur of a Surface Deer to your (Skeleton Type)", cost = ACTION_VALUE*1.04, value = 10, limbs_needed = -1, legs = 1, menace = -1),
            # Accumulated while trying to get other things
            Action("Apply an Unidentified Thigh Bone to your (Skeleton Type)", cost = ACTION_VALUE, value = 100, limbs_needed = -1, legs = 1),
            # Brawling, 12 at a time
            Action("Apply a Jurassic Thigh Bone to your (Skeleton Type)", cost = ACTION_VALUE*(11/6), value = 300, limbs_needed = -1, legs = 1, antiquity = 1),
            # Jericho Locks, 5 actions (Favours: the Church) for 2
            # Counter-Church theology from this scales with torso style and is implemented separately
            Action("Affix Saint Fiacre's Thigh Relic to your (Skeleton Type)", cost = ACTION_VALUE*3.5, value = 1250, limbs_needed = -1, legs = 1),
            # Palaeontological Discoveries, Plain of Thirsty Grasses
            Action("Affix the Helical Thighbone to your (Skeleton Type)", cost = ACTION_VALUE + SURVEY_VALUE*(70/9), value = 300, limbs_needed = -1, legs = 1, amalgamy = 2),
            # Parabolan Orange-Apples, Hedonist, 3cp/action
            Action("Apply an Ivory Femur to your (Skeleton Type)", cost = 900 + ACTION_VALUE*15.5, value = 6500, limbs_needed = -1, legs = 1),

            # Hunt and dissect Pinewood Shark, 40 at a time
            Action("Put Fins on your (Skeleton Type)", cost = ACTION_VALUE*(51/40), value = 50, limbs_needed = -1, fins = 1),
            # Combination of 10 Fins
            Action("Attach the Amber-Crusted Fin to your (Skeleton Type)", cost = ACTION_VALUE*(15/4), value = 1500, limbs_needed = -1, fins = 1, amalgamy = 1, menace = 1),

            # Helicon House, 3 at a time
            Action("Put a Withered Tentacle on your (Skeleton Type)", cost = 50/3 + ACTION_VALUE*4/3, value = 250, limbs_needed = -1, tentacles = 1, antiquity = -1),

            # Carpenter's Granddaughter, 2 at a time
            Action("Apply Plaster Tail Bones to your (Skeleton Type)", cost = ACTION_VALUE*1.5 + SURVEY_VALUE*5, value = 250, tails_needed = -1, tails = 1, implausibility = 1),
            Action("Apply a Tomb-Lion's Tail to your (Skeleton Type)", cost = 220 + ACTION_VALUE*2, value = 250, tails_needed = -1, tails = 1, antiquity = 1),
            # Geology of Winewound
            Action("Apply a Jet Black Stinger to your (Skeleton Type)", cost = ACTION_VALUE*2 + SURVEY_VALUE, value = 50, tails_needed = -1, tails = 1, menace = 2),
            # No consistent source
            # Action("Apply an Obsidian Chitin Tail to your (Skeleton Type)", cost = cp_model.INT32_MAX, value = 500, tails_needed = -1, tails = 1, amalgamy = 1),
            # Helicon House, 3 at a time
            Action("Apply a Withered Tentacle as a tail on your (Skeleton Type)", cost = 50/3 + ACTION_VALUE*4/3, value = 250, tails_needed = -1, tails = 1, antiquity = -1),
            # This actually sets Skeleton: Tails Needed to 0
            Action("Decide your Tailless Animal needs no tail", cost = ACTION_VALUE, tails_needed = -1),
            Action("Remove the tail from your (Skeleton Type)", cost = ACTION_VALUE, tails = -1),

            # Cost from this scales with limbs and is partially implemented separately
            Action("Add four more joints to your skeleton", cost = 1250 + ACTION_VALUE, limbs_needed = 4, amalgamy = 2),
            Action("Make your skeleton less dreadful", cost = ACTION_VALUE, menace = -2),
            Action("Disguise the amalgamy of this piece", cost = 25 + ACTION_VALUE, amalgamy = -2),
            Action("Carve away some evidence of age", cost = ACTION_VALUE, antiquity = -2)
    ]

    return data

def Solve():
    data = create_data_model()
    model = cp_model.CpModel()

    # Any number of any action, except only one torso
    torsos = {}
    actions = {}
    for action in data['actions']:
        if action.torso_style is not None:
            torsos[action] = model.NewBoolVar(action.name)
            actions[action] = torsos[action]
        else:
            actions[action] = model.NewIntVar(0, cp_model.INT32_MAX, action.name)

    model.Add(cp_model.LinearExpr.Sum(torsos.values()) == 1)

    # Skeleton must be declared something
    declarations = {}
    for declaration in Declaration:
        declarations[declaration] = model.NewBoolVar(declaration.value.name)
        actions[declaration.value] = declarations[declaration]
    model.Add(cp_model.LinearExpr.Sum(declarations.values()) == 1)

    # Value calculation
    original_value = model.NewIntVar(0, cp_model.INT32_MAX, 'original value')
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value for action in actions.keys()]) == original_value)

    multiplied_value = model.NewIntVar(0, cp_model.INT32_MAX*11, "multiplied value")
    model.Add(multiplied_value == original_value*11).OnlyEnforceIf(declarations[data['zoological_mania']])
    model.Add(multiplied_value == original_value*10).OnlyEnforceIf(declarations[data['zoological_mania']].Not())

    value = model.NewIntVar(0, cp_model.INT32_MAX, 'value')
    model.AddDivisionEquality(value, multiplied_value, 10)

    del original_value, multiplied_value


    # Torso Style calculation
    torso_style = model.NewIntVarFromDomain(cp_model.Domain.FromValues([torso.torso_style for torso in torsos.keys()]), 'torso_style')
    for torso, torso_variable in torsos.items():
        model.Add(torso_style == torso.torso_style).OnlyEnforceIf(torso_variable)

    # Skulls calculation
    skulls = model.NewIntVar(0, cp_model.INT32_MAX, 'skulls')
    model.Add(skulls == cp_model.LinearExpr.ScalProd(actions.values(), [action.skulls for action in actions.keys()]))

    # Arms calculation
    arms = model.NewIntVar(0, cp_model.INT32_MAX, 'arms')
    model.Add(arms == cp_model.LinearExpr.ScalProd(actions.values(), [action.arms for action in actions.keys()]))

    # Legs calculation
    legs = model.NewIntVar(0, cp_model.INT32_MAX, 'legs')
    model.Add(legs == cp_model.LinearExpr.ScalProd(actions.values(), [action.legs for action in actions.keys()]))

    # Tails calculation
    tails = model.NewIntVar(0, cp_model.INT32_MAX, 'tails')
    model.Add(tails == cp_model.LinearExpr.ScalProd(actions.values(), [action.tails for action in actions.keys()]))

    # Wings calculation
    wings = model.NewIntVar(0, cp_model.INT32_MAX, 'wings')
    model.Add(wings == cp_model.LinearExpr.ScalProd(actions.values(), [action.wings for action in actions.keys()]))

    # Fins calculation
    fins = model.NewIntVar(0, cp_model.INT32_MAX, 'fins')
    model.Add(fins == cp_model.LinearExpr.ScalProd(actions.values(), [action.fins for action in actions.keys()]))

    # Tentacles calculation
    tentacles = model.NewIntVar(0, cp_model.INT32_MAX, 'tentacles')
    model.Add(tentacles == cp_model.LinearExpr.ScalProd(actions.values(), [action.tentacles for action in actions.keys()]))

    # Amalgamy calculation
    amalgamy = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'amalgamy')
    model.Add(amalgamy == cp_model.LinearExpr.ScalProd(actions.values(), [action.amalgamy for action in actions.keys()]))

    # Antiquity calculation
    antiquity = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'antiquity')
    model.Add(antiquity == cp_model.LinearExpr.ScalProd(actions.values(), [action.antiquity for action in actions.keys()]))

    # Menace calculation
    menace = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'menace')
    model.Add(menace == cp_model.LinearExpr.ScalProd(actions.values(), [action.menace for action in actions.keys()]))

    # Implausibility calculation
    implausibility = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'implausibility')
    model.Add(implausibility == cp_model.LinearExpr.ScalProd(actions.values(), [action.implausibility for action in actions.keys()]))

    # Counter-church calculation
    # Calculate amount of Counter-church from Holy Relics of the Thigh of Saint Fiacre
    holy_relic = next(filter(lambda action: action[0].name == "Affix Saint Fiacre's Thigh Relic to your (Skeleton Type)", actions.items()))[1]
    torso_style_divided_by_ten = model.NewIntVar(0, cp_model.INT32_MAX, 'torso style divided by ten')
    model.AddDivisionEquality(torso_style_divided_by_ten, torso_style, 10)
    holy_relic_counter_church = model.NewIntVar(0, cp_model.INT32_MAX, 'holy relic counter-church')
    model.AddMultiplicationEquality(holy_relic_counter_church, [holy_relic, torso_style_divided_by_ten])

    counter_church = model.NewIntVar(cp_model.INT32_MIN, cp_model.INT32_MAX, 'counter-church')
    model.Add(counter_church == cp_model.LinearExpr.ScalProd(actions.values(), [action.counter_church for action in actions.keys()]) + holy_relic_counter_church)

    del holy_relic, torso_style_divided_by_ten, holy_relic_counter_church

    # Exhaustion calculation
    exhaustion = model.NewIntVar(0, MAXIMUM_EXHAUSTION, 'exhaustion')

    # Profit intermediate variables
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
    model.AddDivisionEquality(sale_actions_times_action_value, model.NewConstant(round(DIFFICULTY_SCALER*SHADOWY_LEVEL*ACTION_VALUE)), non_zero_difficulty_level)
    abstract_sale_cost = model.NewIntVar(0, cp_model.INT32_MAX, 'abstract sale cost')
    model.AddDivisionEquality(abstract_sale_cost, ACTION_VALUE**2, sale_actions_times_action_value)
    sale_cost = model.NewIntVar(0, cp_model.INT32_MAX, 'sale cost')
    model.AddMaxEquality(sale_cost, [abstract_sale_cost, ACTION_VALUE])

    del non_zero_difficulty_level, sale_actions_times_action_value, abstract_sale_cost


    # Calculate cost of adding joints
    # This is a partial sum formula.
    add_joints_amber_cost = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost')

    add_joints = next(filter(lambda action: action[0].name == "Add four more joints to your skeleton", actions.items()))[1]

    base_joints = model.NewIntVar(0, cp_model.INT32_MAX, 'base joints')
    model.Add(base_joints == cp_model.LinearExpr.ScalProd(torsos.values(), [action.limbs_needed for torso in torsos.keys()]))

    add_joints_amber_cost_multiple = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple')

    add_joints_amber_cost_multiple_first_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple first term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_first_term, 250, base_joints, base_joints, add_joints)

    add_joints_amber_cost_multiple_second_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple second term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_second_term, 1000, base_joints, add_joints, add_joints)

    add_joints_amber_cost_multiple_third_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple third term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_third_term, 1000, base_joints, add_joints)

    add_joints_amber_cost_multiple_fourth_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple fourth term')
    add_joints_amber_cost_multiple_fourth_term_numerator = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple fourth term numerator')
    add_joints_amber_cost_multiple_fourth_term_numerator_first_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple fourth term numerator first term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_fourth_term_numerator_first_term, 4000, add_joints, add_joints, add_joints)
    model.Add(add_joints_amber_cost_multiple_fourth_term_numerator == add_joints_amber_cost_multiple_fourth_term_numerator_first_term + 2000*add_joints)
    model.AddDivisionEquality(add_joints_amber_cost_multiple_fourth_term, add_joints_amber_cost_multiple_fourth_term_numerator, 3)
    del add_joints_amber_cost_multiple_fourth_term_numerator, add_joints_amber_cost_multiple_fourth_term_numerator_first_term

    add_joints_amber_cost_multiple_fifth_term = model.NewIntVar(0, cp_model.INT32_MAX, 'add joints amber cost multiple fifth term')
    model.AddGeneralMultiplicationEquality(add_joints_amber_cost_multiple_fifth_term, 2000, add_joints, add_joints)

    model.Add(add_joints_amber_cost_multiple == add_joints_amber_cost_multiple_first_term + add_joints_amber_cost_multiple_second_term - add_joints_amber_cost_multiple_third_term + add_joints_amber_cost_multiple_fourth_term - add_joints_amber_cost_multiple_fifth_term)

    del add_joints_amber_cost_multiple_first_term, add_joints_amber_cost_multiple_second_term, add_joints_amber_cost_multiple_third_term, add_joints_amber_cost_multiple_fourth_term, add_joints_amber_cost_multiple_fifth_term

    model.AddMultiplicationEquality(add_joints_amber_cost, [add_joints, add_joints_amber_cost_multiple])

    del add_joints, add_joints_amber_cost_multiple


    cost = model.NewIntVar(0, MAXIMUM_COST, 'cost')
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [int(action.cost) for action in actions.keys()]) + add_joints_amber_cost + sale_cost == cost)

    del sale_cost, add_joints_amber_cost


    # Type of skeleton
    skeleton_in_progress = model.NewIntVar(0, cp_model.INT32_MAX, 'skeleton in progress')

    # Chimera
    model.Add(skeleton_in_progress == 100) \
            .OnlyEnforceIf(declarations[Declaration.CHIMERA])
    # Humanoid
    model.Add(skeleton_in_progress == 110) \
            .OnlyEnforceIf(declarations[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('humanoid antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 0])))
    # Ancient Humanoid (UNCERTAIN)
    model.Add(skeleton_in_progress == 111) \
            .OnlyEnforceIf(declarations[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('ancient humanoid antiquity', antiquity, cp_model.Domain.FromFlatIntervals([1, 5])))
    # Neanderthal
    model.Add(skeleton_in_progress == 112) \
            .OnlyEnforceIf(declarations[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('neanderthal antiquity', antiquity, cp_model.Domain.FromFlatIntervals([6, cp_model.INT_MAX])))
    # Ape (UNCERTAIN)
    model.Add(skeleton_in_progress == 120) \
            .OnlyEnforceIf(declarations[Declaration.APE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('ape antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Primordial Ape (UNCERTAIN)
    model.Add(skeleton_in_progress == 121) \
            .OnlyEnforceIf(declarations[Declaration.APE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('primordial ape antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, cp_model.INT_MAX])))
    # Monkey
    model.Add(skeleton_in_progress == 125) \
            .OnlyEnforceIf(declarations[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('monkey antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 0])))
    # Catarrhine Monkey (UNCERTAIN)
    model.Add(skeleton_in_progress == 126) \
            .OnlyEnforceIf(declarations[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('catarrhine monkey 126 antiquity', antiquity, cp_model.Domain.FromFlatIntervals([1, 8])))
    # Catarrhine Monkey
    model.Add(skeleton_in_progress == 128) \
            .OnlyEnforceIf(declarations[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('catarrhine monkey 128 antiquity', antiquity, cp_model.Domain.FromFlatIntervals([9, cp_model.INT_MAX])))
    # Crocodile
    model.Add(skeleton_in_progress == 160) \
            .OnlyEnforceIf(declarations[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('crocodile antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Dinosaur
    model.Add(skeleton_in_progress == 161) \
            .OnlyEnforceIf(declarations[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('dinosaur antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 4])))
    # Mesosaur (UNCERTAIN)
    model.Add(skeleton_in_progress == 162) \
            .OnlyEnforceIf(declarations[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('mesosaur antiquity', antiquity, cp_model.Domain.FromFlatIntervals([5, cp_model.INT_MAX])))
    # Toad
    model.Add(skeleton_in_progress == 170) \
            .OnlyEnforceIf(declarations[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('toad antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Primordial Amphibian
    model.Add(skeleton_in_progress == 171) \
            .OnlyEnforceIf(declarations[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('primordial amphibian antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 4])))
    # Temnospondyl
    model.Add(skeleton_in_progress == 172) \
            .OnlyEnforceIf(declarations[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('temnospondyl antiquity', antiquity, cp_model.Domain.FromFlatIntervals([5, cp_model.INT_MAX])))
    # Owl
    model.Add(skeleton_in_progress == 180) \
            .OnlyEnforceIf(declarations[Declaration.BIRD]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('owl antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Archaeopteryx
    model.Add(skeleton_in_progress == 181) \
            .OnlyEnforceIf(declarations[Declaration.BIRD]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('archaeopteryx antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 4])))
    # Ornithomimosaur (UNCERTAIN)
    model.Add(skeleton_in_progress == 182) \
            .OnlyEnforceIf(declarations[Declaration.BIRD]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('ornithomimosaur antiquity', antiquity, cp_model.Domain.FromFlatIntervals([5, cp_model.INT_MAX])))
    # Lamprey
    model.Add(skeleton_in_progress == 190) \
            .OnlyEnforceIf(declarations[Declaration.FISH]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('lamprey antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 0])))
    # Coelacanth (UNCERTAIN)
    model.Add(skeleton_in_progress == 191) \
            .OnlyEnforceIf(declarations[Declaration.FISH]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('coelacanth antiquity', antiquity, cp_model.Domain.FromFlatIntervals([1, cp_model.INT_MAX])))
    # Spider (UNCERTAIN)
    model.Add(skeleton_in_progress == 200) \
            .OnlyEnforceIf(declarations[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('spider antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Primordial Orb-Weaver (UNCERTAIN)
    model.Add(skeleton_in_progress == 201) \
            .OnlyEnforceIf(declarations[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('primordial orb-weaver antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 7])))
    # Trigonotarbid
    model.Add(skeleton_in_progress == 203) \
            .OnlyEnforceIf(declarations[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('trigonotarbid antiquity', antiquity, cp_model.Domain.FromFlatIntervals([8, cp_model.INT_MAX])))
    # Beetle (UNCERTAIN)
    model.Add(skeleton_in_progress == 210) \
            .OnlyEnforceIf(declarations[Declaration.INSECT]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('beetle antiquity', antiquity, cp_model.Domain.FromFlatIntervals([cp_model.INT_MIN, 1])))
    # Primordial Beetle (UNCERTAIN)
    model.Add(skeleton_in_progress == 211) \
            .OnlyEnforceIf(declarations[Declaration.INSECT]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('primordial beetle antiquity', antiquity, cp_model.Domain.FromFlatIntervals([2, 6])))
    # Rhyniognatha
    model.Add(skeleton_in_progress == 212) \
            .OnlyEnforceIf(declarations[Declaration.INSECT]) \
            .OnlyEnforceIf(model.NewIntermediateBoolVar('rhyniognatha antiquity', antiquity, cp_model.Domain.FromFlatIntervals([7, cp_model.INT_MAX])))
    # Curator
    model.Add(skeleton_in_progress == 300) \
            .OnlyEnforceIf(declarations[Declaration.CURATOR])


    # Humanoid requirements
    model.Add(skulls == 1).OnlyEnforceIf(declarations[Declaration.HUMANOID])
    model.Add(legs == 2).OnlyEnforceIf(declarations[Declaration.HUMANOID])
    model.Add(arms == 2).OnlyEnforceIf(declarations[Declaration.HUMANOID])
    model.Add(torso_style >= 10).OnlyEnforceIf(declarations[Declaration.HUMANOID])
    model.Add(torso_style <= 20).OnlyEnforceIf(declarations[Declaration.HUMANOID])
    for prohibited_quality in [tails, fins, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.HUMANOID])

    # Ape requirements
    model.Add(skulls == 1).OnlyEnforceIf(declarations[Declaration.APE])
    model.Add(arms == 4).OnlyEnforceIf(declarations[Declaration.APE])
    model.Add(torso_style >= 10).OnlyEnforceIf(declarations[Declaration.APE])
    model.Add(torso_style <= 20).OnlyEnforceIf(declarations[Declaration.APE])
    for prohibited_quality in [legs, tails, fins, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.APE])

    # Monkey requirements
    model.Add(skulls == 1).OnlyEnforceIf(declarations[Declaration.MONKEY])
    model.Add(arms == 4).OnlyEnforceIf(declarations[Declaration.MONKEY])
    model.Add(tails == 1).OnlyEnforceIf(declarations[Declaration.MONKEY])
    model.Add(torso_style >= 10).OnlyEnforceIf(declarations[Declaration.MONKEY])
    model.Add(torso_style <= 20).OnlyEnforceIf(declarations[Declaration.MONKEY])
    for prohibited_quality in [legs, fins, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.MONKEY])

    # Bird requirements
    model.Add(legs == 2).OnlyEnforceIf(declarations[Declaration.BIRD])
    model.Add(wings == 2).OnlyEnforceIf(declarations[Declaration.BIRD])
    model.Add(torso_style >= 20).OnlyEnforceIf(declarations[Declaration.BIRD])
    for prohibited_quality in [arms, fins]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.BIRD])
    model.Add(tails < 2).OnlyEnforceIf(declarations[Declaration.BIRD])

    # Curator requirements
    model.Add(skulls == 1).OnlyEnforceIf(declarations[Declaration.CURATOR])
    model.Add(arms == 2).OnlyEnforceIf(declarations[Declaration.CURATOR])
    model.Add(legs == 2).OnlyEnforceIf(declarations[Declaration.CURATOR])
    model.Add(wings == 2).OnlyEnforceIf(declarations[Declaration.CURATOR])
    for prohibited_quality in [fins, tails]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.CURATOR])

    # Reptile requirements
    model.Add(torso_style >= 20).OnlyEnforceIf(declarations[Declaration.REPTILE])
    model.Add(tails == 1).OnlyEnforceIf(declarations[Declaration.REPTILE])
    model.Add(skulls == 1).OnlyEnforceIf(declarations[Declaration.REPTILE])
    for prohibited_quality in [fins, wings, arms]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.REPTILE])
    model.Add(legs < 5).OnlyEnforceIf(declarations[Declaration.REPTILE])

    # Amphibian requirements
    model.Add(torso_style >= 20).OnlyEnforceIf(declarations[Declaration.AMPHIBIAN])
    model.Add(legs == 4).OnlyEnforceIf(declarations[Declaration.AMPHIBIAN])
    model.Add(skulls == 1).OnlyEnforceIf(declarations[Declaration.AMPHIBIAN])

    for prohibited_quality in [tails, fins, wings, arms]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.AMPHIBIAN])

    # Fish requirements
    model.Add(skulls == 1).OnlyEnforceIf(declarations[Declaration.FISH])
    model.Add(fins >= 2).OnlyEnforceIf(declarations[Declaration.FISH])
    model.Add(tails <= 1).OnlyEnforceIf(declarations[Declaration.FISH])
    model.Add(torso_style >= 20).OnlyEnforceIf(declarations[Declaration.FISH])
    for prohibited_quality in [arms, legs, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.FISH])

    # Insect requirements
    model.Add(skulls == 1).OnlyEnforceIf(declarations[Declaration.INSECT])
    model.Add(legs == 6).OnlyEnforceIf(declarations[Declaration.INSECT])
    model.Add(torso_style >= 20).OnlyEnforceIf(declarations[Declaration.INSECT])
    for prohibited_quality in [arms, fins, tails]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.INSECT])
    model.Add(wings < 5).OnlyEnforceIf(declarations[Declaration.INSECT])

    # Spider requirements
    model.Add(legs == 8).OnlyEnforceIf(declarations[Declaration.SPIDER])
    model.Add(tails <= 1).OnlyEnforceIf(declarations[Declaration.SPIDER])
    model.Add(torso_style >= 20).OnlyEnforceIf(declarations[Declaration.SPIDER])
    for prohibited_quality in [skulls, arms, wings, fins]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(declarations[Declaration.SPIDER])

    # Skeleton must be finished
    for needed_quality in [lambda action: action.skulls_needed, lambda action: action.limbs_needed, lambda action: action.tails_needed]:
        model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [needed_quality(action) for action in actions.keys()]) == 0)

    if data['buyer'] == Buyer.A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES:
        model.Add(skeleton_in_progress >= 100)

        # Revenue
        model.Add(primary_revenue == value + 5)
        model.Add(secondary_revenue == 500)

        # Difficulty Level
        model.Add(difficulty_level == 40*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.A_NAIVE_COLLECTOR:
        model.Add(skeleton_in_progress >= 100)

        value_remainder = model.NewIntVar(0, 249, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 250)

        # Revenue
        model.Add(primary_revenue == value - value_remainder)
        model.Add(secondary_revenue == 0)

        # Difficulty Level
        model.Add(difficulty_level == 25*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity <= 0)

        value_remainder = model.NewIntVar(0, 249, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 250)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 1000)
        model.Add(secondary_revenue == 250*counter_church)

        # Difficulty Level
        model.Add(difficulty_level == 50*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER:
        model.Add(skeleton_in_progress >= 100)
        model.Add(menace <= 0)

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 1000)
        model.Add(secondary_revenue == 0)
        
        # Difficulty Level
        model.Add(difficulty_level == 50*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL:
        model.Add(skeleton_in_progress >= 100)
        model.Add(amalgamy <= 0)

        value_remainder = model.NewIntVar(0, 249, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 250)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 1000)
        model.Add(secondary_revenue == 0)
        
        # Difficulty Level
        model.Add(difficulty_level == 50*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity > 0)

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder)
        model.Add(secondary_revenue == 250*antiquity + (250 if data['bone_market_fluctuations'] == Fluctuation.ANTIQUITY else 0))
        
        # Difficulty Level
        model.Add(difficulty_level == 45*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.MRS_PLENTY:
        model.Add(skeleton_in_progress >= 100)
        model.Add(menace > 0)

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder)
        model.Add(secondary_revenue == 250*menace)
        
        # Difficulty Level
        model.Add(difficulty_level == 45*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.A_TENTACLED_SERVANT:
        model.Add(skeleton_in_progress >= 100)
        model.Add(amalgamy > 0)

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 250*amalgamy + (250 if data['bone_market_fluctuations'] == Fluctuation.AMALGAMY else 0))
        
        # Difficulty Level
        model.Add(difficulty_level == 45*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.AN_INVESTMENT_MINDED_AMBASSADOR:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity > 0)

        antiquity_squared = model.NewIntVar(0, cp_model.INT32_MAX, 'antiquity squared')
        model.AddMultiplicationEquality(antiquity_squared, [antiquity, antiquity])

        tailfeathers = model.NewIntVar(0, cp_model.INT32_MAX, 'tailfeathers')
        if data['bone_market_fluctuations'] == Fluctuation.ANTIQUITY:
            model.AddApproximateExponentiationEquality(tailfeathers, antiquity, 2.2, MAXIMUM_ATTRIBUTE)
        else:
            model.Add(tailfeathers == antiquity_squared)

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)
        extra_value = model.NewIntermediateBoolVar('extra value', value_remainder, cp_model.Domain.FromFlatIntervals([0, cp_model.INT_MAX]))

        # Revenue
        model.Add(primary_revenue == value + 50*extra_value + 250)
        model.Add(secondary_revenue == 250*tailfeathers)
        
        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Exhaustion
        derived_exhaustion = model.NewIntVar(0, cp_model.INT32_MAX, 'derived exhaustion')
        model.AddDivisionEquality(derived_exhaustion, antiquity_squared, 20)

        model.Add(exhaustion == derived_exhaustion + cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.A_TELLER_OF_TERRORS:
        model.Add(skeleton_in_progress >= 100)
        model.Add(menace > 0)

        menace_squared = model.NewIntVar(0, cp_model.INT32_MAX, 'menace squared')
        model.AddMultiplicationEquality(menace_squared, [menace, menace])

        value_remainder = model.NewIntVar(0, 9, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 10)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 50)
        model.Add(secondary_revenue == 50*menace_squared)
        
        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Exhaustion
        derived_exhaustion = model.NewIntVar(0, cp_model.INT32_MAX, 'derived exhaustion')
        model.AddDivisionEquality(derived_exhaustion, menace_squared, 100)

        model.Add(exhaustion == derived_exhaustion + cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.A_TENTACLED_ENTREPRENEUR:
        model.Add(skeleton_in_progress >= 100)
        model.Add(amalgamy > 0)

        amalgamy_squared = model.NewIntVar(0, cp_model.INT32_MAX, 'amalgamy squared')
        model.AddMultiplicationEquality(amalgamy_squared, [amalgamy, amalgamy])

        final_breaths = model.NewIntVar(0, cp_model.INT32_MAX, 'final breaths')
        if data['bone_market_fluctuations'] == Fluctuation.AMALGAMY:
            model.AddApproximateExponentiationEquality(final_breaths, amalgamy, 2.2, MAXIMUM_ATTRIBUTE)
        else:
            model.Add(final_breaths == amalgamy_squared)

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 50*final_breaths)
        
        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Exhaustion
        derived_exhaustion = model.NewIntVar(0, cp_model.INT32_MAX, 'derived exhaustion')
        model.AddDivisionEquality(derived_exhaustion, amalgamy_squared, 100)

        model.Add(exhaustion == derived_exhaustion + cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.AN_AUTHOR_OF_GOTHIC_TALES:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity > 0)
        model.Add(menace > 0)

        antiquity_times_menace = model.NewIntVar(0, cp_model.INT32_MAX, 'antiquity times menace')
        model.AddMultiplicationEquality(antiquity_times_menace, [antiquity, menace])

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 250*antiquity_times_menace + 250*(menace if data['bone_market_fluctuations'] == Fluctuation.ANTIQUITY else 0))

        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Exhaustion
        derived_exhaustion = model.NewIntVar(0, cp_model.INT32_MAX, 'derived exhaustion')
        model.AddDivisionEquality(derived_exhaustion, antiquity_times_menace, 20)

        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]) + derived_exhaustion)
    elif data['buyer'] == Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS:
        model.Add(skeleton_in_progress >= 100)
        model.Add(antiquity > 0)
        model.Add(amalgamy > 0)

        amalgamy_times_antiquity = model.NewIntVar(0, cp_model.INT32_MAX, 'amalgamy times antiquity')
        model.AddMultiplicationEquality(amalgamy_times_antiquity, [amalgamy, antiquity])

        value_remainder = model.NewIntVar(0, 9, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 10)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 250*amalgamy_times_antiquity + 250*(amalgamy if data['bone_market_fluctuations'] == Fluctuation.ANTIQUITY else antiquity if data['bone_market_fluctuations'] == Fluctuation.AMALGAMY else 0))

        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Exhaustion
        derived_exhaustion = model.NewIntVar(0, cp_model.INT32_MAX, 'derived exhaustion')
        model.AddDivisionEquality(derived_exhaustion, amalgamy_times_antiquity, 20)

        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]) + derived_exhaustion)
    elif data['buyer'] == Buyer.A_RUBBERY_COLLECTOR:
        model.Add(skeleton_in_progress >= 100)
        model.Add(amalgamy > 0)
        model.Add(menace > 0)

        amalgamy_times_menace = model.NewIntVar(0, cp_model.INT32_MAX, 'amalgamy times menace')
        model.AddMultiplicationEquality(amalgamy_times_menace, [amalgamy, menace])

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 250)
        model.Add(secondary_revenue == 250*amalgamy_times_menace + 250*(menace if data['bone_market_fluctuations'] == Fluctuation.AMALGAMY else 0))

        # Difficulty Level
        model.Add(difficulty_level == 75*implausibility)

        # Exhaustion
        derived_exhaustion = model.NewIntVar(0, cp_model.INT32_MAX, 'derived exhaustion')
        model.AddDivisionEquality(derived_exhaustion, amalgamy_times_menace, 20)

        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]) + derived_exhaustion)
    elif data['buyer'] == Buyer.A_CONSTABLE:
        model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([110, 119]))

        value_remainder = model.NewIntVar(0, 49, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 50)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 1000)
        model.Add(secondary_revenue == 0)

        # Difficulty Level
        model.Add(difficulty_level == 50*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.AN_ENTHUSIAST_IN_SKULLS:
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

        # Exhaustion
        derived_exhaustion = model.NewIntVar(0, cp_model.INT32_MAX, 'derived exhaustion')
        model.AddDivisionEquality(derived_exhaustion, vital_intelligence, 4)

        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]) + derived_exhaustion)
    elif data['buyer'] == Buyer.A_DREARY_MIDNIGHTER:
        model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([110, 299]))
        model.Add(amalgamy <= 0)
        model.Add(counter_church <= 0)

        value_remainder = model.NewIntVar(0, 2, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 3)

        # Revenue
        model.Add(primary_revenue == value - value_remainder + 300)
        model.Add(secondary_revenue == 250)

        # Difficulty Level
        model.Add(difficulty_level == 100*implausibility)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))
    elif data['buyer'] == Buyer.THE_DUMBWAITER_OF_BALMORAL:
        model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([180, 189]))
        model.Add(value >= 250)
        value_remainder = model.NewIntVar(0, 249, 'value remainder')
        model.AddModuloEquality(value_remainder, value, 250)

        # Revenue
        model.Add(primary_revenue == value - value_remainder)
        model.Add(secondary_revenue == 0)

        # Difficulty Level
        model.Add(difficulty_level == 200)

        # Exhaustion
        model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.exhaustion for action in actions.keys()]))


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
