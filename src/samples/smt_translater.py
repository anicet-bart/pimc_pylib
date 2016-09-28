# -*- coding: utf-8 -*-
# PIMC_PYLIB: the Python Library for Parametric Interval Markov Chains Verification
# Copyright (C) 2016 Ecole des Mines de Nantes
# Author: Anicet BART
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from inequation import *
from model import *
from vmcai16_modeler import *
import traceback
import sys

class SmtTranslater(object):
        
    OPERATOR_PYTHON_TO_SMT = {'<=':'<=', '<':'<', '>=':'>=', '>':'>', '==':'='}

    def __init__ (self, pimc):
        self.indentation = 0
        self.pimc = pimc
        self.boolVars = set()
        # Associates to each var its lb and ub
        # {0: {lb:0.5, ub:1}, 1: {lb:0.3, ub:0.6}}
        self.contVars = {}
        self.semiContVars = {}
        self.constraints = []
        self.variables = {}

    def addBooleanVariable(self, variable):
        var = self.getVariable(variable)
        assert(not(var in self.contVars))
        assert(not(var in self.boolVars))

        self.boolVars.add(var)
    
    def addContinuousVariable(self, variable, lb, ub):
        var = self.getVariable(variable)
        assert(not(var in self.contVars))
        assert(not(var in self.boolVars))

        self.contVars[var] = {'lb':lb, 'ub':ub}
       
    def getVariable(self, variable):
        if not(variable in self.variables):
            name = variable
            if (isinstance(name, Variable)):
                name = name.getName()
            self.variables[variable] = 'v_' + name.replace("(","_").replace(")","_")
        return self.variables[variable]

    def getIndentation(self):
        return "\n" + (" " * self.indentation)

    def addUnaryBoolean(self, constraint):
        self.constraints.append(self.getIndentation() + '(= ' + self.getVariable(constraint) + ' true)')

    def addConjunction(self, constraint):
        if len(constraint.getConstraints()) > 0:
            self.constraints.append(self.getIndentation() + "(and ")
            self.indentation += 1
            for cstr in constraint.getConstraints():
                self.addConstraint(cstr)
            self.indentation -= 1
            self.constraints.append(")");

    def addDisjunction(self, constraint):
        self.constraints.append(self.getIndentation() + "(or ")
        self.indentation += 1
        for cstr in constraint.getConstraints():
            self.addConstraint(cstr)
        self.indentation -= 1
        self.constraints.append(")");

    def addEquivalence(self, constraint):
        self.constraints.append(self.getIndentation() + "(= ")
        self.indentation += 1
        self.addConstraint(constraint.getLHS())
        self.addConstraint(constraint.getRHS())
        self.indentation -= 1
        self.constraints.append(")")

    def addInequation(self, constraint):
        nbConstantsLHS = len(constraint.getConstantLHS())
        nbConstantsRHS = len(constraint.getConstantRHS())        
        
        nbVariablesLHS = 0
        nbVariablesRHS = 0
        sumLHS = ""
        sumRHS = ""
        for c in constraint.getParameters():
            coef = constraint.getCoefficientLHS(c)
            if coef != 0:
                if coef != 1:
                    sumLHS += "(* " + str(coef) + " " + self.getVariable(c) + ") "
                else:
                    sumLHS += self.getVariable(c) + " "
                nbVariablesLHS += 1
            
            coef = constraint.getCoefficientRHS(c)
            if coef != 0:
                if coef != 1:
                    sumRHS += "(* " + str(coef) + " " + self.getVariable(c) + ") "
                else:
                    sumRHS += self.getVariable(c) + " "
                nbVariablesRHS += 1

	constantsLHS = [utils.string2smtNumber(x) for x in constraint.getConstantLHS()]
	constantsRHS = [utils.string2smtNumber(x) for x in constraint.getConstantRHS()]
        sumConstantsLHS = "0" if (nbConstantsLHS == 0) else " ".join(constantsLHS)
        sumConstantsRHS = "0" if (nbConstantsRHS == 0) else " ".join(constantsRHS)
        if nbConstantsLHS + nbVariablesLHS > 1:
            sumLHS = "(+ " + sumLHS + " " + sumConstantsLHS + ")"
        elif nbVariablesLHS == 0:
            sumLHS = sumConstantsLHS

        if nbConstantsRHS + nbVariablesRHS > 1:
            sumRHS = "(+ " + sumRHS + " " + sumConstantsRHS + ")"
        elif nbVariablesRHS == 0:
            sumRHS = sumConstantsRHS
        result = "(" + self.OPERATOR_PYTHON_TO_SMT[constraint.getOperator()] + " " + sumLHS + " " + sumRHS + ")"
        self.constraints.append(self.getIndentation() + result)

    def addConstraint(self, constraint):
        if isinstance(constraint, Inequation):
            return self.addInequation(constraint)
        elif isinstance(constraint, Disjunction):
            return self.addDisjunction(constraint)
        elif isinstance(constraint, Conjunction):
            return self.addConjunction(constraint)
        elif isinstance(constraint, BooleanVariable):
            return self.addUnaryBoolean(constraint)
        elif isinstance(constraint, Equivalence):
            return self.addEquivalence(constraint)
        else:
            print ("[Error] Unknown instance in CplexModeler.addConstraint")
            traceback.print_exc(file=sys.stdout)
            exit(1)

    def printModel(self, fileName):
        file = open(fileName, 'w')
        file.write('(set-logic QF_LRA)\n')

        variables = []
        for var in self.contVars:
            variables.append(var)
            file.write('(declare-fun %s () Real)\n' % var)
            lb = self.contVars[var]['lb']
            ub = self.contVars[var]['ub']
            file.write('(assert (and (>= %s %s) (<= %s %s)))\n' % (var, lb, var, ub))

        for var in self.boolVars:
            variables.append(var)
            file.write('(declare-fun %s () Bool)\n' % (var))

        for constraint in self.constraints:
            file.write('%s' % (constraint))

        file.write('\n\n(check-sat)\n')
        file.write('(get-value (%s))\n' % (" ".join(variables)))
        file.write('(get-info :all-statistics)\n')

    def getInfos(self):
        results = {}
        results['#variables'] = len(self.contVars) + len(self.boolVars)
        results['#booleanVars'] = len(self.boolVars)
        results['#continuousVars'] = len(self.contVars)
        results['#semiContinuousVars'] = 0
        results['#constraints'] = self.nbConstraints
        return results

    @staticmethod
    def consistencyVMCAI16 (pimc, fileName):
        modeler = ModelerVMCAI16()
        model = modeler.consistency(pimc)
        smt = SmtTranslater(pimc)
        for var in model['contVars']:
            smt.addContinuousVariable(var, 0, 1)
        for var in model['boolVars']:
            smt.addBooleanVariable(var)
        smt.constraints.append("(assert ")
        smt.addConstraint(model['constraints'])
        smt.constraints.append(")")
        smt.nbConstraints = model['constraints'].size()
        smt.printModel(fileName)
        return smt
