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
import core.utils as utils
from core.inequation import *
from core.model import *

class ModelerSMT(object):
        
    def __init__ (self, pimc):
        self.pimc = pimc
        self.boolVars = set()
        # Associates to each var its lb and ub
        # {0: {lb:0.5, ub:1}, 1: {lb:0.3, ub:0.6}}
        self.contVars = {}
        self.semiContVars = {}

    def addBooleanVariable(self, variable):
        assert(not(variable in self.boolVars))
        assert(not(variable in self.semiContVars))
        assert(not(variable in self.contVars))

        self.boolVars.add(variable)
    
    def addContinuousVariable(self, variable, lb, ub):
        assert(not(variable in self.boolVars))
        assert(not(variable in self.semiContVars))
        assert(not(variable in self.contVars))

        self.contVars[variable] = {'lb':lb, 'ub':ub}
    
    def addSemiContinuousVariable(self, variable, lb, ub):
        assert(not(variable in self.boolVars))
        assert(not(variable in self.semiContVars))
        assert(not(variable in self.contVars))

        self.semiContVars[variable] = {'lb':lb, 'ub':ub}
    
    def getReachabilityVariable(self, state):
        return 'r' + str(state)

    def getParameterVariable(self, parameter):
        return 'p_' + parameter

    def getTransitionVariable(self, stateFrom, stateTo):
        return 't_' + stateFrom + '_' + stateTo

    def declareVariables(self):
        parameters = self.pimc.getParameters()

        # Parameter variables
        self.param2variable = {}
        for p in parameters:
            var = self.getParameterVariable(p)
            self.param2variable[p] = var
            self.addContinuousVariable(var, 0., 1.)

        # Reachability variables
        for s in self.pimc.getStates():
            var = self.getReachabilityVariable(s)
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
        result = "+"
        first = True
        for predecessor in predecessors[state]:
            if predecessor != state:
                result += " " + self.getTransitionVariable(predecessor, state)
        return result

    def getSumSuccessors(self, state, successors):
        result = "+"
        for successor in successors[state]:
            result += " " + self.getTransitionVariable(state, successor)
        return result

    def declareConstraints(self):
        predecessors = self.pimc.getAllStatesPredecessors()
        successors = self.pimc.getAllStatesSuccessors()
        initialState = self.pimc.getInitialState()
        parameters = self.pimc.getParameters()

        self.constraints = []
        self.constraints.append("(assert (= %s true))\n" % (self.getReachabilityVariable(initialState)))

        for s in sorted(self.pimc.getStates()):
            sumPredecessors = self.getSumPredecessors(s, predecessors)
            sumSuccessors = self.getSumSuccessors(s, successors)
            if s != initialState:
                self.constraints.append("(assert (= (= %s false) (= (%s) 0)))\n" % 
                    (self.getReachabilityVariable(s), sumPredecessors))
            self.constraints.append("(assert (= (= %s false) (= (%s) 0)))\n" % 
                (self.getReachabilityVariable(s), sumSuccessors))
            self.constraints.append("(assert (= (= %s true) (= (%s) 1)))\n" % 
                (self.getReachabilityVariable(s), sumSuccessors))
            for ss in successors[s]:
                inter = self.pimc.getTransition(s, ss)
                lb = self.bound2smt(inter['lb'])
                ub = self.bound2smt(inter['ub'])

                if lb == ub:
                    self.constraints.append("(assert (=> (= %s true) (= %s %s)))\n" % 
                        (self.getReachabilityVariable(s), lb, self.getTransitionVariable(s, ss)))
                else:
                    self.constraints.append("(assert (=> (= %s true) (<= %s %s)))\n" % 
                        (self.getReachabilityVariable(s), lb, self.getTransitionVariable(s, ss)))
                    self.constraints.append("(assert (=> (= %s true) (>= %s %s)))\n" % 
                        (self.getReachabilityVariable(s), ub, self.getTransitionVariable(s, ss)))


    def printModel(self, fileName):
        file = open(fileName, 'w')
        file.write('(set-logic QF_LRA)\n')

        variables = []
        for var in self.contVars:
            variables.append(var)
            file.write('(declare-fun %s () Real)\n' % var)
            lb = float(self.contVars[var]['lb'])
            ub = float(self.contVars[var]['ub'])
            file.write('(assert (and (>= %s %f) (<= %s %f)))\n' % (var, lb, var, ub))

        for var in self.boolVars:
            variables.append(var)
            file.write('(declare-fun %s () Bool)\n' % (var))

        for var in self.semiContVars:
            variables.append(var)
            file.write('(declare-fun %s () Real)\n' % var)
            file.write('(assert (and (>= %s 0) (<= %s 1)))\n' % (var, var))

        for constraint in self.constraints:
            file.write('%s' % (constraint))

        file.write('(check-sat)\n')
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
        model = ModelerSMT(pimc)
        model.declareVariables()
        model.declareConstraints()
        model.printModel(fileName)
        return model
        