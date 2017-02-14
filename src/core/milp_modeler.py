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
from core.inequation import *
from core.model import *

class ModelerMILP(object):
    
    OPERATOR_PYTHON_TO_CPLEX = {'<=':'L', '<':'L', '>=':'G', '>':'G', '==':'E'}
    OPERATOR_PYTHON_IS_STRICT = {'<=':False, '<':True, '>=':False, '>':True, '==':False}
    
    def __init__ (self, pimc, useSemiContinuous=False):
        self.pimc = pimc
        self.boolVars = set()
        self.useSemiContinuous = useSemiContinuous
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
        for p in parameters:
            var = self.getParameterVariable(p)
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


    def getSumPredecessors(self, state, predecessors):
        result = ""
        first = True
        for predecessor in predecessors[state]:
            if predecessor != state:
                if first:
                    first = False
                else:
                    result += " + "
                result += self.getTransitionVariable(predecessor, state)
        return result

    def getSumSuccessors(self, state, successors):
        result = ""
        first = True
        for successor in successors[state]:
            if first:
                first = False
            else:
                result += " + "
            result += self.getTransitionVariable(state, successor)
        return result

    def declareConstraints(self):
        predecessors = self.pimc.getAllStatesPredecessors()
        successors = self.pimc.getAllStatesSuccessors()
        initialState = self.pimc.getInitialState()
        parameters = self.pimc.getParameters()

        self.constraints = []
        self.constraints.append("Constraint0: %s = 1\n" % (self.getReachabilityVariable(initialState)))

        for s in self.pimc.getStates():
            sumPredecessors = self.getSumPredecessors(s, predecessors)
            sumSuccessors = self.getSumSuccessors(s, successors)
            if s != initialState:
                self.constraints.append("Constraint2_%s: %s = 0 <-> %s = 0\n" % 
                    (s, self.getReachabilityVariable(s), sumPredecessors))
            self.constraints.append("Constraint3_%s: %s = 0 <-> %s = 0\n" % 
                (s, self.getReachabilityVariable(s), sumSuccessors))
            self.constraints.append("Constraint4_%s: %s = 1 <-> %s = 1\n" % 
                (s, self.getReachabilityVariable(s), sumSuccessors))
            for ss in successors[s]:
                inter = self.pimc.getTransition(s, ss)
                lbConstant = 0.
                ubConstant = 0.
                lbParameter = "" 
                ubParameter = ""
                if inter['lb'] in parameters:
                    lbParameter = self.getParameterVariable(inter['lb'])
                else:
                    lbConstant = "-" + inter['lb']

                if inter['ub'] in parameters:
                    ubParameter = self.getParameterVariable(inter['ub'])
                else:
                    ubConstant = "-" + inter['ub']

                if not(self.useSemiContinuous) or inter['lb'] in parameters:
                    self.constraints.append("Constraint5_%s_%s_lb: %s = 1 -> %s - %s <= %s\n" % 
                        (s, ss, self.getReachabilityVariable(s), 
                                lbParameter, self.getTransitionVariable(s, ss), lbConstant))
                if not(self.useSemiContinuous) or inter['ub'] in parameters:
                    self.constraints.append("Constraint5_%s_%s_ub: %s = 1 -> %s - %s >= %s\n" % 
                        (s, ss, self.getReachabilityVariable(s), 
                                ubParameter, self.getTransitionVariable(s, ss), ubConstant))


    def printModel(self, fileName):
        file = open(fileName, 'w')
        file.write('Minimize\n')
        file.write('Subject To\n')
        for constraint in self.constraints:
            file.write(' %s' % (constraint))
        
        file.write('Bounds\n')
        for var in self.contVars:
            file.write(' %s <= %s <= %s\n' % (float(self.contVars[var]['lb']), var, float(self.contVars[var]['ub'])))
        for var in self.boolVars:
            file.write(' 0 <= %s <= 1\n' % (var))

        if self.useSemiContinuous:
            for var in self.semiContVars:
                file.write(' %s <= %s <= %s\n' % (float(self.semiContVars[var]['lb']), var, float(self.semiContVars[var]['ub'])))
        else:
            for var in self.semiContVars:
                file.write(' 0. <= %s <= 1.\n' % (var))

        file.write('Binaries\n')
        nb = 0
        for var in self.boolVars:
            if nb == 25:
                file.write('\n')
                nb = 0
            else:
                nb += 1
            file.write(' %s' % (var))

        if self.useSemiContinuous:
            file.write('\nSemi-continuous\n')
            nb = 0
            for var in self.semiContVars:
                if nb == 50:
                    file.write('\n')
                    nb = 0
                else:
                    nb += 1
                file.write(' %s' % (var))
            file.write('\n')
        file.write('\nEnd\n')

    def getInfos(self):
        results = {}
        results['#variables'] = len(self.contVars) + len(self.semiContVars) + len(self.boolVars)
        # We count a constraint "y = True <-> x_1 + x_2 <= 1" as 3 constraints (ie. one equivalence + 2 linear constraints)
        results['#constraints'] = (len(self.constraints) - 1) * 3 + 1
        results['#booleanVars'] = len(self.boolVars)
        results['#continuousVars'] = len(self.contVars)
        if self.useSemiContinuous:
            results['#semiContinuousVars'] = len(self.semiContVars)
        else:
            results['#semiContinuousVars'] = 0
            results['#continuousVars'] += len(self.semiContVars)
        return results

    @staticmethod
    def consistency (pimc, useSemiContinuous, fileName):
        modeler = ModelerMILP(pimc, useSemiContinuous)
        modeler.declareVariables()
        modeler.declareConstraints()
        modeler.printModel(fileName)
        return modeler
        
