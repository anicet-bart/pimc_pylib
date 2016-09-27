# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 13:08:23 2016

@author: Anicet
"""

import cplex
from inequation import *
from model import *

class CplexModeler(object):
    
    OPERATOR_PYTHON_TO_CPLEX = {'<=':'L', '<':'L', '>=':'G', '>':'G', '==':'E'}
    OPERATOR_PYTHON_IS_STRICT = {'<=':False, '<':True, '>=':False, '>':True, '==':False}
    
    def __init__ (self):
        self.cplex = cplex.Cplex()
        self.nbIndicatorVariables = 0
        self.indicatorVariables = dict()

    def addBooleanVariable(self, variable):
        self.cplex.variables.add(names=[variable.getName()], types=[self.cplex.variables.type.integer], lb=[0.], ub=[1.])
        return variable.getName()
    
    def addVariables(self, variables):
        indices = self.cplex.variables.add(names = variables)
        for variable in variables:
            self.cplex.variables.set_upper_bounds(variable, 1.0)

    def addIndicatorVariable(self, constraint):
        #assert(not constraint.name in self.indicatorVariables)
        variable = "iv" + str(self.nbIndicatorVariables)
        self.cplex.variables.add(names = [variable])
        self.nbIndicatorVariables += 1
        #if constraint.name != "":
        #    self.indicatorVariables[constraint.name] = variable
        return variable

    def getIndicatorVariable(self, constraint):
        #if constraint.name in self.indicatorVariables:
        #    return self.indicatorVariables[constraint.name]
        #else:            
        return self.addIndicatorVariable(constraint)

    def addConjunction(self, constraint):
        iVariables = []
        for cstr in constraint.getConstraints():
            iVariables.append(self.addConstraint(cstr))
        
        iVariable = self.getIndicatorVariable(constraint)
        indices = self.cplex.indicator_constraints.add(
            indvar=iVariable,
            complemented=0,
            lin_expr = cplex.SparsePair(ind = iVariables, val = [1.0] * len(iVariables)),
            sense = "E",
            rhs = 0. + len(iVariables),
            name = constraint.getName())
        return iVariable

    def addDisjunction(self, constraint):
        iVariables = []
        for cstr in constraint.getConstraints():
            iVariables.append(self.addConstraint(cstr))
        
        iVariable = self.getIndicatorVariable(constraint)
        indices = self.cplex.indicator_constraints.add(
            indvar=iVariable,
            complemented=0,
            lin_expr = cplex.SparsePair(ind = iVariables, val = [1.0] * len(iVariables)),
            sense = "G",
            rhs = 1.0,
            name = constraint.getName())
        return iVariable

    def addEquivalence(self, constraint):
        print(constraint)
        iVariableLeft  = self.addConstraint(constraint.getLHS())
        iVariableRight = self.addConstraint(constraint.getRHS())
        iVariable      = self.getIndicatorVariable(constraint)
        
        indices = self.cplex.indicator_constraints.add(
            indvar=iVariable,
            complemented=0,
            lin_expr = cplex.SparsePair(ind = [iVariableLeft, iVariableRight], val = [1.0, -1.0]),
            sense = "E",
            rhs = 0.0,
            name = constraint.getName())
        return iVariable


    def addInequation(self, constraint):
        variables = []
        coefs = []
        for c in constraint.getParameters():
            coef = constraint.getCoefficientLHS(c)
            if coef != 0:
                variables.append(c)
                coefs.append(coef)
        
        #if constraint.getOperator() == "<":
        #print(CplexModeler.OPERATOR_PYTHON_TO_CPLEX[constraint.getOperator()])
        
        iVariable = self.getIndicatorVariable(constraint)
        indices = self.cplex.indicator_constraints.add(
            indvar=iVariable,
            complemented=0,
            lin_expr = cplex.SparsePair(ind = variables, val = coefs),
            sense = CplexModeler.OPERATOR_PYTHON_TO_CPLEX[constraint.getOperator()],
            rhs = 0. + constraint.getConstantRHS(),
            name = "ind" + iVariable)
        
        if CplexModeler.OPERATOR_PYTHON_IS_STRICT[constraint.getOperator()]:     
            indices = self.cplex.indicator_constraints.add(
                indvar=iVariable,
                complemented=0,
                lin_expr = cplex.SparsePair(ind = variables, val = coefs),
                sense = "NE",
                rhs = 0. + constraint.getConstantRHS(),
                name = "ind" + iVariable)
            
        return iVariable

    def addConstraint(self, constraint):
        if isinstance(constraint, Inequation):
            return self.addInequation(constraint)
        elif isinstance(constraint, Disjunction):
            return self.addDisjunction(constraint)
        elif isinstance(constraint, Conjunction):
            return self.addConjunction(constraint)
        elif isinstance(constraint, BooleanVariable):
            return self.addBooleanVariable(constraint)
        elif isinstance(constraint, Equivalence):
            return self.addEquivalence(constraint)
        else:
            print ("[Error] Unknown instance in CplexModeler.addConstraint")
            exit(1)

    def addTopConstraint(self, iVariable):
        indices = self.cplex.linear_constraints.add(
            lin_expr = [cplex.SparsePair(ind = [iVariable], val = [1.0])],
            senses = ["E"],
            rhs = [1.],
            names = ["top"])

    @staticmethod
    def modelVMCAI (constraint, variables):
        cplex = CplexModeler()
        cplex.addVariables(variables)
        topVariable = cplex.addConstraint(constraint)
        cplex.addTopConstraint(topVariable)
        return cplex.cplex
            