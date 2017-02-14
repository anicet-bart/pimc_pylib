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

import utils
import fractions
from copy import copy

class Reducer(object):

    @staticmethod
    def moveTransition(pimc, fromState, toStateBefore, toStateAfter):
        probability = pimc.getTransition(fromState, toStateBefore)
        pimc.removeTransition(fromState, toStateBefore)
        result = pimc.getTransition(fromState, toStateAfter)
        if not(result):
            result = probability
        else:
            if not(utils.isDict(probability)):
                probability = {'lb': probability, 'ub':probability}
            if not(utils.isDict(result)):
                result = {'lb': result, 'ub':result}
            result = {
                'lb': "(+ %s %s)" % (result['lb'], probability['lb']),
                'ub': "(+ %s %s)" % (result['ub'], probability['ub'])
            }
        pimc.setProbability(fromState, toStateAfter, result)

    @staticmethod
    def removeStraightStates(pimc):
        toRemove = set()
        # Search for straight states (non absorbing states with only one successor)
        for s in pimc.getStates():
            if len(pimc.getSuccessors(s)) == 1 and not(pimc.isAbsorbingState(s)):
                toRemove.add(s)

        for s in toRemove:
            # The successors of "s" become the successors of its successor "ss"
            ss = next(iter(pimc.getSuccessors(s)))
            pimc.removeTransition(s, ss)
            for sss in pimc.getSuccessors(ss):
                pimc.setProbability(s, sss, pimc.getTransition(ss, sss))
            pimc.removeState(ss)

        # Recursive call until fix point
        if toRemove:
            Reducer.removeStraightStates(pimc)


    @staticmethod
    def keepOnlyStatesReachingLabel(pimc, label):
        # Get all the target states and make them absorbing states
        # and select one of them to become the only one target state to keep (the topState)
        targetStates = pimc.getStatesWithLabel(label)
        pimc.setAbsorbingStates(targetStates)
        topState = next(iter(targetStates))
        
        # Get all the states reaching a target state
        statesReachingTarget = pimc.getAncestors(targetStates)
        statesReachingTarget.update(statesReachingTarget)
        
        # Get all the states reached from the initial state
        initialState = pimc.getInitialState()
        statesReachedFromInit = pimc.getChildren([initialState])
        statesReachedFromInit.add(initialState)

        # Compute the set of states to remove and remove them
        statesToRemove = (pimc.getStates() - (statesReachingTarget & statesReachedFromInit)) | targetStates
        statesToRemove -= set([topState,initialState])
        bottomState = next(iter(statesToRemove))
        statesToRemove.remove(bottomState)
        pimc.removeStates(statesToRemove)
        
        # Replace unify removed states with repectively topState and bottomState
        for s in pimc.getStates():
            for ss in pimc.getSuccessors(s):
                # Warning order important: test first target states
                if ss in targetStates:
                    Reducer.moveTransition(pimc, s, ss, topState)
                elif ss in statesToRemove:
                    Reducer.moveTransition(pimc, s, ss, bottomState)
