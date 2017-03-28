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

import core.utils as utils
import fractions
from copy import copy
import itertools

import sympy
class Calculator:
    # Associate to each operator its precedence value
    OPERATORS  = { "+": 0, "-": 0, "*": 1, "/": 1, "(": 2, ")": 2}

    def __init__ (self):
        self.stack = []

    def push(self, p):
        if p in ['+', '-', '*', '/']:
            op1 = self.stack.pop()
            op2 = self.stack.pop()
            self.stack.append ('(%s %s %s)' % (op1, p, op2) )
        elif p == '!':
            op = self.stack.pop()
            self.stack.append ('%s!' % (op) )
        elif p in ['sin', 'cos', 'tan']:
            op = self.stack.pop()
            self.stack.append('%s(%s)' % (p, op) )
        else:
            self.stack.append(p)

    def convert(self, l):
        l.reverse()
        for e in l:
            self.push(e)
        return self.stack.pop()

    @staticmethod
    def infix_prefix(tokens):
        operandStack = []
        operatorStack = []

        if len(tokens) == 1: return tokens

        for token in tokens:
            # if token is an operator 
            # => push it onto the operand stack
            if not(token in Calculator.OPERATORS):
                operandStack.append(token)

            # if token is a left parentheses or operator of lower priority than the last, or the operator stack is empty,
            # => push it onto the operator stack
            elif token == '(' or not(operatorStack) or Calculator.OPERATORS[operatorStack[-1]] > Calculator.OPERATORS[token]:
                operatorStack.append(token)

            # if token is right parentheses
            elif token == ')':
                # Continue to pop operator and operand stacks, building 
                # prefix expressions until left parentheses is found. 
                # Each prefix expression is push back onto the operand 
                # stack as either a left or right operand for the next operator. 
                while operatorStack[-1] != '(':
                    operator = operatorStack.pop() 
                    rightOperand = operandStack.pop() 
                    leftOperand = operandStack.pop() 
                    operandStack.append([operator, leftOperand, rightOperand])
        
                # Pop the left parentheses from the operator stack. 
                operatorStack.pop()

            # if hierarchy of token is less than or equal to hierarchy of top of the operator stack )
            elif Calculator.OPERATORS[operatorStack[-1]] >= Calculator.OPERATORS[token]:
                # Continue to pop operator and operand stack, building prefix 
                # expressions until the stack is empty or until an operator at 
                # the top of the operator stack has a lower hierarchy than that of the token. 
                while operatorStack and Calculator.OPERATORS[operatorStack[-1]] <= Calculator.OPERATORS[token]: 
                    operator = operatorStack.pop() 
                    rightOperand = operandStack.pop() 
                    leftOperand = operandStack.pop()                     
                    operandStack.append([operator, leftOperand, rightOperand])
        
                # Push the lower precedence operator onto the stack 
                operatorStack.append(token)

        # If the stack is not empty, continue to pop operator and operand stacks 
        # building prefix expressions until the operator stack is empty. 
        while operatorStack:
            operator = operatorStack.pop() 
            rightOperand = operandStack.pop() 
            leftOperand = operandStack.pop() 
            operandStack.append([operator, leftOperand, rightOperand])

        return operandStack[0]

    def prefix_to_flat(tokens):
        result = list(tokens)
        found = True
        # Loop while a sublist has been flatted
        while found:
            found = False
            tmp = []
            # Loop over all the tokens in the list
            for e in result:
                # If a token is a list which is not a string
                if type(e) is list and not(type(e) is str):
                    # Add parentheses and join the sublist with the main list
                    tmp.append('(')
                    tmp.extend(e)
                    tmp.append(')')
                    found = True
                
                # Check if if is the - unary operator
                elif len(e) > 1 and e[0] == '-' and e != "-":
                    tmp.extend(['(', '-', e[1:], ')'])

                # Else the token is added into the main list
                else:
                    tmp.append(e)

            result = tmp

        if len(result) > 1 and result[0] != '(':
            result.insert(0, '(')
            result.append(')')
        return result

    def flat_to_string(tokens):
        result = " ".join(tokens)
        result = result.replace("( ", "(").replace(" )", ")")
        return result

    @staticmethod
    def simplify(prefixedExpr):
        c = Calculator()
        # TODO: assume that no more than binary operators
        expr = prefixedExpr.replace("(", "").replace(")", "").split(" ")
        infixedExpr = c.convert(expr)
        simplifiedInfix = "%s" % sympy.simplify(infixedExpr)
        
        # Add space before and after operators (warning with unary opperator -)
        simplifiedInfix = simplifiedInfix.replace("/", " / ").replace("*", " * ").replace("(", " ( ").replace(")", " ) ")
        
        simplifiedPrefix = Calculator.infix_prefix(simplifiedInfix.split())
        simplifiedPrefix = Calculator.prefix_to_flat(simplifiedPrefix)

        return Calculator.flat_to_string(simplifiedPrefix)
        

