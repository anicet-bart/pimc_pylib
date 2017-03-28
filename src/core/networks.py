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

import fractions
from copy import copy

try:
    import core.utils as utils
except ImportError:
    import utils


class MC(object):
    def __init__(self):
        self.states = set()
        self.initialState = None
        self.labels = {}
        self.transitionFunction = {}
        self.predecessors = {}
        
    def setInitialState(self, state):
        self.initialState = state

    def getInitialState(self):
        return self.initialState

    def setStates(self, states):
        if (type(states) == set):
            self.states = states
        else:
            self.states = set(states)
     
    def getStates(self):
        return self.states
    
    def getStatesWithLabel(self, label):
        result = set()
        for s in self.getStates():
            if self.getLabel(s) == label:
                result.add(s)
        return result

    def removeStates(self, states):
        for s in states:
            self.removeState(s)

    def removeState(self, state):
        assert(state != self.initialState)
        self.states.remove(state)
        del self.labels[state]
        del self.transitionFunction[state]

    def nbStates(self):
        return len(self.states)
     
    def getSuccessors(self, state):
        if state in self.transitionFunction:
            return set(self.transitionFunction[state].keys())
        else:
            return set()

    def getPredecessors(self, state):
        if state in self.predecessors:
            return self.predecessors[state]
        else:
            return set()

    def setLabel(self, state, label):
        assert(state in self.labels)
        self.labels[state] = label

    def addLabels(self, state, labels):
        # [TODO] utiliser Set au lieu de String pour stocket les labels
        if not(state in self.labels):
            self.labels[state] = ""
        self.labels[state] += " ".join(labels)

    def setLabels(self, labels):
        utils.isType(labels, dict)       
        self.labels = labels
        
    def getLabel(self, state):
        assert(state in self.labels)
        return self.labels[state]

    def getLabels(self, state):
        assert(state in self.labels)
        if self.labels[state]:
            return self.labels[state].split(" ")       
        else:
            return []

    def getTransition(self, stateFrom, stateTo):
        if stateFrom in self.transitionFunction and stateTo in self.transitionFunction[stateFrom]:
            return self.transitionFunction[stateFrom][stateTo]
        return None     

    def removeTransition(self, stateFrom, stateTo):
        del self.transitionFunction[stateFrom][stateTo]
        self.predecessors[stateTo].remove(stateFrom)

    def setAbsorbingStates(self, states):
        for s in states:
            self.setAbsorbingState(s)

    def setAbsorbingState(self, state):
        for s in self.getSuccessors(state):
            self.removeTransition(state, s)
        self.setProbability(state, state, "1")

    def isAbsorbingState(self, state):
        if  (state in self.transitionFunction) and (state in self.transitionFunction[state]) and (len(self.transitionFunction[state]) == 1):
            # TODO: not efficient
            return state in self.transitionFunction[state].keys()
        return False

    def setProbability(self, nodeFrom, nodeTo, probability):
        if not (nodeFrom in self.states):
            raise Exception("Undeclared state '%s'." % (nodeFrom))
        if not (nodeTo in self.states):
            raise Exception("Undeclared state '%s'." % (nodeTo))
        
        # Add successor relation between nodeFrom and nodeTo
        if not(nodeFrom in self.transitionFunction):
            self.transitionFunction[nodeFrom] = {}
        self.transitionFunction[nodeFrom][nodeTo] = probability

        # Add predecessor relation between nodeTo and nodeFrom
        if not(nodeTo in self.predecessors):
            self.predecessors[nodeTo] = set()
        self.predecessors[nodeTo].add(nodeFrom)

        
    def setProbabilityFromString(self, nodeFrom, nodeTo, probability):
        self.setProbability(nodeFrom, nodeTo, fractions.Fraction(probability))
     
    def nbTransitions(self):
        result = 0
        for state in self.transitionFunction:
            result += len(self.transitionFunction[state])            
        return result
     

    def getAllStatesSuccessors(self):
        result = {state:set() for state in self.states}
        for state in self.states:
            for successor in self.transitionFunction[state]:
                result[state].add(successor)
        for state in self.states:
            result[state] = sorted(result[state])
        return result

    def getAllStatesPredecessors(self):
        result = {state:set() for state in self.states}
        for state in self.states:
            result[state] = sorted(self.getPredecessors(state))
        return result

    def getAllStatesChildren(self):
        children = self.getAllStatesSuccessors()
        predecessors = self.getAllStatesPredecessors()
        successors = self.getAllStatesSuccessors()
        stack = set(self.states)

        while stack:
            state = stack.pop()
            sizeBefore = len(children[state])
            for successor in successors[state]:
                children[state].update(children[successor])
            sizeAfter = len(children[state])
            if sizeBefore != sizeAfter:
                for predecessor in predecessors[state]:
                    stack.add(predecessor)
        return children

    def getAllReachableStates(self):
        result = self.getAllStatesChildren()
        for state in result:
            result[state].add(state)
        return result

    def getChildren(self, states):
        result = set()
        stack = set()
        stack.update(states)
        successors = self.getAllStatesSuccessors()

        while stack:
            state = stack.pop()
            for successor in successors[state]:
                if not(successor in result):
                    result.add(successor)
                    stack.add(successor)
        return result

    def getAncestors(self, states):
        result = set()
        stack = set()
        stack.update(states)
        predecessors = self.getAllStatesPredecessors()

        while stack:
            state = stack.pop()
            for predecessor in predecessors[state]:
                if not(predecessor in result):
                    result.add(predecessor)
                    stack.add(predecessor)
        return result

    def guessInitialState(self):
        reachableStates = self.getAllReachableStates()
        result = None
        nbReachable = -1

        for state in reachableStates:
            if len(reachableStates[state]) > nbReachable:
                result = state
                nbReachable = len(reachableStates[state])
        return result, nbReachable


