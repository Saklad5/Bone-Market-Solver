__author__: str = "Jeremy Saklad"

from collections.abc import Iterable
from functools import cache, partialmethod, reduce, singledispatch, singledispatchmethod
from numbers import Integral, Number
from typing import Final

from ortools.sat.python import cp_model

class BoneMarketModel(cp_model.CpModel):
    """A CpModel with additional functions for common constraints and enhanced enforcement literal support."""

    __slots__: tuple[()] = ()

    def AddAllowedAssignments(self, variables: Iterable[Iterable], tuples_list: Iterable[Iterable]) -> tuple:
        # Used for variable names
        invocation: Final[str] = repr((variables, tuples_list))

        intermediate_variables, constraints = zip(*(self.NewIntermediateIntVar(variable, f'{invocation}: {variable}') for variable in variables))
        super().AddAllowedAssignments(intermediate_variables, tuples_list)
        return constraints

    def AddApproximateExponentiationEquality(self, target, var, exp: Number, upto: Integral) -> tuple:
        """Add an approximate exponentiation equality using a lookup table.

Set `upto` to a value that is unlikely to come into play.

Each parameter is interpreted as a BoundedLinearExpression, and a layer of indirection is applied such that each Constraint in the returned tuple can accept an enforcement literal."""
        return self.AddAllowedAssignments((target, var), ((int(base**exp), base) for base in range(upto + 1)))

    def AddDivisionEquality(self, target, num, denom) -> tuple:
        """Adds `target == num // denom` (integer division rounded towards 0).

Each parameter is interpreted as a BoundedLinearExpression, and a layer of indirection is applied such that each Constraint in the returned tuple can accept an enforcement literal."""
        # Used for variable names
        invocation: Final[str] = f'{repr(target)} == {repr(num)} // {repr(denom)}'

        intermediate_target, target_constraint = self.NewIntermediateIntVar(target, f'{invocation}: target')
        intermediate_num, num_constraint = self.NewIntermediateIntVar(num, f'{invocation}: num', lb=0)
        intermediate_denom, denom_constraint = self.NewIntermediateIntVar(denom, f'{invocation}: denom', lb=1)

        super().AddDivisionEquality(intermediate_target, intermediate_num, intermediate_denom)
        return (target_constraint, num_constraint, denom_constraint)

    def AddIf(self, variable, *constraints: tuple) -> frozenset:
        """Add constraints to the model, only enforced if the specified variable is true.

Each item in `constraints` must be either a BoundedLinearExpression, a Constraint compatible with OnlyEnforceIf, a 0-arity partial method of CpModel returning a valid item, or an iterable containing valid items."""

        @singledispatch
        def Add(constraint: Iterable) -> frozenset:
            return frozenset((Add(element) for element in constraint))

        @Add.register
        def _(constraint: cp_model.Constraint) -> cp_model.Constraint:
            return constraint.OnlyEnforceIf(variable)

        @Add.register
        def _(constraint: cp_model.BoundedLinearExpression) -> cp_model.Constraint:
            return Add(self.Add(constraint))

        @Add.register
        def _(constraint: partialmethod):
            return Add(constraint.__get__(self)())

        return frozenset((Add(constraint) for constraint in constraints))

    def AddMultiplicationEquality(self, target, variables: Iterable) -> tuple:
        """Adds `target == variables[0] * .. * variables[n]`.

Each parameter is interpreted as a BoundedLinearExpression, and a layer of indirection is applied such that each Constraint in the returned tuple can accept an enforcement literal."""

        superclass: Final = super()

        def Multiply(end, stack: list) -> tuple:
            intermediate_variable, variable_constraint = self.NewIntermediateIntVar(stack.pop(), f'{repr(end)} == {"*".join((repr(variable) for variable in stack))}: last variable')

            partial_target: Final[cp_model.IntVar] = self.NewIntVar(f'{repr(end)} == {"*".join((repr(variable) for variable in stack))}: partial target')
            recursive_constraints: Final[tuple] = self.AddMultiplicationEquality(partial_target, stack) if len(stack) > 1 else (self.Add(partial_target == stack.pop()),)

            intermediate_target, target_constraint = self.NewIntermediateIntVar(end, f'{repr(end)} == {"*".join((repr(variable) for variable in stack))}: target')

            superclass.AddMultiplicationEquality(intermediate_target, (partial_target, intermediate_variable))

            return (variable_constraint, *recursive_constraints, target_constraint)

        # Avoid mutating parameter directly
        return Multiply(target, variables.copy() if isinstance(variables, list) else list(variables))

    @cache
    def BoolExpression(self, bounded_linear_exp: cp_model.BoundedLinearExpression) -> cp_model.IntVar:
        """Add a fully-reified implication using an intermediate Boolean variable."""

        intermediate: Final[cp_model.IntVar] = self.NewBoolVar(str(bounded_linear_exp))
        linear_exp: Final[cp_model.LinearExp] = bounded_linear_exp.Expression()
        domain: Final[cp_model.Domain] = cp_model.Domain(*bounded_linear_exp.Bounds())
        self.AddLinearExpressionInDomain(linear_exp, domain).OnlyEnforceIf(intermediate)
        self.AddLinearExpressionInDomain(linear_exp, domain.Complement()).OnlyEnforceIf(intermediate.Not())
        return intermediate

    @singledispatchmethod
    def NewIntermediateIntVar(self, expression: cp_model.LinearExpr, name: str, *, lb: Integral = cp_model.INT32_MIN, ub: Integral = cp_model.INT32_MAX) -> tuple[cp_model.IntVar, cp_model.Constraint]:
        """Creates an integer variable equivalent to the given expression and returns a tuple consisting of the variable and constraint for use with enforcement literals.

`equality` must be either a LinearExp or a unary partialmethod that accepts a target integer variable and returns Constraints."""

        intermediate: Final[cp_model.IntVar] = super().NewIntVar(lb, ub, name)
        return (intermediate, self.Add(intermediate == expression))

    @NewIntermediateIntVar.register
    def _(self, expression: partialmethod, name: str, *, lb: Integral = cp_model.INT32_MIN, ub: Integral = cp_model.INT32_MAX) -> tuple:
        intermediate: Final[cp_model.IntVar] = super().NewIntVar(lb, ub, name)
        return (intermediate, expression.__get__(self)(intermediate))

    def NewIntVar(self, name: str, *, lb: Integral = cp_model.INT32_MIN, ub: Integral = cp_model.INT32_MAX) -> cp_model.IntVar:
        return super().NewIntVar(lb, ub, name)