class Reducer(object):

    @staticmethod
    def moveTransition(pimc, fromBefore, toBefore, fromAfter, toAfter, operator="+"):
        probability = pimc.getTransition(fromBefore, toBefore)
        pimc.removeTransition(fromBefore, toBefore)
        result = pimc.getTransition(fromAfter, toAfter)
        if not(result):
            result = probability
        else:
            if not(utils.isDict(probability)):
                probability = {'lb': probability, 'ub':probability}
            if not(utils.isDict(result)):
                result = {'lb': result, 'ub':result}
            result = {
                'lb': "(%s %s %s)" % (operator, result['lb'], probability['lb']),
                'ub': "(%s %s %s)" % (operator, result['ub'], probability['ub'])
            }
        pimc.setProbability(fromAfter, toAfter, result)

    @staticmethod
    def removeStraightStates(pimc):
        toRemove = set()
        removed = set()
        # Search for straight states (non absorbing states with only one successor)
        for s in pimc.getStates():
            if len(pimc.getSuccessors(s)) == 1 and not(pimc.isAbsorbingState(s)):
                toRemove.add(s)
        
        for s in toRemove:
            # The successors of "s" are replaced by the successors of its successor "ss"
            if not(s in removed):
                ss = next(iter(pimc.getSuccessors(s)))
                pimc.removeTransition(s, ss)

                # Move transitions (ss, sss) to (s, sss)
                for sss in pimc.getSuccessors(ss):
                    # If self loop (ss, ss) then set self loop (s, s)
                    if sss == ss:
                        Reducer.moveTransition(pimc, ss, ss, s, s, "*")
                    else:
                        Reducer.moveTransition(pimc, ss, sss, s, sss, "*")

                # Move transitions (sss, ss) to (sss, s)
                predecessors = set(pimc.getPredecessors(ss))
                for sss in predecessors:
                    Reducer.moveTransition(pimc, sss, ss, sss, s, "*")

                pimc.addLabels(s, pimc.getLabels(ss))
                removed.add(ss)

        print(sorted(removed))
        # Recursive call until fix point
        if toRemove:
            Reducer.removeStraightStates(pimc)
        for s in removed:
            pimc.removeState(s)



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
        if statesToRemove:
            bottomState = next(iter(statesToRemove))
            statesToRemove.remove(bottomState)
        else:
            bottomState = None
        
        pimc.removeStates(statesToRemove)
        
        # Replace unify removed states with repectively topState and bottomState
        for s in pimc.getStates():
            for ss in pimc.getSuccessors(s):
                # Warning order important: test first target states
                if ss in targetStates:
                    Reducer.moveTransition(pimc, s, ss, s, topState, "*")
                elif ss in statesToRemove:
                    Reducer.moveTransition(pimc, s, ss, s, bottomState, "*")
        pimc.setLabel(topState, label)
        
    @staticmethod
    def simplifyExpressionsOnTransitions(pimc):
        for s in pimc.getStates():
            for ss in pimc.getSuccessors(s):
                transition = pimc.getTransition(s, ss)
                pimc.removeTransition(s, ss)
                if not(utils.isDict(transition)):
                    bound = Calculator.simplify(transition)
                    transition = {'lb':bound, 'ub': bound}
                elif transition['lb'] == transition['ub']:
                    transition['lb'] = Calculator.simplify(transition['lb'])
                    transition['ub'] = transition['lb']
                else:
                    transition['lb'] = Calculator.simplify(transition['lb'])
                    transition['ub'] = Calculator.simplify(transition['ub'])
                pimc.setProbability(s, ss, transition)
