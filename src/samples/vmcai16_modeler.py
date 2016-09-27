# -*- coding: utf-8 -*-
"""
Created on Fri May 20 10:50:19 2016

@author: Anicet
"""
import utils
from readers import *
from model import *
from inequation import *


class ModelerVMCAI16(object):
    def __init__(self):
        self.nConsistencies = dict()
        
    def modelPIMC(self, pimc):
        result = []
        states = pimc.getStates()        
        
        for state in states:
            lc = self.LC(state, states, pimc)            
            #print("LC(%s, %s) = %s" % (state, states, lc))
            result.extend(lc)

       
    def LP(self, state, pimc):
        result = []
        for s in pimc.getSuccessors(state):
            interval = pimc.getTransition(state, s)
            if interval:
                if pimc.isParameter(interval['lb']):
                    result.append(interval['lb'])
        return result
                    
    def withZero(self, state, pimc):
       result = []
       for s in pimc.getSuccessors(state):
            interval = pimc.getTransition(state, s)
            if interval:
                if pimc.isParameter(interval['lb']):
                    result.append(s)
                elif (interval['lb'] == 0) or (interval['lb'] == "0"):
                    result.append(s)
       return result
       
    def LC(self, state, states, pimc):
        result = []
        parameters = pimc.getParameters()
        cstrsLB = Inequation("<=", parameters)
        cstrsUB = Inequation(">=", parameters)          
        
        for s in states:
            interval = pimc.getTransition(state, s)
            if interval:
                cstrsLB.addLHS(interval['lb'])
                cstrsUB.addLHS(interval['ub'])
            
                # Lower bound lower than or equal to upper bound
                # interval['lb'] <= interval['ub']
                tmp = Inequation("<=", parameters)
                tmp.addLHS(interval['lb'])
                tmp.addRHS(interval['ub'])
                result.append(tmp)

        # Sum of lower bounds (lb) lower than one
        cstrsLB.addRHS(1)
        # Sum of upper bounds (ub) greater than one  
        cstrsUB.addRHS(1)
        
        result = [cstrsLB, cstrsUB] + result 
        return result
        

    def setLowerBoundsToZero(self, fromState, states, pimc):
        result = []
        parameters = pimc.getParameters()
        
        for state in states:
            interval = pimc.getTransition(fromState, state)
            if interval:
                # interval['lb'] = 0
                tmp = Inequation("==", parameters)
                tmp.addLHS(interval['lb'])
                tmp.addRHS(0)
                result.append(tmp)
        return result

    def nConsistencyLocal(self, state, states, n, pimc):
        name = "Cons_%s(%s,%s)" % (n, state, list(states))
        result = Conjunction(name=name, constraints=[])
        
        if n >= 0:
            for s in (pimc.getSuccessors(state) - states):
                result.addConstraint(self.nConsistency(s, n-1, pimc))
        result.addConstraints(self.LC(state, pimc.getSuccessors(state) - states, pimc))
        result.addConstraints(self.setLowerBoundsToZero(state, states, pimc))
        return result
        
    def nConsistency(self, state, n, pimc):
        name = "Cons_%s(%s)" % (n, state)

        if name in self.nConsistencies:
            result = self.nConsistencies[name]['eqVariable']
        else:
            if n == 0:
                result = Conjunction(name=name, constraints=self.LC(state, pimc.getSuccessors(state), pimc))
            else:  
                result = Disjunction(name=name, constraints=[])
                for states in utils.powersetSet(self.withZero(state, pimc)):
                    result.addConstraint(self.nConsistencyLocal(state, states, n, pimc))
            
            eqVariable = BooleanVariable("EqVar"+name)
            equivalence = Equivalence(name="Eq"+name, left=eqVariable, right=result)

            self.nConsistencies[name] = dict(eqVariable=eqVariable, equivalence=equivalence)
            result = eqVariable
        return result                

    def consistency(self, pimc):
        constraints = Conjunction(constraints=[])
        constraints.addConstraint(self.nConsistency(pimc.getInitialState(), pimc.nbStates(), pimc))
        for elt in self.nConsistencies:
            constraints.addConstraint(self.nConsistencies[elt]['equivalence'])

        result = {}
        result['constraints'] = constraints
        result['contVars'] = pimc.getParameters()
        result['boolVars'] = [self.nConsistencies[elt]['eqVariable'] for elt in self.nConsistencies]
        return result


    def nReachabilityLocal(self, state, localStates, goalStates, n, pimc):
        name = "Reach_%s(%s,X=%s,G=%s)" % (n, state, list(localStates), list(goalStates))
        result = Conjunction(name=name, constraints=[])
        
        result.addConstraint(self.nConsistencyLocal(state, localStates, pimc.nbStates() ,pimc))
        if state in goalStates:
            isStateInGoal = Inequation.tautology()
        else:
            isStateInGoal = Inequation.contradiction()

        if n == 0:
            result.addConstraint(isStateInGoal)
        else:  
            innerDisjunction = Disjunction(constraints=[])
            innerDisjunction.addConstraint(isStateInGoal)
            for sPrime in (pimc.getSuccessors(state) - localStates):
                innerConjunction = Conjunction(constraints=[])
                innerConjunction.addConstraint(self.nReachability(sPrime, goalStates, n-1, pimc))
                
                # pimc.up(state, s') > 0
                constraint = Inequation(">", pimc.getParameters())
                constraint.addLHS(pimc.up(state, sPrime))
                innerConjunction.addConstraint(constraint)
                
                # \Sigma{ pimc.low(state, s'') < 1 }
                constraint = Inequation("<", pimc.getParameters())
                for sSecond in pimc.getStates():
                    if sSecond != sPrime:
                        constraint.addLHS(pimc.low(state, sSecond))
                constraint.addRHS(1)
                innerConjunction.addConstraint(constraint)
                
                innerDisjunction.addConstraint(innerConjunction)
            result.addConstraint(innerDisjunction)
        return result    
        
    def nReachability(self, state, goalStates, n, pimc):
        name = "Reach_%s(%s,G=%s)" % (n, state, list(goalStates))
        result = Disjunction(name=name, constraints=[])      
        
        for states in utils.powersetSet(self.withZero(state, pimc)):
            result.addConstraint(self.nReachabilityLocal(state, states, goalStates, n, pimc))
        return result  

    def reachability(self, state, goalStates, n, pimc):
        result = Conjunction(constraints=[])
        result.addConstraint(self.nReachability(state, goalStates, n, pimc))
        for elt in self.nConsistencies:
            result.addConstraint(self.nConsistencies[elt]['equivalence'])
        return result
