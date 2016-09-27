# -*- coding: utf-8 -*-
"""
Created on Fri May 20 15:27:06 2016

@author: Anicet
"""
import utils
import fractions
from copy import copy

class MC(object):
    def __init__(self):
        self.states = set()
        self.initialState = None
        self.labels = {}
        self.transitionFunction = {}
        
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
     
    def nbStates(self):
        return len(self.states)
     
    def getSuccessors(self, state):
        if state in self.transitionFunction:
            return set(self.transitionFunction[state].keys())
        else:
            return set()
     
    def setLabels(self, labels):
        utils.isType(labels, dict)            
        self.labels = labels
        
    def getLabel(self, state):
        assert(state in self.labels)
        return self.labels[state]

    def getTransition(self, stateFrom, stateTo):
        if stateFrom in self.transitionFunction and stateTo in self.transitionFunction[stateFrom]:
            return self.transitionFunction[stateFrom][stateTo]
        return None     
     
    def setProbability(self, nodeFrom, nodeTo, probability):
        if not (nodeFrom in self.states):
            raise Exception("Undeclared state '%s'." % (nodeFrom))
        if not (nodeTo in self.states):
            raise Exception("Undeclared state '%s'." % (nodeTo))
        
        if not(nodeFrom in self.transitionFunction):
            self.transitionFunction[nodeFrom] = {}
        self.transitionFunction[nodeFrom][nodeTo] = probability
        
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
            for successor in self.transitionFunction[state]:
                result[successor].add(state)
        for state in self.states:
            result[state] = sorted(result[state])
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
        
    def setParameters(self, parameters):
        if (type(parameters) == set):
            self.parameters = parameters
        else:
            self.parameters = set(parameters)
      
    def isParameter(self, value):
        return value in self.parameters
      
    def getParameters(self):
        return self.parameters
      
    def setProbabilityFromString(self, nodeFrom, nodeTo, probability):
        bounds = probability.split(';')
        # Lower bound
        lowerBound = "".join(bounds[0].split()) # removes spaces
        if not(lowerBound in self.parameters):
            if self.useFractions:
                lowerBound = fractions.Fraction(lowerBound)
            else:
                lowerBound = lowerBound

            
        # Upper bound
        if len(bounds) > 1:
            upperBound = "".join(bounds[1].split()) # removes spaces
            if not(upperBound in self.parameters):
                if self.useFractions:
                    upperBound = fractions.Fraction(upperBound)
                else:
                    upperBound = upperBound
        else:
            upperBound = copy(lowerBound)
        self.setProbability(nodeFrom, nodeTo, {'lb': lowerBound, 'ub':upperBound})
        
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
        result['ratioIntervals'] = nbIntervals / float(nbTransitions)
        result['ratioParamInBounds'] = nbParamsInBounds / (2. * nbIntervals)
        result['#intervals'] = nbIntervals
        result['#parameters'] = nbParameters
        result['#paramInBounds'] = nbParamsInBounds
        result['initialState'] = self.getInitialState()
        return result
