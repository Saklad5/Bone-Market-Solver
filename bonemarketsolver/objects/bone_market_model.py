__author__ = "Jeremy Saklad"

from functools import reduce

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

    def NewIntermediateBoolVar(self, name, linear_exp, domain):
        """Add a fully-reified implication using an intermediate Boolean variable."""

        intermediate = self.NewBoolVar(name)
        self.AddLinearExpressionInDomain(linear_exp, domain).OnlyEnforceIf(intermediate)
        self.AddLinearExpressionInDomain(linear_exp, domain.Complement()).OnlyEnforceIf(intermediate.Not())
        return intermediate

    def NewIntermediateIntVar(self, linear_exp, name, *, lb = cp_model.INT_MIN//8, ub = cp_model.INT_MAX//8):
        """Creates an integer variable equivalent to the given expression and returns a tuple consisting of the variable and constraint for use with enforcement literals."""

        intermediate = super().NewIntVar(lb, ub, name)
        return (intermediate, self.Add(intermediate == linear_exp))

    def NewIntVar(self, name, *, lb = cp_model.INT32_MIN, ub = cp_model.INT32_MAX):
        return super().NewIntVar(lb, ub, name)
