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

import sys
from fractions import Fraction
import core.utils as utils
from core.inequation import *
from core.model import *

class ReachabilitySMT(object):
        
    # Only support one label as given property
    def __init__ (self, pimc, property, reachability=True, quantitative=True):
        self.pimc = pimc
        self.property = property
        self.reachability = reachability
        self.quantitative = quantitative
        self.boolVars = set()
        # Associates to each var its lb and ub
        # {0: {lb:0.5, ub:1}, 1: {lb:0.3, ub:0.6}}
        self.intVars = {}
        self.contVars = {}
        self.semiContVars = {}

    def isAbsorbingState(self, state):
        return 

    def addBooleanVariable(self, variable):
        assert (not(variable in self.boolVars)),     "%s in %s" % (variable, self.boolVars)
        assert (not(variable in self.semiContVars)), "%s in %s" % (variable, self.semiContVars)
        assert (not(variable in self.intVars)),      "%s in %s" % (variable, self.intVars)
        assert (not(variable in self.contVars)),     "%s in %s" % (variable, self.contVars)

        self.boolVars.add(variable)
    
    def addIntegerVariable(self, variable, lb, ub):
        assert (not(variable in self.boolVars)),     "%s in %s" % (variable, self.boolVars)
        assert (not(variable in self.semiContVars)), "%s in %s" % (variable, self.semiContVars)
        assert (not(variable in self.intVars)),      "%s in %s" % (variable, self.intVars)
        assert (not(variable in self.contVars)),     "%s in %s" % (variable, self.contVars)

        self.intVars[variable] = {'lb':lb, 'ub':ub}

    def addContinuousVariable(self, variable, lb, ub):
        assert (not(variable in self.boolVars)),     "%s in %s" % (variable, self.boolVars)
        assert (not(variable in self.semiContVars)), "%s in %s" % (variable, self.semiContVars)
        assert (not(variable in self.intVars)),      "%s in %s" % (variable, self.intVars)
        assert (not(variable in self.contVars)),     "%s in %s" % (variable, self.contVars)

        self.contVars[variable] = {'lb':lb, 'ub':ub}
    
    def addSemiContinuousVariable(self, variable, lb, ub):
        assert (not(variable in self.boolVars)),     "%s in %s" % (variable, self.boolVars)
        assert (not(variable in self.semiContVars)), "%s in %s" % (variable, self.semiContVars)
        assert (not(variable in self.intVars)),      "%s in %s" % (variable, self.intVars)
        assert (not(variable in self.contVars)),     "%s in %s" % (variable, self.contVars)

        self.semiContVars[variable] = {'lb':lb, 'ub':ub}
    
    def getVariableStateQualitativeReachability(self, state):
        """ Variable indicating if the given state is reachable from the initial state. """
        return 'ri_' + str(state)

    def getVariableStateQuantitativeReachability(self, state):
        """ Variable indicating the probability to reach the target states from the given state. """
        return 'rq_' + str(state)

    def getVariableStateCanReachTarget(self, state):
        """ Variable indicating if the given state can reach at least one target state. """
        return 'rt_' + str(state)

    def getVariablePathLengthFromInitialState(self, state):
    	""" Variable indicatng the length of an existing path from the initial state to the given state """
    	return 'li_' + str(state)
        	
    def getVariablePathLengthToTargetState(self, state):
    	""" Variable indicatng the length of an existing path from the given state to a target state """
        return 'lt_' + str(state)

    def getParameterVariable(self, parameter):
        """ Variable indicating the value for the given parameter. """
        return 'p_' + parameter

    def getTransitionVariable(self, stateFrom, stateTo):
        """ Variable indicating the probability given to the transition from stateFrom to stateTo. """
        return 't_' + stateFrom + '_' + stateTo


    def declareVariables(self):
        parameters = self.pimc.getParameters()

        # Parameter variables
        self.param2variable = {}
        for p in parameters:
            var = self.getParameterVariable(p)
            self.param2variable[p] = var
            self.addContinuousVariable(var, 0., 1.)

        # Existential consistency
        for s in self.pimc.getStates():        
            var = self.getVariableStateQualitativeReachability(s)
            self.addBooleanVariable(var)

        # Transition variables
        for s in self.pimc.getStates():
            for ss in self.pimc.getSuccessors(s):
                inter = self.pimc.getTransition(s, ss)
                assert(inter != None)
                lb = 0 if (inter['lb'] in parameters) else inter['lb']
                ub = 1 if (inter['ub'] in parameters) else inter['ub']
                var = self.getTransitionVariable(s, ss)
                self.addSemiContinuousVariable(var, lb, ub)

        if self.reachability:
            for s in self.pimc.getStates():
                # Qualitative reachability variables
                var = self.getVariablePathLengthFromInitialState(s)
                #self.addIntegerVariable(var, 0, self.pimc.nbStates())
                self.addContinuousVariable(var, 0, self.pimc.nbStates())

                # Quantitative reachability variables
                if self.quantitative:
                    var = self.getVariablePathLengthToTargetState(s)
                    #self.addIntegerVariable(var, 0, self.pimc.nbStates())
                    self.addContinuousVariable(var, 0, self.pimc.nbStates())

                    var = self.getVariableStateCanReachTarget(s)
                    self.addBooleanVariable(var)

                    var = self.getVariableStateQuantitativeReachability(s)
                    self.addContinuousVariable(var, 0., 1.)


    def bound2smt(self, bound):
        result = bound

        # Search and replace parameters by their coresponding variables
        if isinstance(bound, basestring):
            result = utils.multireplace(bound, self.param2variable)

        # If no parameters format number as smt number
        if result == bound:
            result = utils.string2smtNumber(bound)

        return result

    def getSumPredecessors(self, state, predecessors):
        result = ""
        nb = 0
        for predecessor in predecessors[state]:
            if predecessor != state:
                result += " " + self.getTransitionVariable(predecessor, state)
                nb += 1

        if nb == 0:
            result = "0"
        elif nb > 1:
            result = "(+%s)" % result
        return result

    def getSumSuccessors(self, state, successors):
        result = ""
        nb = 0
        for successor in successors[state]:
            result += " " + self.getTransitionVariable(state, successor)
            nb += 1

        if nb == 0:
            result = "0"
        elif nb > 1:
            result = "(+%s)" % result
        return result

    def isTargetState(self, state):
    	return self.property in self.pimc.getLabel(state)


    def declareConstraintsExistentialConsistency(self, state):
        sumPredecessors = self.getSumPredecessors(state, self.predecessors)
        sumSuccessors = self.getSumSuccessors(state, self.successors)

        if state == self.pimc.getInitialState():
            # Constraint (1) from Mec
            self.constraints.append("(assert (= %s true))\n" % 
                (self.getVariableStateQualitativeReachability(state)))
        else:
            # Constraint (2) from Mec
            self.constraints.append("(assert (= (= %s false) (= %s 0)))\n" % 
                (self.getVariableStateQualitativeReachability(state), sumPredecessors))

        # Constraint (3) from Mec
        self.constraints.append("(assert (= (= %s false) (= %s 0)))\n" % 
            (self.getVariableStateQualitativeReachability(state), sumSuccessors))

        # Constraint (4) from Mec
        self.constraints.append("(assert (= (= %s true) (= %s 1)))\n" % 
            (self.getVariableStateQualitativeReachability(state), sumSuccessors))

        # Constraints (5) from Mec
        for s in self.successors[state]:
            inter = self.pimc.getTransition(state, s)
            lb = self.bound2smt(inter['lb'])
            ub = self.bound2smt(inter['ub'])
            
            # P(state, s) is a singleton
            if lb == ub:
                self.constraints.append("(assert (=> (= %s true) (= %s %s)))\n" % 
                    (self.getVariableStateQualitativeReachability(state), lb, self.getTransitionVariable(state, s)))

            # P(state, s) is an interval
            else:
                self.constraints.append("(assert (=> (= %s true) (<= %s %s)))\n" % 
                    (self.getVariableStateQualitativeReachability(state), lb, self.getTransitionVariable(state, s)))
                self.constraints.append("(assert (=> (= %s true) (>= %s %s)))\n" % 
                    (self.getVariableStateQualitativeReachability(state), ub, self.getTransitionVariable(state, s)))


    def declareConstraintsExistentialReachability(self, state):
        if state == self.pimc.getInitialState():
            # Constraint (1) from Mer
            self.constraints.append("(assert (= %s 1))\n" % 
                (self.getVariablePathLengthFromInitialState(state)))
        else:
            # Constraint (2) from Mer
            self.constraints.append("(assert (not (= %s 1)))\n" % 
                (self.getVariablePathLengthFromInitialState(state)))

            # Constraint (2') from Mer
            self.constraints.append("(assert (=> (< %s 1) (= %s 0)))\n" % 
                (self.getVariablePathLengthFromInitialState(state), self.getVariablePathLengthFromInitialState(state)))

            # Prepare disjunction and conjunction for constraints (3) and (4)
            disjunction = []
            conjunction = []
            for s in self.predecessors[state]:
                if s != state:
                    disjunction.append("(and (= %s (+ %s 1)) (> %s 0))" % 
                        (self.getVariablePathLengthFromInitialState(state), self.getVariablePathLengthFromInitialState(s), self.getTransitionVariable(s, state)))
                    conjunction.append("(or (= %s 0) (= %s 0))" % 
                        (self.getVariablePathLengthFromInitialState(s), self.getTransitionVariable(s, state)))
            if len(conjunction) == 0:
                resultConjunction = "true"
                resultDisjunction = "false"
            elif len(conjunction) == 1:
                resultConjunction = conjunction[0]
                resultDisjunction = disjunction[0]
            else:
                resultConjunction = "(and %s)" % (" ".join(conjunction))
                resultDisjunction = "(or %s)" % (" ".join(disjunction))

        	# Constraint (3) from Mer
            self.constraints.append("(assert (=> (> %s 1) %s))\n" % 
                (self.getVariablePathLengthFromInitialState(state), resultDisjunction))

            # Constraint (4) from Mer
            self.constraints.append("(assert (= (= %s 0) %s))\n" % 
                (self.getVariablePathLengthFromInitialState(state), resultConjunction))

        # Constraint (5) from Mer
        self.constraints.append("(assert (= (= %s false) (= %s 0)))\n" % 
            (self.getVariableStateQualitativeReachability(state), self.getVariablePathLengthFromInitialState(state)))
	

    def declareConstraintsExistentialReachabilityForInitialState(self):
        targetStates = set()
        for s in self.pimc.getStates():
            if self.isTargetState(s):
                targetStates.add(self.getVariableStateQualitativeReachability(s))
        assert(len(targetStates) > 0)
        
        result = " ".join(targetStates)
        if len(targetStates) > 1:
            result = "(or %s)" % result
        self.constraints.append("(assert (= %s true))\n" % (result))


    def declareConstraintsExistentialReachabilityPrime(self, state):
        if self.isTargetState(state):
            # Constraint (1) from MerPrime
            self.constraints.append("(assert (= %s 1))\n" % 
                (self.getVariablePathLengthToTargetState(state)))
        else:
            # Constraint (2) from MerPrime
            self.constraints.append("(assert (not (= %s 1)))\n" % 
                (self.getVariablePathLengthToTargetState(state)))

            # Constraint (2') from Mer
            self.constraints.append("(assert (=> (< %s 1) (= %s 0)))\n" % 
                (self.getVariablePathLengthToTargetState(state), self.getVariablePathLengthToTargetState(state)))

            # Prepare disjunction and conjunction for constraints (3) and (4)
            disjunction = []
            conjunction = []
            for s in self.successors[state]:
                if s != state:
                    disjunction.append("(and (= %s (+ %s 1)) (> %s 0))" % 
                        (self.getVariablePathLengthToTargetState(state), self.getVariablePathLengthToTargetState(s), self.getTransitionVariable(state, s)))
                    conjunction.append("(or (= %s 0) (= %s 0))" % 
                        (self.getVariablePathLengthToTargetState(s), self.getTransitionVariable(state, s)))
            if len(conjunction) == 0:
                resultConjunction = "true"
                resultDisjunction = "false"
            elif len(conjunction) == 1:
                resultConjunction = conjunction[0]
                resultDisjunction = disjunction[0]
            else:
                resultConjunction = "(and %s)" % (" ".join(conjunction))
                resultDisjunction = "(or %s)" % (" ".join(disjunction))

        	# Constraint (3) from MerPrime
            self.constraints.append("(assert (=> (> %s 1) %s))\n" % 
                (self.getVariablePathLengthToTargetState(state), resultDisjunction))

            # Constraint (4) from MerPrime
            self.constraints.append("(assert (= (= %s 0) %s))\n" % 
                (self.getVariablePathLengthToTargetState(state), resultConjunction))

        # Constraint (5) from MerPrime
        self.constraints.append("(assert (= (= %s true) (and (= %s true) (not (= %s 0)))))\n" % 
            (self.getVariableStateCanReachTarget(state), 
                self.getVariableStateQualitativeReachability(state), self.getVariablePathLengthToTargetState(state)))

        # Constraint forcing to reach a target state from the initial state
        if state == self.pimc.getInitialState():
		self.constraints.append("(assert (> %s 0))\n" % 
			(self.getVariablePathLengthToTargetState(state)))



    def declareConstraintsExistentialReachabilityExtended(self, state):
        # Constraint (1) from MerExtended
        self.constraints.append("(assert (=> (= %s false) (= %s 0)))\n" % 
            (self.getVariableStateCanReachTarget(state), self.getVariableStateQuantitativeReachability(state)))

        # Constraint (2) from MerExtended
        if self.isTargetState(state):
            self.constraints.append("(assert (=> (= %s true) (= %s 1)))\n" % 
                (self.getVariableStateCanReachTarget(state), self.getVariableStateQuantitativeReachability(state)))

        # Constraint (3) from MerExtended
        else:
            addition = []
            for s in self.successors[state]:
                addition.append("(* %s %s)" % (self.getVariableStateQuantitativeReachability(s), self.getTransitionVariable(state, s)))
            result = addition[0] if (len(addition) == 1) else "(+ %s)" % (" ".join(addition))
            self.constraints.append("(assert (=> (= %s true) (= %s %s)))\n" % 
                (self.getVariableStateCanReachTarget(state), self.getVariableStateQuantitativeReachability(state), result))
	


    def declareConstraints(self):
        self.predecessors = self.pimc.getAllStatesPredecessors()
        self.successors = self.pimc.getAllStatesSuccessors()
        self.constraints = []

        print("Initial state: %s" % self.pimc.getInitialState())

        for s in sorted(self.pimc.getStates(), key=int):
            self.declareConstraintsExistentialConsistency(s)
            if self.reachability:
                self.declareConstraintsExistentialReachability(s)
                self.declareConstraintsExistentialReachabilityForInitialState()
                if self.quantitative:
                    self.declareConstraintsExistentialReachabilityPrime(s)
                    self.declareConstraintsExistentialReachabilityExtended(s)

    def printModel(self, fileName):
        file = open(fileName, 'w')
        #file.write('(set-logic QF_NIRA)\n')
        file.write('(set-option :produce-models true)\n')

        variables = []
        for var in sorted(self.contVars):
            variables.append(var)
            file.write('(declare-fun %s () Real)\n' % var)
            lb = float(self.contVars[var]['lb'])
            ub = float(self.contVars[var]['ub'])
            file.write('(assert (and (>= %s %f) (<= %s %f)))\n' % (var, lb, var, ub))

        for var in sorted(self.boolVars):
            variables.append(var)
            file.write('(declare-fun %s () Bool)\n' % (var))

        for var in sorted(self.semiContVars):
            variables.append(var)
            file.write('(declare-fun %s () Real)\n' % var)
            file.write('(assert (and (>= %s 0) (<= %s 1)))\n' % (var, var))

        for var in sorted(self.intVars):
            variables.append(var)
            file.write('(declare-const %s Int)\n' % var)
            lb = float(self.intVars[var]['lb'])
            ub = float(self.intVars[var]['ub'])
            file.write('(assert (and (>= %s %d) (<= %s %d)))\n' % (var, lb, var, ub))

        for constraint in self.constraints:
            file.write('%s' % (constraint))

        file.write('(check-sat)\n')
        #file.write('(check-sat-using (then simplify solve-eqs smt))\n')
        file.write('(get-value (%s))\n' % (" ".join(variables)))
        file.write('(get-info :all-statistics)\n')

    def getInfos(self):
        results = {}
        results['#variables'] = len(self.contVars) + len(self.semiContVars) + len(self.boolVars)
        results['#booleanVars'] = len(self.boolVars)
        results['#continuousVars'] = len(self.contVars)
        results['#continuousVars'] += len(self.semiContVars)
        results['#semiContinuousVars'] = 0

        # We count a constraint "y = True <-> x_1 + x_2 <= 1" as 3 constraints (ie. one equivalence + 2 linear constraints)
        results['#constraints'] = (len(self.constraints) - 1) * 3 + 1
        # Domains for continuous variables are encoded with one constraint
        results['#constraints'] += results['#continuousVars']
        return results
 
    @staticmethod
    def consistency (pimc, fileName):
        model = ReachabilitySMT(pimc, property='target', reachability=False, quantitative=False)
        model.declareVariables()
        model.declareConstraints()
        model.printModel(fileName)
        return model

    @staticmethod
    def qualitativeReachability (pimc, fileName):
        model = ReachabilitySMT(pimc, property='target', reachability=True, quantitative=False)
        model.declareVariables()
        model.declareConstraints()
        model.printModel(fileName)
        return model

    @staticmethod
    def quantitativeReachability (pimc, fileName):
        model = ReachabilitySMT(pimc, property='target', reachability=True, quantitative=True)
        model.declareVariables()
        model.declareConstraints()
        model.printModel(fileName)
        return model
