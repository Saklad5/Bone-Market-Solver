"""Use constraint programming to devise the optimal skeleton at the Bone Market in Fallen London."""

__all__ = ['Adjustment', 'Appendage', 'Buyer', 'Declaration', 'DiplomatFascination', 'Embellishment', 'Fluctuation', 'OccasionalBuyer', 'Skull', 'Solve', 'Torso']
__author__ = "Jeremy Saklad"

from functools import partialmethod

from ortools.sat.python import cp_model

from .data.adjustments import Adjustment
from .data.appendages import Appendage
from .data.buyers import Buyer
from .data.costs import Cost
from .data.declarations import Declaration
from .data.diplomat_fascinations import DiplomatFascination
from .data.embellishments import Embellishment
from .data.fluctuations import Fluctuation
from .data.occasional_buyers import OccasionalBuyer
from .data.skulls import Skull
from .data.torsos import Torso
from .objects.bone_market_model import BoneMarketModel

# This multiplier is applied to the profit margin to avoid losing precision due to rounding.
PROFIT_MARGIN_MULTIPLIER = 10000

# This is the highest number of attribute to calculate fractional exponents for.
MAXIMUM_ATTRIBUTE = 100

# This is a constant used to calculate difficulty checks. You almost certainly do not need to change this.
DIFFICULTY_SCALER = 0.6


