"""Use constraint programming to devise the optimal skeleton at the Bone Market in Fallen London."""

__all__ = ['Adjustment', 'Appendage', 'Buyer', 'Declaration', 'DiplomatFascination', 'Embellishment', 'Fluctuation', 'OccasionalBuyer', 'Skull', 'Solve', 'Torso']
__author__ = "Jeremy Saklad"

from os import cpu_count

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
PROFIT_MARGIN_MULTIPLIER = 10000000

# This is the highest number of attribute to calculate fractional exponents for.
MAXIMUM_ATTRIBUTE = 100

# This is a constant used to calculate difficulty checks. You almost certainly do not need to change this.
DIFFICULTY_SCALER = 0.6


def Solve(shadowy_level, bone_market_fluctuations = None, zoological_mania = None, occasional_buyer = None, diplomat_fascination = None, desired_buyers = [], maximum_cost = cp_model.INT32_MAX, maximum_exhaustion = cp_model.INT32_MAX, time_limit = float('inf'), workers = cpu_count(), blacklist = [], stdscr = None):
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
    amalgamy = model.NewIntVar('amalgamy')
    model.Add(amalgamy == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.amalgamy for action in actions.keys()]))

    # Antiquity calculation
    antiquity = model.NewIntVar('antiquity')
    model.Add(antiquity == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.antiquity for action in actions.keys()]))


    # Menace calculation
    menace = model.NewIntVar('menace')

    constant_base_menace = model.NewIntVar('constant base menace')
    model.Add(constant_base_menace == cp_model.LinearExpr.ScalProd(actions.values(), [action.value.menace for action in actions.keys()]))

    # Calculate menace from Vake skulls
    vake_skull_bonus_menace = model.NewIntVarFromDomain(cp_model.Domain.FromValues([0, 2, 3]), 'vake skull bonus menace')
    vake_skulls_times_two = model.NewIntVar('vake skulls times two', lb = 0)
    model.AddMultiplicationEquality(vake_skulls_times_two, (2, actions[Skull.VAKE_SKULL]))
    model.AddMinEquality(vake_skull_bonus_menace, [vake_skulls_times_two, 3])
    del vake_skulls_times_two

    model.Add(menace == constant_base_menace + vake_skull_bonus_menace)

    del constant_base_menace, vake_skull_bonus_menace


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

    counter_church = model.NewIntVar('counter-church')
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
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 0))
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
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 0))
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
            .OnlyEnforceIf(model.BoolExpression(antiquity <= 0))
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


    # Humanoid requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.HUMANOID])
    model.Add(legs == 2).OnlyEnforceIf(actions[Declaration.HUMANOID])
    model.Add(arms == 2).OnlyEnforceIf(actions[Declaration.HUMANOID])
    model.AddLinearExpressionInDomain(torso_style, cp_model.Domain.FromFlatIntervals([10, 20])).OnlyEnforceIf(actions[Declaration.HUMANOID])
    for prohibited_quality in [tails, fins, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.HUMANOID])

    # Ape requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.APE])
    model.Add(arms == 4).OnlyEnforceIf(actions[Declaration.APE])
    model.AddLinearExpressionInDomain(torso_style, cp_model.Domain.FromFlatIntervals([10, 20])).OnlyEnforceIf(actions[Declaration.APE])
    for prohibited_quality in [legs, tails, fins, wings]:
        model.Add(prohibited_quality == 0).OnlyEnforceIf(actions[Declaration.APE])

    # Monkey requirements
    model.Add(skulls == 1).OnlyEnforceIf(actions[Declaration.MONKEY])
    model.Add(arms == 4).OnlyEnforceIf(actions[Declaration.MONKEY])
    model.Add(tails == 1).OnlyEnforceIf(actions[Declaration.MONKEY])
    model.AddLinearExpressionInDomain(torso_style, cp_model.Domain.FromFlatIntervals([10, 20])).OnlyEnforceIf(actions[Declaration.MONKEY])
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
    model.Add(cp_model.LinearExpr.ScalProd(actions.values(), [action.value.tails_needed for action in actions.keys()]) > 0).OnlyEnforceIf(actions[Appendage.SKIP_TAILS])


    # A Palaeontologist with Hoarding Propensities
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES])

    model.Add(primary_revenue == value + zoological_mania_bonus + 5).OnlyEnforceIf(actions[Buyer.A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES])
    model.Add(secondary_revenue == 500).OnlyEnforceIf(actions[Buyer.A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES])

    model.Add(difficulty_level == 40*implausibility).OnlyEnforceIf(actions[Buyer.A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.A_PALAEONTOLOGIST_WITH_HOARDING_PROPENSITIES])


    # A Naive Collector
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_NAIVE_COLLECTOR])

    total_value = model.NewIntVar(f'{Buyer.A_NAIVE_COLLECTOR.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_NAIVE_COLLECTOR.name}: total value remainder', lb = 0, ub = 249)
    model.AddModuloEquality(total_value_remainder, total_value, 250)

    model.Add(primary_revenue == total_value - total_value_remainder).OnlyEnforceIf(actions[Buyer.A_NAIVE_COLLECTOR])
    model.Add(secondary_revenue == 0).OnlyEnforceIf(actions[Buyer.A_NAIVE_COLLECTOR])

    model.Add(difficulty_level == 25*implausibility).OnlyEnforceIf(actions[Buyer.A_NAIVE_COLLECTOR])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.A_NAIVE_COLLECTOR])

    del total_value, total_value_remainder


    # A Familiar Bohemian Sculptress
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS])
    model.Add(antiquity <= 0).OnlyEnforceIf(actions[Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS])

    total_value = model.NewIntVar(f'{Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS.name}: total value remainder', lb = 0, ub = 249)
    model.AddModuloEquality(total_value_remainder, total_value, 250)

    model.Add(primary_revenue == total_value - total_value_remainder + 1000).OnlyEnforceIf(actions[Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS])
    model.Add(secondary_revenue == 250*counter_church).OnlyEnforceIf(actions[Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS])

    model.Add(difficulty_level == 50*implausibility).OnlyEnforceIf(actions[Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.A_FAMILIAR_BOHEMIAN_SCULPTRESS])

    del total_value, total_value_remainder


    # A Pedagogically Inclined Grandmother
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER])
    model.Add(menace <= 0).OnlyEnforceIf(actions[Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER])

    total_value = model.NewIntVar(f'{Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder + 1000).OnlyEnforceIf(actions[Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER])
    model.Add(secondary_revenue == 0).OnlyEnforceIf(actions[Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER])

    model.Add(difficulty_level == 50*implausibility).OnlyEnforceIf(actions[Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER])

    del total_value, total_value_remainder


    # A Theologian of the Old School
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL])
    model.Add(amalgamy <= 0).OnlyEnforceIf(actions[Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL])

    total_value = model.NewIntVar(f'{Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL.name}: total value remainder', lb = 0, ub = 249)
    model.AddModuloEquality(total_value_remainder, total_value, 250)

    model.Add(primary_revenue == total_value - total_value_remainder + 1000).OnlyEnforceIf(actions[Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL])
    model.Add(secondary_revenue == 0).OnlyEnforceIf(actions[Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL])

    model.Add(difficulty_level == 50*implausibility).OnlyEnforceIf(actions[Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.A_THEOLOGIAN_OF_THE_OLD_SCHOOL])

    del total_value, total_value_remainder


    # An Enthusiast of the Ancient World
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD])
    model.Add(antiquity > 0).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD])

    total_value = model.NewIntVar(f'{Buyer.A_PEDAGOGICALLY_INCLINED_GRANDMOTHER.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD])
    model.Add(secondary_revenue == 250*antiquity + (250 if bone_market_fluctuations == Fluctuation.ANTIQUITY else 0)).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD])

    model.Add(difficulty_level == 45*implausibility).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.AN_ENTHUSIAST_OF_THE_ANCIENT_WORLD])

    del total_value, total_value_remainder


    # Mrs Plenty
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.MRS_PLENTY])
    model.Add(menace > 0).OnlyEnforceIf(actions[Buyer.MRS_PLENTY])

    total_value = model.NewIntVar(f'{Buyer.MRS_PLENTY.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.MRS_PLENTY.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder).OnlyEnforceIf(actions[Buyer.MRS_PLENTY])
    model.Add(secondary_revenue == 250*menace).OnlyEnforceIf(actions[Buyer.MRS_PLENTY])

    model.Add(difficulty_level == 45*implausibility).OnlyEnforceIf(actions[Buyer.MRS_PLENTY])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.MRS_PLENTY])

    del total_value, total_value_remainder


    # A Tentacled Servant
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_TENTACLED_SERVANT])
    model.Add(amalgamy > 0).OnlyEnforceIf(actions[Buyer.A_TENTACLED_SERVANT])

    total_value = model.NewIntVar(f'{Buyer.A_TENTACLED_SERVANT.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_TENTACLED_SERVANT.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder + 250).OnlyEnforceIf(actions[Buyer.A_TENTACLED_SERVANT])
    model.Add(secondary_revenue == 250*amalgamy + (250 if bone_market_fluctuations == Fluctuation.AMALGAMY else 0)).OnlyEnforceIf(actions[Buyer.A_TENTACLED_SERVANT])

    model.Add(difficulty_level == 45*implausibility).OnlyEnforceIf(actions[Buyer.A_TENTACLED_SERVANT])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.A_TENTACLED_SERVANT])

    del total_value, total_value_remainder


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


    # A Constable
    model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([110, 119])).OnlyEnforceIf(actions[Buyer.A_CONSTABLE])

    value_remainder = model.NewIntVar(f'{Buyer.A_CONSTABLE.name}: value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(value_remainder, value, 50)

    model.Add(primary_revenue == value - value_remainder + 1000).OnlyEnforceIf(actions[Buyer.A_CONSTABLE])
    model.Add(secondary_revenue == 0).OnlyEnforceIf(actions[Buyer.A_CONSTABLE])

    model.Add(difficulty_level == 50*implausibility).OnlyEnforceIf(actions[Buyer.A_CONSTABLE])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.A_CONSTABLE])

    del value_remainder


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


    # A Dreary Midnighter
    model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([110, 299])).OnlyEnforceIf(actions[Buyer.A_DREARY_MIDNIGHTER])
    model.Add(amalgamy <= 0).OnlyEnforceIf(actions[Buyer.A_DREARY_MIDNIGHTER])
    model.Add(counter_church <= 0).OnlyEnforceIf(actions[Buyer.A_DREARY_MIDNIGHTER])

    total_value = model.NewIntVar(f'{Buyer.A_DREARY_MIDNIGHTER.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_DREARY_MIDNIGHTER.name}: total value remainder', lb = 0, ub = 2)
    model.AddModuloEquality(total_value_remainder, total_value, 3)

    model.Add(primary_revenue == total_value - total_value_remainder + 300).OnlyEnforceIf(actions[Buyer.A_DREARY_MIDNIGHTER])
    model.Add(secondary_revenue == 250).OnlyEnforceIf(actions[Buyer.A_DREARY_MIDNIGHTER])

    model.Add(difficulty_level == 100*implausibility).OnlyEnforceIf(actions[Buyer.A_DREARY_MIDNIGHTER])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.A_DREARY_MIDNIGHTER])

    del total_value, total_value_remainder


    # A Colourful Phantasist - Bazaarine
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE])
    model.Add(implausibility >= 2).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE])
    model.Add(amalgamy >= 4).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE])

    amalgamy_times_implausibility = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE.name}: amalgamy times implausibility')
    model.AddMultiplicationEquality(amalgamy_times_implausibility, (amalgamy, implausibility))

    bazaarine_poetry = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE.name}: bazaarine poetry')
    model.Add(bazaarine_poetry == amalgamy_times_implausibility + 1)

    total_value = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder + 100).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE])
    model.Add(secondary_revenue == 250*bazaarine_poetry).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, bazaarine_poetry, 20)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_BAZAARINE])

    del amalgamy_times_implausibility, bazaarine_poetry, total_value, total_value_remainder, derived_exhaustion


    # A Colourful Phantasist - Nocturnal
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL])
    model.Add(implausibility >= 2).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL])
    model.Add(menace >= 4).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL])

    menace_times_implausibility = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL.name}: menace times implausibility')
    model.AddMultiplicationEquality(menace_times_implausibility, (menace, implausibility))

    stygian_ivory = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL.name}: stygian ivory')
    model.Add(stygian_ivory == menace_times_implausibility + 1)

    total_value = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder + 100).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL])
    model.Add(secondary_revenue == 250*stygian_ivory).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, stygian_ivory, 20)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_NOCTURNAL])

    del menace_times_implausibility, stygian_ivory, total_value, total_value_remainder, derived_exhaustion


    # A Colourful Phantasist - Celestial
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL])
    model.Add(implausibility >= 2).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL])
    model.Add(antiquity >= 4).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL])

    antiquity_times_implausibility = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL.name}: antiquity times implausibility')
    model.AddMultiplicationEquality(antiquity_times_implausibility, (antiquity, implausibility))

    knob_of_scintillack = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL.name}: knob of scintillack')
    model.Add(knob_of_scintillack == antiquity_times_implausibility + 1)

    total_value = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL.name}: total value', lb = 0)
    model.Add(total_value == value + zoological_mania_bonus)

    total_value_remainder = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL.name}: total value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(total_value_remainder, total_value, 50)

    model.Add(primary_revenue == total_value - total_value_remainder + 100).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL])
    model.Add(secondary_revenue == 250*knob_of_scintillack).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, knob_of_scintillack, 20)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.A_COLOURFUL_PHANTASIST_CELESTIAL])

    del antiquity_times_implausibility, knob_of_scintillack, total_value, total_value_remainder, derived_exhaustion


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
    model.Add(menace <= 0).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])
    model.Add(amalgamy <= 0).OnlyEnforceIf(actions[Buyer.AN_ENTERPRISING_BOOT_SALESMAN])
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


    # The Dumbwaiter of Balmoral
    model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([180, 189])).OnlyEnforceIf(actions[Buyer.THE_DUMBWAITER_OF_BALMORAL])
    model.Add(value >= 250).OnlyEnforceIf(actions[Buyer.THE_DUMBWAITER_OF_BALMORAL])

    value_remainder = model.NewIntVar(f'{Buyer.THE_DUMBWAITER_OF_BALMORAL.name}: value remainder', lb = 0, ub = 249)
    model.AddModuloEquality(value_remainder, value, 250)

    model.Add(primary_revenue == value - value_remainder).OnlyEnforceIf(actions[Buyer.THE_DUMBWAITER_OF_BALMORAL])
    model.Add(secondary_revenue == 0).OnlyEnforceIf(actions[Buyer.THE_DUMBWAITER_OF_BALMORAL])

    model.Add(difficulty_level == 200).OnlyEnforceIf(actions[Buyer.THE_DUMBWAITER_OF_BALMORAL])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.THE_DUMBWAITER_OF_BALMORAL])

    del value_remainder


    # The Carpenter's Granddaughter
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.THE_CARPENTERS_GRANDDAUGHTER])
    model.Add(value + zoological_mania_bonus >= 30000).OnlyEnforceIf(actions[Buyer.THE_CARPENTERS_GRANDDAUGHTER])

    model.Add(primary_revenue == 31250).OnlyEnforceIf(actions[Buyer.THE_CARPENTERS_GRANDDAUGHTER])
    model.Add(secondary_revenue == 0).OnlyEnforceIf(actions[Buyer.THE_CARPENTERS_GRANDDAUGHTER])

    model.Add(difficulty_level == 100*implausibility).OnlyEnforceIf(actions[Buyer.THE_CARPENTERS_GRANDDAUGHTER])

    model.Add(added_exhaustion == 0).OnlyEnforceIf(actions[Buyer.THE_CARPENTERS_GRANDDAUGHTER])


    # The Trifling Diplomat - Amalgamy
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY])
    model.Add(amalgamy >= 5).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY])

    amalgamy_squared = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY.name}: amalgamy squared', lb = 0)
    model.AddMultiplicationEquality(amalgamy_squared, (amalgamy, amalgamy))

    value_remainder = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY.name}: value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(value_remainder, value, 50)

    model.Add(primary_revenue == value - value_remainder + 50).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY])
    model.Add(secondary_revenue == 50*amalgamy_squared).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, amalgamy_squared, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_AMALGAMY])

    del amalgamy_squared, value_remainder, derived_exhaustion


    # The Trifling Diplomat - Antiquity
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY])
    model.Add(antiquity >= 5).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY])

    antiquity_squared = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY.name}: antiquity squared', lb = 0)
    model.AddMultiplicationEquality(antiquity_squared, (antiquity, antiquity))

    value_remainder = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY.name}: value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(value_remainder, value, 50)

    model.Add(primary_revenue == value - value_remainder + 50).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY])
    model.Add(secondary_revenue == 50*antiquity_squared).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, antiquity_squared, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_ANTIQUITY])

    del antiquity_squared, value_remainder, derived_exhaustion


    # The Trifling Diplomat - Bird
    model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([180, 189])).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_BIRD])

    non_negative_amalgamy = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_BIRD.name}: non-negative amalgamy')
    model.AddMaxEquality(non_negative_amalgamy, [amalgamy, 0])

    non_negative_menace = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_BIRD.name}: non-negative menace')
    model.AddMaxEquality(non_negative_menace, [menace, 0])

    non_negative_antiquity = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_BIRD.name}: non-negative antiquity')
    model.AddMaxEquality(non_negative_antiquity, [antiquity, 0])

    compromising_documents = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_BIRD.name}: compromising documents', lb = 0)
    model.AddMultiplicationEquality(compromising_documents, (non_negative_amalgamy, non_negative_menace, non_negative_antiquity))

    value_remainder = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_BIRD.name}: value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(value_remainder, value, 50)

    model.Add(primary_revenue == value - value_remainder + 50).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_BIRD])
    model.Add(secondary_revenue == 50*compromising_documents).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_BIRD])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_BIRD])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_BIRD.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, compromising_documents, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_BIRD])

    del non_negative_amalgamy, non_negative_menace, non_negative_antiquity, compromising_documents, value_remainder, derived_exhaustion


    # The Trifling Diplomat - Fish
    model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([190, 199])).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_FISH])

    non_negative_amalgamy = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_FISH.name}: non-negative amalgamy')
    model.AddMaxEquality(non_negative_amalgamy, [amalgamy, 0])

    non_negative_menace = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_FISH.name}: non-negative menace')
    model.AddMaxEquality(non_negative_menace, [menace, 0])

    non_negative_antiquity = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_FISH.name}: non-negative antiquity')
    model.AddMaxEquality(non_negative_antiquity, [antiquity, 0])

    compromising_documents = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_FISH.name}: compromising documents', lb = 0)
    model.AddMultiplicationEquality(compromising_documents, (non_negative_amalgamy, non_negative_menace, non_negative_antiquity))

    value_remainder = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_FISH.name}: value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(value_remainder, value, 50)

    model.Add(primary_revenue == value - value_remainder + 50).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_FISH])
    model.Add(secondary_revenue == 50*compromising_documents).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_FISH])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_FISH])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_FISH.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, compromising_documents, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_FISH])

    del non_negative_amalgamy, non_negative_menace, non_negative_antiquity, compromising_documents, value_remainder, derived_exhaustion


    # The Trifling Diplomat - Insect
    model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([210, 219])).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_INSECT])

    non_negative_amalgamy = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_INSECT.name}: non-negative amalgamy')
    model.AddMaxEquality(non_negative_amalgamy, [amalgamy, 0])

    non_negative_menace = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_INSECT.name}: non-negative menace')
    model.AddMaxEquality(non_negative_menace, [menace, 0])

    non_negative_antiquity = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_INSECT.name}: non-negative antiquity')
    model.AddMaxEquality(non_negative_antiquity, [antiquity, 0])

    compromising_documents = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_INSECT.name}: compromising documents', lb = 0)
    model.AddMultiplicationEquality(compromising_documents, (non_negative_amalgamy, non_negative_menace, non_negative_antiquity))

    value_remainder = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_INSECT.name}: value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(value_remainder, value, 50)

    model.Add(primary_revenue == value - value_remainder + 50).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_INSECT])
    model.Add(secondary_revenue == 50*compromising_documents).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_INSECT])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_INSECT])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_INSECT.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, compromising_documents, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_INSECT])

    del non_negative_amalgamy, non_negative_menace, non_negative_antiquity, compromising_documents, value_remainder, derived_exhaustion


    # The Trifling Diplomat - Reptile
    model.AddLinearExpressionInDomain(skeleton_in_progress, cp_model.Domain.FromFlatIntervals([160, 169])).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_REPTILE])

    non_negative_amalgamy = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_REPTILE.name}: non-negative amalgamy')
    model.AddMaxEquality(non_negative_amalgamy, [amalgamy, 0])

    non_negative_menace = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_REPTILE.name}: non-negative menace')
    model.AddMaxEquality(non_negative_menace, [menace, 0])

    non_negative_antiquity = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_REPTILE.name}: non-negative antiquity')
    model.AddMaxEquality(non_negative_antiquity, [antiquity, 0])

    compromising_documents = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_REPTILE.name}: compromising documents', lb = 0)
    model.AddMultiplicationEquality(compromising_documents, (non_negative_amalgamy, non_negative_menace, non_negative_antiquity))

    value_remainder = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_REPTILE.name}: value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(value_remainder, value, 50)

    model.Add(primary_revenue == value - value_remainder + 50).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_REPTILE])
    model.Add(secondary_revenue == 50*compromising_documents).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_REPTILE])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_REPTILE])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_REPTILE.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, compromising_documents, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_REPTILE])

    del non_negative_amalgamy, non_negative_menace, non_negative_antiquity, compromising_documents, value_remainder, derived_exhaustion


    # The Trifling Diplomat - Skulls
    model.Add(skeleton_in_progress >= 100).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_SKULLS])
    model.Add(skulls >= 5).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_SKULLS])

    non_negative_amalgamy = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_SKULLS.name}: non-negative amalgamy')
    model.AddMaxEquality(non_negative_amalgamy, [amalgamy, 0])

    non_negative_menace = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_SKULLS.name}: non-negative menace')
    model.AddMaxEquality(non_negative_menace, [menace, 0])

    non_negative_antiquity = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_SKULLS.name}: non-negative antiquity')
    model.AddMaxEquality(non_negative_antiquity, [antiquity, 0])

    compromising_documents = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_SKULLS.name}: compromising documents', lb = 0)
    model.AddMultiplicationEquality(compromising_documents, (non_negative_amalgamy, non_negative_menace, non_negative_antiquity))

    value_remainder = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_SKULLS.name}: value remainder', lb = 0, ub = 49)
    model.AddModuloEquality(value_remainder, value, 50)

    model.Add(primary_revenue == value - value_remainder + 50).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_SKULLS])
    model.Add(secondary_revenue == 50*compromising_documents).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_SKULLS])

    model.Add(difficulty_level == 0).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_SKULLS])

    # The indirection is necessary for applying an enforcement literal
    derived_exhaustion = model.NewIntVar(f'{Buyer.THE_TRIFLING_DIPLOMAT_SKULLS.name}: derived exhaustion')
    model.AddDivisionEquality(derived_exhaustion, compromising_documents, 100)
    model.Add(added_exhaustion == derived_exhaustion).OnlyEnforceIf(actions[Buyer.THE_TRIFLING_DIPLOMAT_SKULLS])

    del non_negative_amalgamy, non_negative_menace, non_negative_antiquity, compromising_documents, value_remainder, derived_exhaustion


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
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit

    # There's no window in verbose mode
    if stdscr is None:
        solver.parameters.log_search_progress = True
        solver.Solve(model)
    else:
        solver.SolveWithSolutionCallback(model, printer)

    status = solver.StatusName()

    if status == 'INFEASIBLE':
        raise RuntimeError("There is no satisfactory skeleton.")
    elif status == 'FEASIBLE':
        print("WARNING: skeleton may be suboptimal.")
    elif status != 'OPTIMAL':
        raise RuntimeError(f"Unknown status returned: {status}.")

    return printer.PrintableSolution(solver)