class IMC(MC):
    def __init__(self):
        MC.__init__(self)
      
    def setProbabilityFromString(self, nodeFrom, nodeTo, probability):
        bounds = probability.split(';')
        lowerBound = fractions.Fraction("".join(bounds[0].split())) # removes spaces
        if len(bounds) > 1:
            upperBound = fractions.Fraction("".join(bounds[1].split())) # removes spaces
        else:
            upperBound = fractions.Fraction(lowerBound)
        self.setProbability(nodeFrom, nodeTo, {'lb': lowerBound, 'ub':upperBound})
      
      
     
     
class PIMC(IMC):
    def __init__(self, useFractions=False):
        IMC.__init__(self)
        self.parameters = set()
        self.useFractions = useFractions
        
    def low(self, fromState, toState):
        interval = self.getTransition(fromState, toState)
        if interval:
            return interval['lb']
        return None

    def up(self, fromState, toState):        
        interval = self.getTransition(fromState, toState)
        if interval:
            return interval['ub']
        return None
        
    def nbParameters(self):
        return len(self.parameters)

    def setParameters(self, parameters):
        if (type(parameters) == set):
            self.parameters = parameters
        else:
            self.parameters = set(parameters)
      
    def isParameter(self, value):
        return value in self.parameters
      
    def isParametric(self, value):
        for p in self.parameters:
            if p in value:
                return True
        return False

    def getParameters(self):
        return self.parameters
      
    def setProbabilityFromString(self, nodeFrom, nodeTo, probability):
        bounds = probability.split(';')
        
        # Lower bound
        lowerBound = bounds[0].strip()
        if not(self.isParametric(lowerBound)):
            if self.useFractions:
                lowerBound = "".join(lowerBound.split()) # removes spaces for fractions
                lowerBound = fractions.Fraction(lowerBound)
            
        # Upper bound
        if len(bounds) > 1:
            upperBound = bounds[1].strip()
            if not(self.isParametric(upperBound)):
                if self.useFractions:
                    upperBound = "".join(upperBound.split()) # removes spaces for fractions
                    upperBound = fractions.Fraction(upperBound)
        else:
            upperBound = copy(lowerBound)
        self.setProbability(nodeFrom, nodeTo, {'lb': lowerBound, 'ub':upperBound})
        
    def getTransitionAsString(self, nodeFrom, nodeTo):
        probability = self.getTransition(nodeFrom, nodeTo)
        if not(utils.isDict(probability)):
            return probability
        elif probability['lb'] == probability['ub']:
            return probability['lb']
        else:
            return "%s ; %s" % (probability['lb'], probability['ub'])

    def isVariable(self, bound):
        return bound in self.parameters

    def countParametersInIntervals(self):
        nbIntervals = 0
        nbParamsInBounds = 0
        parameters = self.getParameters()

        for s in self.getStates():
            for ss in self.getSuccessors(s):
                lb = self.low(s, ss)
                ub = self.up(s, ss)
                if lb in parameters:
                    nbParamsInBounds += 1
                if ub in parameters:
                    nbParamsInBounds += 1
                if ub != lb:
                    nbIntervals += 1
        return len(parameters), nbIntervals, nbParamsInBounds

    def getInfos(self):
        nbStates = self.nbStates()
        nbTransitions = self.nbTransitions()
        nbParameters, nbIntervals, nbParamsInBounds = self.countParametersInIntervals()

        result = {}
        result['#states'] = nbStates
        result['#transitions'] = nbTransitions
        result['ratioIntervals'] = nbIntervals / float(nbTransitions) if nbTransitions != 0 else 0
        result['ratioParamInBounds'] = nbParamsInBounds / (2. * nbIntervals) if nbIntervals != 0 else 0
        result['#intervals'] = nbIntervals
        result['#parameters'] = nbParameters
        result['#paramInBounds'] = nbParamsInBounds
        result['initialState'] = self.getInitialState()
        return result


    def export(self, file="/dev/stdout"):
        states = sorted(self.getStates(), key=int)
        with open(file, 'w') as f:
            f.write('Type: pIMC\n')
            f.write('Nodes: %s\n' % (self.nbStates()))
            f.write('Parameters: %s\n' % (self.nbParameters()))
            for param in self.getParameters():
                f.write('%s\n' % (param))
            f.write('Labels:\n')
            f.write('%s : %s\n' % (self.initialState, self.getLabel(self.initialState)))
            for state in states:
                if state != self.initialState:
                    f.write('%s : %s\n' % (state, self.getLabel(state)))
            f.write('Edges:\n')
            for s in states:
                for ss in sorted(self.getSuccessors(s), key=int):
                    f.write("%s->%s | %s\n" % (s, ss, self.getTransitionAsString(s, ss)))
