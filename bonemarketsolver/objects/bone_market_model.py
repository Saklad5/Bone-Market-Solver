__author__ = "Jeremy Saklad"

from functools import cache, partialmethod, reduce, singledispatch

from ortools.sat.python import cp_model

class BoneMarketModel(cp_model.CpModel):
    """A CpModel with additional functions for common constraints and enhanced enforcement literal support."""

    __slots__ = ()

    def AddAllowedAssignments(self, variables, tuples_list):
        intermediate_variables, constraints = zip(*(self.NewIntermediateIntVar(variable, f'{repr((variables, tuples_list))}: {variable}') for variable in variables))
        super().AddAllowedAssignments(intermediate_variables, tuples_list)
        return constraints

    def AddApproximateExponentiationEquality(self, target, var, exp, upto):
        """Add an approximate exponentiation equality using a lookup table.

Set `upto` to a value that is unlikely to come into play.

Each parameter is interpreted as a BoundedLinearExpression, and a layer of indirection is applied such that each Constraint in the returned tuple can accept an enforcement literal."""
        return self.AddAllowedAssignments((target, var), ((int(base**exp), base) for base in range(upto + 1)))

    def AddDivisionEquality(self, target, num, denom):
        """Adds `target == num // denom` (integer division rounded towards 0).

Each parameter is interpreted as a BoundedLinearExpression, and a layer of indirection is applied such that each Constraint in the returned tuple can accept an enforcement literal."""
        intermediate_target, target_constraint = self.NewIntermediateIntVar(target, f'{repr(target)} == {repr(num)} // {repr(denom)}: target')
        intermediate_num, num_constraint = self.NewIntermediateIntVar(num, f'{repr(target)} == {repr(num)} // {repr(denom)}: num', lb = 0)
        intermediate_denom, denom_constraint = self.NewIntermediateIntVar(denom, f'{repr(target)} == {repr(num)} // {repr(denom)}: denom', lb = 1)

        super().AddDivisionEquality(intermediate_target, intermediate_num, intermediate_denom)
        return (target_constraint, num_constraint, denom_constraint)

    def AddDivisionMultiplicationEquality(self, target, num, denom, multiple = None):
        """Adds `target == (num // denom) * multiple`.

Each parameter is interpreted as a BoundedLinearExpression, and a layer of indirection is applied such that each Constraint in the returned tuple can accept an enforcement literal.

`multiple` defaults to the same value as `denom` if unspecified."""
        quotient = self.NewIntVar(f'{repr(target)} == ({repr(num)} // {repr(denom)}) * {repr(multiple)}: quotient')
        intermediate_num, num_constraint = self.NewIntermediateIntVar(num, f'{repr(target)} == ({repr(num)} // {repr(denom)}) * {repr(multiple)}: num', lb = 0)
        intermediate_denom, denom_constraint = self.NewIntermediateIntVar(denom, f'{repr(target)} == ({repr(num)} // {repr(denom)}) * {repr(multiple)}: denom', lb = 1)
        intermediate_target, target_constraint = self.NewIntermediateIntVar(target, f'{repr(target)} == ({repr(num)} // {repr(denom)}) * {repr(multiple)}: target')
        if multiple:
            intermediate_multiple, multiple_constraint = self.NewIntermediateIntVar(multiple, f'{repr(target)} == ({repr(num)} // {repr(denom)}) * {repr(multiple)}: multiple')

        super().AddDivisionEquality(quotient, intermediate_num, intermediate_denom)
        super().AddMultiplicationEquality(intermediate_target, (quotient, intermediate_multiple if multiple else intermediate_denom))

        return (num_constraint, denom_constraint, target_constraint, *((multiple_constraint,) if multiple else ()))

    def AddIf(self, variable, *constraints):
        """Add constraints to the model, only enforced if the specified variable is true.

Each item in `constraints` must be either a BoundedLinearExpression, a Constraint compatible with OnlyEnforceIf, a 0-arity partial method of CpModel returning a valid item, or an iterable containing valid items."""

        @singledispatch
        def Add(constraint):
            if constraint_iterator := iter(constraint):
                return frozenset((Add(element) for element in constraint_iterator))
            else:
                raise TypeError(f"Invalid constraint: {repr(constraint)}")

        @Add.register
        def _(constraint: cp_model.Constraint):
            return constraint.OnlyEnforceIf(variable)

        @Add.register
        def _(constraint: cp_model.BoundedLinearExpression):
            return Add(self.Add(constraint))

        @Add.register
        def _(constraint: partialmethod):
            return Add(constraint.__get__(self)())

        return frozenset((Add(constraint) for constraint in constraints))

    def AddMultiplicationEquality(self, target, variables):
        """Adds `target == variables[0] * .. * variables[n]`.

Each parameter is interpreted as a BoundedLinearExpression, and a layer of indirection is applied such that each Constraint in the returned tuple can accept an enforcement literal."""

        superclass = super()

        def Multiply(end, stack):
            intermediate_variable, variable_constraint = self.NewIntermediateIntVar(stack.pop(), f'{repr(end)} == {"*".join((repr(variable) for variable in stack))}: last variable')

            partial_target = self.NewIntVar(f'{repr(end)} == {"*".join((repr(variable) for variable in stack))}: partial target')
            recursive_constraints = self.AddMultiplicationEquality(partial_target, stack) if len(stack) > 1 else (self.Add(partial_target == stack.pop()),)

            intermediate_target, target_constraint = self.NewIntermediateIntVar(end, f'{repr(end)} == {"*".join((repr(variable) for variable in stack))}: target')

            superclass.AddMultiplicationEquality(intermediate_target, (partial_target, intermediate_variable))

            return (variable_constraint, *recursive_constraints, target_constraint)

        # Avoid mutating parameter directly
        return Multiply(target, variables.copy() if isinstance(variables, list) else list(variables))

    @cache
    def BoolExpression(self, bounded_linear_exp):
        """Add a fully-reified implication using an intermediate Boolean variable."""

        intermediate = self.NewBoolVar(str(bounded_linear_exp))
        linear_exp = bounded_linear_exp.Expression()
        domain = cp_model.Domain(*bounded_linear_exp.Bounds())
        self.AddLinearExpressionInDomain(linear_exp, domain).OnlyEnforceIf(intermediate)
        self.AddLinearExpressionInDomain(linear_exp, domain.Complement()).OnlyEnforceIf(intermediate.Not())
        return intermediate

    def NewIntermediateIntVar(self, linear_exp, name, *, lb = cp_model.INT32_MIN, ub = cp_model.INT32_MAX):
        """Creates an integer variable equivalent to the given expression and returns a tuple consisting of the variable and constraint for use with enforcement literals."""

        intermediate = super().NewIntVar(lb, ub, name)
        return (intermediate, self.Add(intermediate == linear_exp))

    def NewIntVar(self, name, *, lb = cp_model.INT32_MIN, ub = cp_model.INT32_MAX):
        return super().NewIntVar(lb, ub, name)