def Solve(shadowy_level, bone_market_fluctuations = None, zoological_mania = None, occasional_buyer = None, diplomat_fascination = None, desired_buyers = [], maximum_cost = cp_model.INT32_MAX, maximum_exhaustion = cp_model.INT32_MAX, time_limit = float('inf'), workers = None, blacklist = [], stdscr = None):
    model = BoneMarketModel()

    actions = {}

    # Torso
    for torso in Torso:
        actions[torso] = model.NewBoolVar(torso.value.name)

    # Skull
    for skull in Skull:
        actions[skull] = model.NewIntVar(skull.value.name, lb = 0)

    # Appendage
    for appendage in Appendage:
        if appendage == Appendage.SKIP_TAILS:
            actions[appendage] = model.NewBoolVar(appendage.value.name)
        else:
            actions[appendage] = model.NewIntVar(appendage.value.name, lb = 0)
    # Avoid adding joints at first
    model.AddHint(actions[Appendage.ADD_JOINTS], 0)

    # Adjustment
    for adjustment in Adjustment:
        actions[adjustment] = model.NewIntVar(adjustment.value.name, lb = 0)

    # Declaration
    for declaration in Declaration:
        actions[declaration] = model.NewBoolVar(declaration.value.name)
    # Try non-Chimera declarations first
    model.AddHint(actions[Declaration.CHIMERA], 0)

    # Embellishment
    for embellishment in Embellishment:
        actions[embellishment] = model.NewIntVar(embellishment.value.name, lb = 0)


    # Buyer
    for buyer in Buyer:
        actions[buyer] = model.NewBoolVar(buyer.value.name)

    # Mark unavailable buyers
    model.AddAssumptions([
        actions[buyer].Not()
        for unavailable_buyer in OccasionalBuyer if unavailable_buyer != occasional_buyer
        for buyer in unavailable_buyer.value if buyer not in desired_buyers
        ])
    model.AddAssumptions([
        actions[outmoded_fascination.value].Not()
        for outmoded_fascination in DiplomatFascination if outmoded_fascination != diplomat_fascination and outmoded_fascination.value not in desired_buyers
        ])

    # Restrict to desired buyers
    if desired_buyers:
        model.Add(cp_model.LinearExpr.Sum([actions[desired_buyer] for desired_buyer in desired_buyers]) == 1)

    # Blacklist
    model.Add(cp_model.LinearExpr.Sum([actions[forbidden] for forbidden in blacklist]) == 0)


    # One torso
    model.Add(cp_model.LinearExpr.Sum([value for (key, value) in actions.items() if isinstance(key, Torso)]) == 1)

    # One declaration
    model.Add(cp_model.LinearExpr.Sum([value for (key, value) in actions.items() if isinstance(key, Declaration)]) == 1)

    # One buyer
    model.Add(cp_model.LinearExpr.Sum([value for (key, value) in actions.items() if isinstance(key, Buyer)]) == 1)


    # Value calculation
    value = model.NewIntVar('value', lb = 0)

    base_value = model.NewIntVar('base value', lb = 0)
    model.Add(base_value == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.value for action in actions.keys()]))

    # Calculate value from Vake skulls
    # This is a partial sum formula.
    vake_skull_value = model.NewIntVar('vake skull value')

    vake_skulls = actions[Skull.VAKE_SKULL]

    vake_skulls_squared = model.NewIntVar('vake skulls squared', lb = 0)
    model.AddMultiplicationEquality(vake_skulls_squared, (vake_skulls, vake_skulls))

    model.Add(vake_skull_value == -250 * vake_skulls_squared + 6750 * vake_skulls)

    del vake_skulls, vake_skulls_squared

    model.Add(value == base_value + vake_skull_value)

    del base_value, vake_skull_value

    # Zoological Mania
    zoological_mania_bonus = model.NewIntVar('zoological mania bonus', lb = 0)
    if zoological_mania:
        multiplier = 15 if zoological_mania in [Declaration.FISH, Declaration.INSECT, Declaration.SPIDER] else 10

        potential_zoological_mania_bonus = model.NewIntVar('potential zoological mania bonus', lb = 0)
        multiplied_value = model.NewIntVar('multiplied value', lb = 0)
        model.Add(multiplied_value == multiplier*value)
        model.AddDivisionEquality(potential_zoological_mania_bonus, multiplied_value, 100)
        model.Add(zoological_mania_bonus == potential_zoological_mania_bonus).OnlyEnforceIf(actions[zoological_mania])
        model.Add(zoological_mania_bonus == 0).OnlyEnforceIf(actions[zoological_mania].Not())

        del multiplier, potential_zoological_mania_bonus, multiplied_value
    else:
        model.Add(zoological_mania_bonus == 0)


    # Torso Style calculation
    torso_style = model.NewIntVarFromDomain(cp_model.Domain.FromValues([torso.value.torso_style for torso in Torso]), 'torso style')
    for torso, torso_variable in {key: value for (key, value) in actions.items() if isinstance(key, Torso)}.items():
        model.Add(torso_style == torso.value.torso_style).OnlyEnforceIf(torso_variable)

    # Skulls calculation
    skulls = model.NewIntVar('skulls', lb = 0)
    model.Add(skulls == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.skulls for action in actions.keys()]))

    # Arms calculation
    arms = model.NewIntVar('arms', lb = 0)
    model.Add(arms == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.arms for action in actions.keys()]))

    # Legs calculation
    legs = model.NewIntVar('legs', lb = 0)
    model.Add(legs == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.legs for action in actions.keys()]))

    # Tails calculation
    tails = model.NewIntVar('tails', lb = 0)
    model.Add(tails == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tails for action in actions.keys()]))

    # Wings calculation
    wings = model.NewIntVar('wings', lb = 0)
    model.Add(wings == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.wings for action in actions.keys()]))

    # Fins calculation
    fins = model.NewIntVar('fins', lb = 0)
    model.Add(fins == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.fins for action in actions.keys()]))

    # Tentacles calculation
    tentacles = model.NewIntVar('tentacles', lb = 0)
    model.Add(tentacles == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tentacles for action in actions.keys()]))

    # Amalgamy calculation
    amalgamy = model.NewIntVar('amalgamy', lb = 0)
    unbound_amalgamy = model.NewIntVar('unbound amalgamy')
    model.Add(unbound_amalgamy == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.amalgamy for action in actions.keys()]))
    model.AddMaxEquality(amalgamy, (unbound_amalgamy, 0))
    del unbound_amalgamy

    # Antiquity calculation
    antiquity = model.NewIntVar('antiquity', lb = 0)
    unbound_antiquity = model.NewIntVar('unbound antiquity')
    model.Add(unbound_antiquity == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.antiquity for action in actions.keys()]))
    model.AddMaxEquality(antiquity, (unbound_antiquity, 0))
    del unbound_antiquity


    # Menace calculation
    menace = model.NewIntVar('menace', lb = 0)

    unbound_menace = model.NewIntVar('unbound menace')

    constant_base_menace = model.NewIntVar('constant base menace')
    model.Add(constant_base_menace == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.menace for action in actions.keys()]))

    # Calculate menace from Vake skulls
    vake_skull_bonus_menace = model.NewIntVarFromDomain(cp_model.Domain.FromValues([0, 2, 3]), 'vake skull bonus menace')
    vake_skulls_times_two = model.NewIntVar('vake skulls times two', lb = 0)
    model.AddMultiplicationEquality(vake_skulls_times_two, (2, actions[Skull.VAKE_SKULL]))
    model.AddMinEquality(vake_skull_bonus_menace, [vake_skulls_times_two, 3])
    del vake_skulls_times_two

    model.Add(unbound_menace == constant_base_menace + vake_skull_bonus_menace)
    model.AddMaxEquality(menace, (unbound_menace, 0))
    del unbound_menace, constant_base_menace, vake_skull_bonus_menace


    # Implausibility calculation
    implausibility = model.NewIntVar('implausibility')

    constant_base_implausibility = model.NewIntVar('implausibility')
    model.Add(constant_base_implausibility == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.implausibility for action in actions.keys()]))

    # Calculate implausibility from Vake skulls
    # This is a partial sum formula.
    vake_skull_implausibility = model.NewIntVar('vake skull implausibility', lb = 0)

    vake_skull_implausibility_numerator = model.NewIntVar('vake skull implausibility numerator', lb = 0)

    vake_skulls = actions[Skull.VAKE_SKULL]

    vake_skull_implausibility_numerator_second_term = model.NewIntVar('vake skull implausibility numerator second term', lb = 0)
    model.AddMultiplicationEquality(vake_skull_implausibility_numerator_second_term, (vake_skulls, vake_skulls))

    vake_skull_implausibility_numerator_third_term = model.NewIntVar('vake skull implausibility numerator third term', lb = 0, ub = 1)
    model.AddModuloEquality(vake_skull_implausibility_numerator_third_term, vake_skulls, 2)

    model.Add(vake_skull_implausibility_numerator == -2 * vake_skulls + vake_skull_implausibility_numerator_second_term + vake_skull_implausibility_numerator_third_term)

    del vake_skulls, vake_skull_implausibility_numerator_second_term, vake_skull_implausibility_numerator_third_term

    model.AddDivisionEquality(vake_skull_implausibility, vake_skull_implausibility_numerator, 4)

    del vake_skull_implausibility_numerator

    model.Add(implausibility == constant_base_implausibility + vake_skull_implausibility)

    del constant_base_implausibility, vake_skull_implausibility


    # Counter-church calculation
    # Calculate amount of Counter-church from Holy Relics of the Thigh of Saint Fiacre
    holy_relic = actions[Appendage.FIACRE_THIGH]
    torso_style_divided_by_ten = model.NewIntVar('torso style divided by ten', lb = 0)
    model.AddDivisionEquality(torso_style_divided_by_ten, torso_style, 10)
    holy_relic_counter_church = model.NewIntVar('holy relic counter-church', lb = 0)
    model.AddMultiplicationEquality(holy_relic_counter_church, (holy_relic, torso_style_divided_by_ten))

    counter_church = model.NewIntVar('counter-church', lb = 0)
    model.Add(counter_church == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.counter_church for action in actions.keys()]) + holy_relic_counter_church)

    del holy_relic, torso_style_divided_by_ten, holy_relic_counter_church


    # Exhaustion calculation
    exhaustion = model.NewIntVar('exhaustion', lb = 0, ub = maximum_exhaustion)

    # Exhaustion added by certain buyers
    added_exhaustion = model.NewIntVar('added exhaustion', lb = 0, ub = maximum_exhaustion)
    model.Add(exhaustion == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.exhaustion for action in actions.keys()]) + added_exhaustion)


    # Profit intermediate variables
    primary_revenue = model.NewIntVar('primary revenue', lb = 0)
    secondary_revenue = model.NewIntVar('secondary revenue', lb = 0)
    total_revenue = model.NewIntVar('total revenue', lb = 0)
    model.Add(total_revenue == cp_model.LinearExpr.Sum([primary_revenue, secondary_revenue]))


    # Cost
    # Calculate value of actions needed to sell the skeleton.
    difficulty_level = model.NewIntVar('difficulty level')

    non_zero_difficulty_level = model.NewIntVar('non-zero difficulty level', lb = 1)
    model.AddMaxEquality(non_zero_difficulty_level, [difficulty_level, 1])

    sale_actions_times_action_value = model.NewIntVar('sale actions times action value', lb = 0)
    model.AddDivisionEquality(sale_actions_times_action_value, model.NewConstant(round(DIFFICULTY_SCALER*shadowy_level*Cost.ACTION.value)), non_zero_difficulty_level)
    abstract_sale_cost = model.NewIntVar('abstract sale cost', lb = 0)
    model.AddDivisionEquality(abstract_sale_cost, Cost.ACTION.value**2, sale_actions_times_action_value)
    sale_cost = model.NewIntVar('sale cost', lb = 0)
    model.AddMaxEquality(sale_cost, [abstract_sale_cost, Cost.ACTION.value])

    del non_zero_difficulty_level, sale_actions_times_action_value, abstract_sale_cost


    # Calculate cost of adding joints
    # This is a partial sum formula.
    add_joints_amber_cost = model.NewIntVar('add joints amber cost', lb = 0)

    add_joints = actions[Appendage.ADD_JOINTS]

    base_joints = model.NewIntVar('base joints', lb = 0)
    model.Add(base_joints == cp_model.LinearExpr.ScalProd([value for (key, value) in actions.items() if isinstance(key, Torso)], [torso.value.limbs_needed + torso.value.arms + torso.value.legs + torso.value.wings + torso.value.fins + torso.value.tentacles for torso in Torso]))

    add_joints_amber_cost_multiple = model.NewIntVar('add joints amber cost multiple', lb = 0)

    add_joints_amber_cost_multiple_first_term = model.NewIntVar('add joints amber cost multiple first term', lb = 0)
    model.AddMultiplicationEquality(add_joints_amber_cost_multiple_first_term, (25, base_joints, base_joints, add_joints))

    add_joints_amber_cost_multiple_second_term = model.NewIntVar('add joints amber cost multiple second term', lb = 0)
    model.AddMultiplicationEquality(add_joints_amber_cost_multiple_second_term, (100, base_joints, add_joints, add_joints))

    add_joints_amber_cost_multiple_third_term = model.NewIntVar('add joints amber cost multiple third term', lb = 0)
    model.AddMultiplicationEquality(add_joints_amber_cost_multiple_third_term, (100, base_joints, add_joints))

    add_joints_amber_cost_multiple_fourth_term = model.NewIntVar('add joints amber cost multiple fourth term', lb = 0)
    add_joints_amber_cost_multiple_fourth_term_numerator = model.NewIntVar('add joints amber cost multiple fourth term numerator', lb = 0)
    add_joints_amber_cost_multiple_fourth_term_numerator_first_term = model.NewIntVar('add joints amber cost multiple fourth term numerator first term', lb = 0)
    model.AddMultiplicationEquality(add_joints_amber_cost_multiple_fourth_term_numerator_first_term, (400, add_joints, add_joints, add_joints))
    model.Add(add_joints_amber_cost_multiple_fourth_term_numerator == add_joints_amber_cost_multiple_fourth_term_numerator_first_term + 200*add_joints)
    model.AddDivisionEquality(add_joints_amber_cost_multiple_fourth_term, add_joints_amber_cost_multiple_fourth_term_numerator, 3)
    del add_joints_amber_cost_multiple_fourth_term_numerator, add_joints_amber_cost_multiple_fourth_term_numerator_first_term

    add_joints_amber_cost_multiple_fifth_term = model.NewIntVar('add joints amber cost multiple fifth term', lb = 0)
    model.AddMultiplicationEquality(add_joints_amber_cost_multiple_fifth_term, (200, add_joints, add_joints))

    model.Add(add_joints_amber_cost_multiple == add_joints_amber_cost_multiple_first_term + add_joints_amber_cost_multiple_second_term - add_joints_amber_cost_multiple_third_term + add_joints_amber_cost_multiple_fourth_term - add_joints_amber_cost_multiple_fifth_term)

    del add_joints_amber_cost_multiple_first_term, add_joints_amber_cost_multiple_second_term, add_joints_amber_cost_multiple_third_term, add_joints_amber_cost_multiple_fourth_term, add_joints_amber_cost_multiple_fifth_term

    model.AddMultiplicationEquality(add_joints_amber_cost, (add_joints_amber_cost_multiple, Cost.WARM_AMBER.value))

    del add_joints, add_joints_amber_cost_multiple


    cost = model.NewIntVar('cost', lb = 0, ub = maximum_cost)
    model.Add(cost == cp_model.LinearExpr.ScalProd(actions.values(), [int(action.value.cost) for action in actions.keys()]) + add_joints_amber_cost + sale_cost)

    del sale_cost, add_joints_amber_cost


    # Type of skeleton
    skeleton_in_progress = model.NewIntVar('skeleton in progress', lb = 0)

    # Chimera
    model.Add(skeleton_in_progress == 100) \
            .OnlyEnforceIf(actions[Declaration.CHIMERA])
    # Humanoid
    model.Add(skeleton_in_progress == 110) \
            .OnlyEnforceIf(actions[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity == 0))
    # Ancient Humanoid (UNCERTAIN)
    model.Add(skeleton_in_progress == 111) \
            .OnlyEnforceIf(actions[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.BoolExpression(cp_model.BoundedLinearExpression(antiquity, (1, 5))))
    # Neanderthal
    model.Add(skeleton_in_progress == 112) \
            .OnlyEnforceIf(actions[Declaration.HUMANOID]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 6))
    # Ape (UNCERTAIN)
    model.Add(skeleton_in_progress == 120) \
            .OnlyEnforceIf(actions[Declaration.APE]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 1))
    # Primordial Ape (UNCERTAIN)
    model.Add(skeleton_in_progress == 121) \
            .OnlyEnforceIf(actions[Declaration.APE]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 2))
    # Monkey
    model.Add(skeleton_in_progress == 125) \
            .OnlyEnforceIf(actions[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity == 0))
    # Catarrhine Monkey (UNCERTAIN)
    model.Add(skeleton_in_progress == 126) \
            .OnlyEnforceIf(actions[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.BoolExpression(cp_model.BoundedLinearExpression(antiquity, (1, 8))))
    # Catarrhine Monkey
    model.Add(skeleton_in_progress == 128) \
            .OnlyEnforceIf(actions[Declaration.MONKEY]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 9))
    # Crocodile
    model.Add(skeleton_in_progress == 160) \
            .OnlyEnforceIf(actions[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 1))
    # Dinosaur
    model.Add(skeleton_in_progress == 161) \
            .OnlyEnforceIf(actions[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.BoolExpression(cp_model.BoundedLinearExpression(antiquity, (2, 4))))
    # Mesosaur (UNCERTAIN)
    model.Add(skeleton_in_progress == 162) \
            .OnlyEnforceIf(actions[Declaration.REPTILE]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 5))
    # Toad
    model.Add(skeleton_in_progress == 170) \
            .OnlyEnforceIf(actions[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 1))
    # Primordial Amphibian
    model.Add(skeleton_in_progress == 171) \
            .OnlyEnforceIf(actions[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.BoolExpression(cp_model.BoundedLinearExpression(antiquity, (2, 4))))
    # Temnospondyl
    model.Add(skeleton_in_progress == 172) \
            .OnlyEnforceIf(actions[Declaration.AMPHIBIAN]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 5))
    # Owl
    model.Add(skeleton_in_progress == 180) \
            .OnlyEnforceIf(actions[Declaration.BIRD]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 1))
    # Archaeopteryx
    model.Add(skeleton_in_progress == 181) \
            .OnlyEnforceIf(actions[Declaration.BIRD]) \
            .OnlyEnforceIf(model.BoolExpression(cp_model.BoundedLinearExpression(antiquity, (2, 4))))
    # Ornithomimosaur (UNCERTAIN)
    model.Add(skeleton_in_progress == 182) \
            .OnlyEnforceIf(actions[Declaration.BIRD]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 5))
    # Lamprey
    model.Add(skeleton_in_progress == 190) \
            .OnlyEnforceIf(actions[Declaration.FISH]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity == 0))
    # Coelacanth (UNCERTAIN)
    model.Add(skeleton_in_progress == 191) \
            .OnlyEnforceIf(actions[Declaration.FISH]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 1))
    # Spider (UNCERTAIN)
    model.Add(skeleton_in_progress == 200) \
            .OnlyEnforceIf(actions[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 1))
    # Primordial Orb-Weaver (UNCERTAIN)
    model.Add(skeleton_in_progress == 201) \
            .OnlyEnforceIf(actions[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.BoolExpression(cp_model.BoundedLinearExpression(antiquity, (2, 7))))
    # Trigonotarbid
    model.Add(skeleton_in_progress == 203) \
            .OnlyEnforceIf(actions[Declaration.SPIDER]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 8))
    # Beetle (UNCERTAIN)
    model.Add(skeleton_in_progress == 210) \
            .OnlyEnforceIf(actions[Declaration.INSECT]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 1))
    # Primordial Beetle (UNCERTAIN)
    model.Add(skeleton_in_progress == 211) \
            .OnlyEnforceIf(actions[Declaration.INSECT]) \
            .OnlyEnforceIf(model.BoolExpression(cp_model.BoundedLinearExpression(antiquity, (2, 6))))
    # Rhyniognatha
    model.Add(skeleton_in_progress == 212) \
            .OnlyEnforceIf(actions[Declaration.INSECT]) \
            .OnlyEnforceIf(model.BoolExpression(antiquity >= 7))
    # Curator
    model.Add(skeleton_in_progress == 300) \
            .OnlyEnforceIf(actions[Declaration.CURATOR])


    # Declaration requirements

    model.AddIf(actions[Declaration.HUMANOID],
        (part == 0 for part in (tails, fins, wings)),
        skulls == 1,
        (part == 2 for part in (legs, arms)),
        cp_model.BoundedLinearExpression(torso_style, (10, 20)),
    )

    model.AddIf(actions[Declaration.APE],
        (part == 0 for part in (legs, tails, fins, wings)),
        skulls == 1,
        arms == 4,
        cp_model.BoundedLinearExpression(torso_style, (10, 20)),
    )

    model.AddIf(actions[Declaration.MONKEY],
        (part == 0 for part in (legs, fins, wings)),
        (part == 1 for part in (skulls, tails)),
        arms == 4,
        cp_model.BoundedLinearExpression(torso_style, (10, 20)),
    )

    model.AddIf(actions[Declaration.BIRD],
        (part == 0 for part in (arms, fins)),
        tails < 2,
        (part == 2 for part in (legs, wings)),
        torso_style >= 20,
    )

    model.AddIf(actions[Declaration.CURATOR],
        (part == 0 for part in (fins, tails)),
        skulls == 1,
        (part == 2 for part in (arms, legs, wings)),
    )

    model.AddIf(actions[Declaration.REPTILE],
        (part == 0 for part in (fins, wings, arms)),
        (part == 1 for part in (tails, skulls)),
        legs < 5,
        torso_style >= 20,
    )

    model.AddIf(actions[Declaration.AMPHIBIAN],
        (part == 0 for part in (tails, fins, wings, arms)),
        skulls == 1,
        legs == 4,
        torso_style >= 20,
    )

    model.AddIf(actions[Declaration.FISH],
        (part == 0 for part in (arms, legs, wings)),
        tails <= 1,
        skulls == 1,
        fins >= 2,
        torso_style >= 20,
    )

    model.AddIf(actions[Declaration.INSECT],
        (part == 0 for part in (arms, fins, tails)),
        skulls == 1,
        wings < 5,
        legs == 6,
        torso_style >= 20,
    )

    model.AddIf(actions[Declaration.SPIDER],
        (part == 0 for part in (skulls, arms, wings, fins)),
        tails <= 1,
        legs == 8,
        torso_style >= 20,
    )

    # Skeleton must have no unfilled skulls
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.skulls_needed for action in actions.keys()]) == 0)

    # Skeleton must have no unfilled limbs
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.limbs_needed for action in actions.keys()]) == 0)

    # Skeleton must have no unfilled tails, unless they were skipped
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tails_needed for action in actions.keys()]) == 0).OnlyEnforceIf(actions[Appendage.SKIP_TAILS].Not())
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tails_needed for action in actions.keys()]) > 0).OnlyEnforceIf(actions[Appendage.SKIP_TAILS])


    model.AddIf(actions[Buyer.A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES],
        skeleton_in_progress >= 100,
        primary_revenue == value + zoological_mania_bonus + 5,
        secondary_revenue == 500,
        difficulty_level == 40*implausibility,
        added_exhaustion == 0,
    )

    model.AddIf(actions[Buyer.A_NAIVE_COLLECTOR],
        skeleton_in_progress >= 100,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue, value + zoological_mania_bonus, 250),
        secondary_revenue == 0,
        difficulty_level == 25*implausibility,
        added_exhaustion == 0,
    )

    model.AddIf(actions[Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS],
        skeleton_in_progress >= 100,
        antiquity == 0,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 1000, value + zoological_mania_bonus, 250),
        secondary_revenue == 250*counter_church,
        difficulty_level == 50*implausibility,
        added_exhaustion == 0,
    )

    model.AddIf(actions[Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER],
        skeleton_in_progress >= 100,
        menace == 0,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 1000, value + zoological_mania_bonus, 50),
        secondary_revenue == 0,
        difficulty_level == 50*implausibility,
        added_exhaustion == 0,
    )

    model.AddIf(actions[Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL],
        skeleton_in_progress >= 100,
        amalgamy == 0,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 1000, value + zoological_mania_bonus, 250),
        secondary_revenue == 0,
        difficulty_level == 50*implausibility,
        added_exhaustion == 0,
    )

    model.AddIf(actions[Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD],
        skeleton_in_progress >= 100,
        antiquity > 0,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue, value + zoological_mania_bonus, 50),
        secondary_revenue == 250*(antiquity + (1 if bone_market_fluctuations == Fluctuation.ANTIQUITY else 0)),
        difficulty_level == 45*implausibility,
        added_exhaustion == 0,
    )

    model.AddIf(actions[Buyer.MRS_PLENTY],
        skeleton_in_progress >= 100,
        menace > 0,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue, value + zoological_mania_bonus, 50),
        secondary_revenue == 250*menace,
        difficulty_level == 45*implausibility,
        added_exhaustion == 0,
    )

    model.AddIf(actions[Buyer.A_TENTACLED_SERVANT],
        skeleton_in_progress >= 100,
        amalgamy > 0,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 250, value + zoological_mania_bonus, 50),
        secondary_revenue == 250*(amalgamy + (1 if bone_market_fluctuations == Fluctuation.AMALGAMY else 0)),
        difficulty_level == 45*implausibility,
        added_exhaustion == 0,
    )


    # An Investment-Minded Ambassador
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.AN_INVESTMENT_MINDED_AMBASSADOR])
    model.Add(antiquity > 0).OnlyEnforceIf(actions[Buyer.AN_INVESTMENT_MINDED_AMBASSADOR])

    antiquity_squared_times_four_fifths = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: antiquity squared times four-fifths', lb = 0)
    antiquity_squared_times_four = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: antiquity squared times four', lb = 0)
    model.AddMultiplicationEquality(antiquity_squared_times_four, (antiquity, antiquity, 4))
    model.AddDivisionEquality(antiquity_squared_times_four_fifths, antiquity_squared_times_four, 5)
    del antiquity_squared_times_four

    tailfeathers = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: tailfeathers')
    if bone_market_fluctuations == Fluctuation.ANTIQUITY:
        boosted_antiquity = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: boosted antiquity', lb = 0)
        model.AddApproximateExponentiationEquality(boosted_antiquity, antiquity, 2.1, MAXIMUM_ATTRIBUTE)
        boosted_antiquity_times_four = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: boosted antiquity times four', lb = 0)
        model.AddMultiplicationEquality(boosted_antiquity_times_four, (boosted_antiquity, 4))
        boosted_antiquity_times_four_fifths = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: boosted antiquity times four-fifths', lb = 0)
        model.AddDivisionEquality(boosted_antiquity_times_four_fifths, boosted_antiquity_times_four, 5)
        model.Add(tailfeathers == boosted_antiquity_times_four_fifths).OnlyEnforceIf(actions[Buyer.AN_INVESTMENT_MINDED_AMBASSADOR])
        del boosted_antiquity, boosted_antiquity_times_four, boosted_antiquity_times_four_fifths
    else:
        model.Add(tailfeathers == antiquity_squared_times_four_fifths).OnlyEnforceIf(actions[Buyer.AN_INVESTMENT_MINDED_AMBASSADOR])

    total_value = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)
    extra_value = model.BoolExpression(total_value_remainder >= 0)

    model.Add(primary_revenue == total_value + 50*extra_value + 250).OnlyEnforceIf(actions[Buyer.AN_INVESTMENT_MINDED_AMBASSADOR])
    model.Add(secondary_revenue == 250*tailfeathers).OnlyEnforceIf(actions[Buyer.AN_INVESTMENT_MINDED_AMBASSADOR])

    model.Add(difficulty_level == 75*implausibility).OnlyEnforceIf(actions[Buyer.AN_INVESTMENT_MINDED_AMBASSADOR])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.AN_INVESTMENT_MINDED_AMBASSADOR.name}: derived exhaustion', lb = 0)
    model.AddDivisionEquality(derived_exhaustion, antiquity_squared_times_four_fifths, 20)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.AN_INVESTMENT_MINDED_AMBASSADOR])

    del antiquity_squared_times_four_fifths, tailfeathers, total_value, total_value_remainder, extra_value, derived_exhaustion


    # A Teller of Terrors
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_TELLER_OF_TERRORS])
    model.Add(menace > 0).OnlyEnforceIf(actions[Buyer.A_TELLER_OF_TERRORS])

    menace_squared = model.NewIntVar(f'{Buyer.A_TELLER_OF_TERRORS.name}: menace squared', lb = 0)
    model.AddMultiplicationEquality(menace_squared, (menace, menace))

    feathers = model.NewIntVar(f'{Buyer.A_TELLER_OF_TERRORS.name}: feathers')
    if bone_market_fluctuations == Fluctuation.MENACE:
        boosted_menace = model.NewIntVar(f'{Buyer.A_TELLER_OF_TERRORS.name}: boosted menace')
        model.AddApproximateExponentiationEquality(boosted_menace, menace, 2.1, MAXIMUM_ATTRIBUTE)
        model.Add(feathers == 4*boosted_menace).OnlyEnforceIf(actions[Buyer.A_TELLER_OF_TERRORS])
        del boosted_menace
    else:
        model.Add(feathers == 4*menace_squared).OnlyEnforceIf(actions[Buyer.A_TELLER_OF_TERRORS])

    total_value = model.NewIntVar(f'{Buyer.A_TELLER_OF_TERRORS.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_TELLER_OF_TERRORS.name}: total value remainder', lb = 0, ub = 9)
    model.AddModuloEquality(total_value_remainder, total_value, 10)

    model.Add(primary_revenue == total_value - total_value_remainder + 50).OnlyEnforceIf(actions[Buyer.A_TELLER_OF_TERRORS])
    model.Add(secondary_revenue == 50*feathers).OnlyEnforceIf(actions[Buyer.A_TELLER_OF_TERRORS])

    model.Add(difficulty_level == 75*implausibility).OnlyEnforceIf(actions[Buyer.A_TELLER_OF_TERRORS])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.A_TELLER_OF_TERRORS.name}: derived exhaustion', lb = 0)
    model.AddDivisionEquality(derived_exhaustion, menace_squared, 25)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.A_TELLER_OF_TERRORS])

    del menace_squared, feathers, total_value, total_value_remainder, derived_exhaustion


    # A Tentacled Entrepreneur
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_TENTACLED_ENTREPRENEUR])
    model.Add(amalgamy > 0).OnlyEnforceIf(actions[Buyer.A_TENTACLED_ENTREPRENEUR])

    amalgamy_squared = model.NewIntVar(f'{Buyer.A_TENTACLED_ENTREPRENEUR.name}: amalgamy squared', lb = 0)
    model.AddMultiplicationEquality(amalgamy_squared, (amalgamy, amalgamy))

    final_breaths = model.NewIntVar(f'{Buyer.A_TENTACLED_ENTREPRENEUR.name}: final breaths')
    if bone_market_fluctuations == Fluctuation.AMALGAMY:
        boosted_amalgamy = model.NewIntVar(f'{Buyer.A_TENTACLED_ENTREPRENEUR.name}: boosted amalgamy')
        model.AddApproximateExponentiationEquality(boosted_amalgamy, amalgamy, 2.1, MAXIMUM_ATTRIBUTE)
        model.Add(final_breaths == 4*boosted_amalgamy).OnlyEnforceIf(actions[Buyer.A_TENTACLED_ENTREPRENEUR])
        del boosted_amalgamy
    else:
        model.Add(final_breaths == 4*amalgamy_squared).OnlyEnforceIf(actions[Buyer.A_TENTACLED_ENTREPRENEUR])

    total_value = model.NewIntVar(f'{Buyer.A_TENTACLED_ENTREPRENEUR.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_TENTACLED_ENTREPRENEUR.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder + 250).OnlyEnforceIf(actions[Buyer.A_TENTACLED_ENTREPRENEUR])
    model.Add(secondary_revenue == 50*final_breaths).OnlyEnforceIf(actions[Buyer.A_TENTACLED_ENTREPRENEUR])

    model.Add(difficulty_level == 75*implausibility).OnlyEnforceIf(actions[Buyer.A_TENTACLED_ENTREPRENEUR])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.A_TENTACLED_ENTREPRENEUR.name}: derived exhaustion', lb = 0)
    model.AddDivisionEquality(derived_exhaustion, amalgamy_squared, 25)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.A_TENTACLED_ENTREPRENEUR])

    del amalgamy_squared, final_breaths, total_value, total_value_remainder, derived_exhaustion


    # An Author of Gothic Tales
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.AN_AUTHOR_OF_GOTHIC_TALES])
    model.Add(antiquity > 0).OnlyEnforceIf(actions[Buyer.AN_AUTHOR_OF_GOTHIC_TALES])
    model.Add(menace > 0).OnlyEnforceIf(actions[Buyer.AN_AUTHOR_OF_GOTHIC_TALES])

    antiquity_times_menace = model.NewIntVar(f'{Buyer.AN_AUTHOR_OF_GOTHIC_TALES.name}: antiquity times menace')
    model.AddMultiplicationEquality(antiquity_times_menace, (antiquity, menace))

    antiquity_fluctuation_bonus = model.NewIntVar(f'{Buyer.AN_AUTHOR_OF_GOTHIC_TALES.name}: antiquity fluctuation bonus')
    model.AddDivisionEquality(antiquity_fluctuation_bonus, antiquity, 2)

    menace_fluctuation_bonus = model.NewIntVar(f'{Buyer.AN_AUTHOR_OF_GOTHIC_TALES.name}: menace fluctuation bonus')
    model.AddDivisionEquality(menace_fluctuation_bonus, menace, 2)

    total_value = model.NewIntVar(f'{Buyer.AN_AUTHOR_OF_GOTHIC_TALES.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.AN_AUTHOR_OF_GOTHIC_TALES.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder + 250).OnlyEnforceIf(actions[Buyer.AN_AUTHOR_OF_GOTHIC_TALES])
    model.Add(secondary_revenue == 250*antiquity_times_menace + 250*(antiquity_fluctuation_bonus if bone_market_fluctuations == Fluctuation.ANTIQUITY else menace_fluctuation_bonus if bone_market_fluctuations == Fluctuation.MENACE else 0)).OnlyEnforceIf(actions[Buyer.AN_AUTHOR_OF_GOTHIC_TALES])

    model.Add(difficulty_level == 75*implausibility).OnlyEnforceIf(actions[Buyer.AN_AUTHOR_OF_GOTHIC_TALES])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.AN_AUTHOR_OF_GOTHIC_TALES.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, antiquity_times_menace, 20)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.AN_AUTHOR_OF_GOTHIC_TALES])

    del antiquity_times_menace, antiquity_fluctuation_bonus, menace_fluctuation_bonus, total_value, total_value_remainder, derived_exhaustion


    # A Zailor with Particular Interests
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS])
    model.Add(antiquity > 0).OnlyEnforceIf(actions[Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS])
    model.Add(amalgamy > 0).OnlyEnforceIf(actions[Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS])

    amalgamy_times_antiquity = model.NewIntVar(f'{Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS.name}: amalgamy times antiquity')
    model.AddMultiplicationEquality(amalgamy_times_antiquity, (amalgamy, antiquity))

    amalgamy_fluctuation_bonus = model.NewIntVar(f'{Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS.name}: amalgamy fluctuation bonus')
    model.AddDivisionEquality(amalgamy_fluctuation_bonus, amalgamy, 2)

    antiquity_fluctuation_bonus = model.NewIntVar(f'{Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS.name}: antiquity fluctuation bonus')
    model.AddDivisionEquality(antiquity_fluctuation_bonus, antiquity, 2)

    total_value = model.NewIntVar(f'{Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS.name}: total value remainder', lb = 0, ub = 9)
    model.AddModuloEquality(total_value_remainder, total_value, 10)

    model.Add(primary_revenue == total_value - total_value_remainder + 250).OnlyEnforceIf(actions[Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS])
    model.Add(secondary_revenue == 250*amalgamy_times_antiquity + 250*(amalgamy_fluctuation_bonus if bone_market_fluctuations == Fluctuation.AMALGAMY else antiquity_fluctuation_bonus if bone_market_fluctuations == Fluctuation.ANTIQUITY else 0)).OnlyEnforceIf(actions[Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS])

    model.Add(difficulty_level == 75*implausibility).OnlyEnforceIf(actions[Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, amalgamy_times_antiquity, 20)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.A_ZAILOR_WITH_PARTICULAR_INTERESTS])

    del amalgamy_times_antiquity, amalgamy_fluctuation_bonus, antiquity_fluctuation_bonus, total_value, total_value_remainder, derived_exhaustion


    # A Rubbery Collector
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_RUBBERY_COLLECTOR])
    model.Add(amalgamy > 0).OnlyEnforceIf(actions[Buyer.A_RUBBERY_COLLECTOR])
    model.Add(menace > 0).OnlyEnforceIf(actions[Buyer.A_RUBBERY_COLLECTOR])

    amalgamy_times_menace = model.NewIntVar(f'{Buyer.A_RUBBERY_COLLECTOR.name}: amalgamy times menace')
    model.AddMultiplicationEquality(amalgamy_times_menace, (amalgamy, menace))

    amalgamy_fluctuation_bonus = model.NewIntVar(f'{Buyer.A_RUBBERY_COLLECTOR.name}: amalgamy fluctuation bonus')
    model.AddDivisionEquality(amalgamy_fluctuation_bonus, amalgamy, 2)

    menace_fluctuation_bonus = model.NewIntVar(f'{Buyer.A_RUBBERY_COLLECTOR.name}: menace fluctuation bonus')
    model.AddDivisionEquality(menace_fluctuation_bonus, menace, 2)

    total_value = model.NewIntVar(f'{Buyer.A_RUBBERY_COLLECTOR.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_RUBBERY_COLLECTOR.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder + 250).OnlyEnforceIf(actions[Buyer.A_RUBBERY_COLLECTOR])
    model.Add(secondary_revenue == 250*amalgamy_times_menace + 250*(amalgamy_fluctuation_bonus if bone_market_fluctuations == Fluctuation.AMALGAMY else menace_fluctuation_bonus if bone_market_fluctuations == Fluctuation.MENACE else 0)).OnlyEnforceIf(actions[Buyer.A_RUBBERY_COLLECTOR])

    model.Add(difficulty_level == 75*implausibility).OnlyEnforceIf(actions[Buyer.A_RUBBERY_COLLECTOR])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.A_RUBBERY_COLLECTOR.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, amalgamy_times_menace, 20)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.A_RUBBERY_COLLECTOR])

    del amalgamy_times_menace, amalgamy_fluctuation_bonus, menace_fluctuation_bonus, total_value, total_value_remainder, derived_exhaustion


    model.AddIf(actions[Buyer.A_CONSTABLE],
        cp_model.BoundedLinearExpression(skeleton_in_progress, (110, 119)),
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 1000, value, 50),
        secondary_revenue == 0,
        difficulty_level == 50*implausibility,
        added_exhaustion == 0,
    )


    # An Enthusiast in Skulls
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_IN_SKULLS])
    model.Add(skulls >= 2).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_IN_SKULLS])

    extra_skulls = model.NewIntVar(f'{Buyer.AN_ENTHUSIAST_IN_SKULLS.name}: extra skulls', lb = 0)
    model.Add(extra_skulls == skulls - 1).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_IN_SKULLS])
    vital_intelligence = model.NewIntVar(f'{Buyer.AN_ENTHUSIAST_IN_SKULLS.name}: vital intelligence')
    model.AddApproximateExponentiationEquality(vital_intelligence, extra_skulls, 1.8, MAXIMUM_ATTRIBUTE)

    model.Add(primary_revenue == value + zoological_mania_bonus).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_IN_SKULLS])
    model.Add(secondary_revenue == 1250*vital_intelligence).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_IN_SKULLS])

    model.Add(difficulty_level == 60*implausibility).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_IN_SKULLS])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.AN_ENTHUSIAST_IN_SKULLS.name}: derived exhaustion', lb = 0)
    model.AddDivisionEquality(derived_exhaustion, vital_intelligence, 4)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_IN_SKULLS])

    del extra_skulls, vital_intelligence, derived_exhaustion


    model.AddIf(actions[Buyer.A_DREARY_MIDNIGHTER],
        cp_model.BoundedLinearExpression(skeleton_in_progress, (110, 299)),
        amalgamy == 0,
        counter_church == 0,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 300, value + zoological_mania_bonus, 3),
        secondary_revenue == 250,
        difficulty_level == 100*implausibility,
        added_exhaustion == 0,
    )

    {
        model.AddIf(actions[getattr(Buyer, 'A_COLOURFUL_PHANTASIST_' + style)],
            skeleton_in_progress >= 100,
            implausibility >= 2,
            attribute >= 4,
            partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 100, value + zoological_mania_bonus, 50),
            partialmethod(BoneMarketModel.AddMultiplicationEquality, secondary_revenue - 250, (250, attribute, implausibility)),
            difficulty_level == 0,
            partialmethod(BoneMarketModel.AddDivisionEquality, added_exhaustion, secondary_revenue, 5000),
        ) for style, attribute in (
                ('BAZAARINE', amalgamy),
                ('NOCTURNAL', menace),
                ('CELESTIAL', antiquity),
            )
    }


    # An Ingenuous Malacologist
    model.Add(tentacles >= 4).OnlyEnforceIf(actions[Buyer.AN_INGENUOUS_MALACOLOGIST])
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.AN_INGENUOUS_MALACOLOGIST])

    exponentiated_tentacles = model.NewIntVar(f'{Buyer.AN_INGENUOUS_MALACOLOGIST.name}: exponentiated tentacles', lb = 0)
    model.AddApproximateExponentiationEquality(exponentiated_tentacles, tentacles, 2.2, MAXIMUM_ATTRIBUTE)

    collated_research = model.NewIntVar(f'{Buyer.AN_INGENUOUS_MALACOLOGIST.name}: collated research')
    model.AddDivisionEquality(collated_research, exponentiated_tentacles, 5)

    value_remainder = model.NewIntVar(f'{Buyer.AN_INGENUOUS_MALACOLOGIST.name}: value remainder', lb = 0, ub = 249)
    model.AddModuloEquality(value_remainder, value, 250)

    model.Add(primary_revenue == value - value_remainder + 250).OnlyEnforceIf(actions[Buyer.AN_INGENUOUS_MALACOLOGIST])
    model.Add(secondary_revenue == 250*collated_research).OnlyEnforceIf(actions[Buyer.AN_INGENUOUS_MALACOLOGIST])

    model.Add(difficulty_level == 60*implausibility).OnlyEnforceIf(actions[Buyer.AN_INGENUOUS_MALACOLOGIST])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.AN_INGENUOUS_MALACOLOGIST.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, exponentiated_tentacles, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.AN_INGENUOUS_MALACOLOGIST])

    del exponentiated_tentacles, collated_research, value_remainder, derived_exhaustion


    # An Enterprising Boot Salesman
    model.Add(menace == 0).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])
    model.Add(amalgamy == 0).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])
    model.Add(legs >= 4).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])

    diamonds = model.NewIntVar(f'{Buyer.AN_ENTERPRISING_BOOT_SALESMAN.name}: diamonds', lb = 0)
    model.AddApproximateExponentiationEquality(diamonds, legs, 2.2, MAXIMUM_ATTRIBUTE)

    total_value = model.NewIntVar(f'{Buyer.AN_ENTERPRISING_BOOT_SALESMAN.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.AN_ENTERPRISING_BOOT_SALESMAN.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])
    model.Add(secondary_revenue == 50*diamonds).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.AN_ENTERPRISING_BOOT_SALESMAN.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, diamonds, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])

    del diamonds, total_value, total_value_remainder, derived_exhaustion


    model.AddIf(actions[Buyer.THE_DUMBWAITER_OF_BALMORAL],
        cp_model.BoundedLinearExpression(skeleton_in_progress, (180, 189)),
        value >= 250,
        partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue, value, 250),
        secondary_revenue == 0,
        difficulty_level == 200,
        added_exhaustion == 0,
    )

    model.AddIf(actions[Buyer.THE_CARPENTERS_GRANDDAUGHTER],
        skeleton_in_progress >= 100,
        value + zoological_mania_bonus >= 30000,
        primary_revenue == 31250,
        secondary_revenue == 0,
        difficulty_level == 100*implausibility,
        added_exhaustion == 0,
    )

    # The Trifling Diplomat
    {
        model.AddIf(actions[getattr(DiplomatFascination, str(attribute).upper()).value],
            skeleton_in_progress >= 100,
            attribute >= 5,
            partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 50, value, 50),
            partialmethod(BoneMarketModel.AddMultiplicationEquality, secondary_revenue, (50, attribute, attribute)),
            difficulty_level == 0,
            partialmethod(BoneMarketModel.AddDivisionEquality, added_exhaustion, secondary_revenue, 5000),
        ) for attribute in (
                amalgamy,
                antiquity,
                menace,
            )
    }
    for fascination, criteria in (
            ('BIRD', (cp_model.BoundedLinearExpression(skeleton_in_progress, (180, 189)),)),
            ('FISH', (cp_model.BoundedLinearExpression(skeleton_in_progress, (190, 199)),)),
            ('INSECT', (cp_model.BoundedLinearExpression(skeleton_in_progress, (210, 219)),)),
            ('REPTILE', (cp_model.BoundedLinearExpression(skeleton_in_progress, (160, 169)),)),
            ('SKULLS', (skeleton_in_progress >= 100, skulls >= 5)),
        ):
        compromising_documents = model.NewIntVar(f'{getattr(DiplomatFascination, fascination).name}: compromising documents')
        compromising_documents_constraints = model.AddDivisionApproximateExponentiationEquality(compromising_documents, cp_model.LinearExpr.Sum((amalgamy, antiquity, menace)), 3, 2.2, MAXIMUM_ATTRIBUTE)
        model.AddIf(actions[getattr(DiplomatFascination, fascination).value],
            *criteria,
            partialmethod(BoneMarketModel.AddDivisionMultiplicationEquality, primary_revenue - 50, value, 50),
            secondary_revenue == 50*compromising_documents,
            compromising_documents_constraints, # Applies enforcement literal to intermediate calculations
            difficulty_level == 0,
            partialmethod(BoneMarketModel.AddDivisionEquality, added_exhaustion, secondary_revenue, 5000),
        )
    else:
        del fascination, criteria, compromising_documents, compromising_documents_constraints


    # Maximize profit margin
    net_profit = model.NewIntVar('net profit')
    model.Add(net_profit == total_revenue - cost)

    # This is necessary to preserve some degree of precision after dividing
    multiplied_net_profit = model.NewIntVar('multiplied net profit', lb = cp_model.INT32_MIN*PROFIT_MARGIN_MULTIPLIER, ub = cp_model.INT32_MAX*PROFIT_MARGIN_MULTIPLIER)
    model.AddMultiplicationEquality(multiplied_net_profit, (net_profit, PROFIT_MARGIN_MULTIPLIER))

    absolute_multiplied_net_profit = model.NewIntVar('absolute multiplied net profit', lb = 0, ub = cp_model.INT32_MAX*PROFIT_MARGIN_MULTIPLIER)
    model.AddAbsEquality(absolute_multiplied_net_profit, multiplied_net_profit)

    absolute_profit_margin = model.NewIntVar('absolute profit margin', lb = cp_model.INT32_MIN*PROFIT_MARGIN_MULTIPLIER, ub = cp_model.INT32_MAX*PROFIT_MARGIN_MULTIPLIER)
    model.AddDivisionEquality(absolute_profit_margin, absolute_multiplied_net_profit, total_revenue)

    profit_margin = model.NewIntVar('profit margin', lb = cp_model.INT32_MIN*PROFIT_MARGIN_MULTIPLIER, ub = cp_model.INT32_MAX*PROFIT_MARGIN_MULTIPLIER)

    positive_net_profit = model.BoolExpression(net_profit >= 0)
    model.Add(profit_margin == absolute_profit_margin).OnlyEnforceIf(positive_net_profit)
    model.Add(profit_margin == absolute_profit_margin*-1).OnlyEnforceIf(positive_net_profit.Not())

    del multiplied_net_profit, absolute_multiplied_net_profit, absolute_profit_margin, positive_net_profit


    model.Maximize(profit_margin)


    class SkeletonPrinter(cp_model.CpSolverSolutionCallback):
        """A class that prints the steps that comprise a skeleton as well as relevant attributes."""

        __slots__ = 'this', '__solution_count'

        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__solution_count = 0

        def PrintableSolution(self, solver = None):
            """Print the latest solution of a provided solver."""

            output = ""

            # Allows use as a callback
            if solver is None:
                solver = self

            for action in actions.keys():
                for _ in range(int(solver.Value(actions[action]))):
                    output += str(action) + "\n"

            output += f"""
Profit: £{solver.Value(net_profit)/100:,.2f}
Profit Margin: {solver.Value(profit_margin)/PROFIT_MARGIN_MULTIPLIER:+,.2%}

Total Revenue: £{solver.Value(total_revenue)/100:,.2f}
Primary Revenue: £{solver.Value(primary_revenue)/100:,.2f}
Secondary Revenue: £{solver.Value(secondary_revenue)/100:,.2f}

Cost: £{solver.Value(cost)/100:,.2f}

Value: £{solver.Value(value)/100:,.2f}
Amalgamy: {solver.Value(amalgamy):n}
Antiquity: {solver.Value(antiquity):n}
Menace: {solver.Value(menace):n}
Counter-Church: {solver.Value(counter_church):n}
Implausibility: {solver.Value(implausibility):n}

Exhaustion: {solver.Value(exhaustion):n}"""

            return output


        def OnSolutionCallback(self):
            self.__solution_count += 1

            # Prints current solution to window
            stdscr.clear()
            stdscr.addstr(self.PrintableSolution())

            stdscr.addstr(stdscr.getmaxyx()[0] - 1, 0, f"Skeleton #{self.__solution_count:n}")

            stdscr.refresh()


        def SolutionCount(self):
            return self.__solution_count


    printer = SkeletonPrinter()

    solver = cp_model.CpSolver()
    if workers:
        solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit

    # There's no window in verbose mode
    if stdscr is None:
        solver.parameters.log_search_progress = True
        solver.Solve(model)
    else:
        solver.Solve(model, printer)

    status = solver.StatusName()

    if status == 'INFEASIBLE':
        raise RuntimeError("There is no satisfactory skeleton.")
    elif status == 'FEASIBLE':
        print("WARNING: skeleton may be suboptimal.")
    elif status != 'OPTIMAL':
        raise RuntimeError(f"Unknown status returned: {status}.")

    return printer.PrintableSolution(solver)
