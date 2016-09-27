# -*- coding: utf-8 -*-
"""
Created on Fri May 20 15:34:21 2016

@author: Anicet
"""

import utils
import collections
import inequation

class Variable(object):
    def __init__(self, name):
        self.name = str(name)

    def getName(self):
        return self.name

    def isTautology(self):
        return False
        
    def isContradiction(self):
        return False
        
    def normalize(self):
        return self
    
    def size(self):
        return 1
        
    def __str__(self, nbIndents=0):
        return ' ' * nbIndents + self.name
    def __repr__(self):
        return self.__str__()

class BooleanVariable(Variable):
    def __init__(self, name):
        super(BooleanVariable, self).__init__(name)

class Constraint(object):
    
    TAUTOLOGY = inequation.Inequation.tautology()
    CONTRADICTION = inequation.Inequation.contradiction()
    
    def __init__(self, expression, variables, name):
        utils.isType(expression, str) and utils.isType(variables, str)
        self.expression = expression
        self.variables = variables
        self.name = str(name)
        self.checkMissingVariablesInExpression()


    def checkMissingVariablesInExpression(self):
        variables = self.missingVariablesInExpression()
        if variables:
            print("[Warning] variables are missing in the given constraint expression:")
            print("* constraint expression : %s" % (self.expression))
            print("* constraint variable(s): %s" % (self.variables))
            print("* missing variable(s)   : %s" % (variables))

    def missingVariablesInExpression(self):
        result = set()
        for var in self.variables:
            if not str(var) in self.expression:
                result.add(var)
        return result

    def getExpression(self):
        return self.expression
    def getVariables(self):
        return self.variables
    def getName(self):
        return self.name
        
    def __str__(self):
        return ("%s: %s (scope %s)" % (self.name, self.expression, self.variables))
    def __repr__(self):
        return self.__str__()


class Model(object):
    
    def __init__(self):
        self.variables = set()
        self.constraints = set()
        
    def __str__(self):
        return ("#variables: %d\n%s\n#constraints: %d\n%s" % 
            (len(self.variables), self.variables,
             len(self.constraints), self.constraints))


    def addVariable(self, variable):
        utils.isInstance(variable, Variable)
        self.variables.add(variable)        

    def addConstraint(self, constraint):
        utils.isInstance(constraint, Constraint)
        self.constraints.add(constraint)        


class Conjunction(object):
    def __init__(self, constraints=[], name=""):
        self.name = name
        self.constraints = constraints
        
    def getName(self):
        return self.name        
        
    def addConstraint(self, constraint):
        self.constraints.append(constraint)
        #self.normalize()
        
    def addConstraints(self, constraints):
        self.constraints.extend(constraints)        
        
    def getConstraints(self):
        return self.constraints

    def isTautology(self):
        for constraint in self.constraints:
            if not constraint.isTautology():
                return False
        self.constraints = [Constraint.TAUTOLOGY]
        return True
        
    def isContradiction(self):
        for constraint in self.constraints:
            if constraint.isContradiction():
                self.constraints = [Constraint.CONTRADICTION] 
                return True
        return False
    
    def normalize(self):
        if self.isTautology():
            self.constraints = [Constraint.TAUTOLOGY]
        
        elif self.isContradiction():
            self.constraints = [Constraint.CONTRADICTION]

        else:
            self.constraints = [c.normalize() for c in self.constraints if not c.isTautology()]
        return self
            
    def size(self):
        result = 0
        for constraint in self.constraints:
            result += constraint.size()
        return result

    def __str__(self, nbIndents=0):
        indent = ' ' * nbIndents
        result = indent + self.name + " = inter(\n"
        first = True        
        
        for constraint in self.constraints:
            if first:                
                first = False
            else:
                result += ",\n"
            result += constraint.__str__(nbIndents+1)
        result += indent + ")"
        return result        
        
    def __repr__(self):
        return self.__str__()

class Disjunction(Conjunction):

        
    def isTautology(self):
        for constraint in self.constraints:
            if constraint.isTautology():
                self.constraints = [Constraint.TAUTOLOGY]
                return True
        return False
        
    def isContradiction(self):
        for constraint in self.constraints:
            if not constraint.isContradiction():
                return False
        self.constraints = [Constraint.CONTRADICTION]
        return True      
        
    def normalize(self):
        if self.isTautology():
            self.constraints = [Constraint.TAUTOLOGY]
        
        elif self.isContradiction():
            self.constraints = [Constraint.CONTRADICTION]

        else:
            self.constraints = [c.normalize() for c in self.constraints if not c.isContradiction()]
        return self
        
    def __str__(self, nbIndents=0):
        indent = ' ' * nbIndents
        result = indent + self.name + " = union(\n"
        first = True        
        
        for constraint in self.constraints:
            if first:                
                first = False
            else:
                result += ",\n"
            result += constraint.__str__(nbIndents+1)
        result += indent + ")"
        return result       
    def __repr__(self):
        return self.__str__()
        
        
class Equivalence:
    def __init__(self, name="", left=None, right=None):
        self.name = name
        self.left = left
        self.right = right
        
    def getName(self):
        return self.name        
        
    def setLHS(self, constraint):
        self.left = constraint
        
    def setRHS(self, constraint):
        self.right = constraint
        
    def getLHS(self):
        return self.left
        
    def getRHS(self):
        return self.right
        
    def isTautology(self):
        return False
        
    def isContradiction(self):
        return False 
        
    def normalize(self):
        self.left.normalize()
        self.right.normalize()
        return self
        
    def size(self):
        return 1 + self.left.size() + self.right.size()

    def __str__(self, nbIndents=0):
        indent = ' ' * nbIndents
        result = indent + \
            self.getLHS().__str__(nbIndents+1) +  " <=>\n" + \
            self.getRHS().__str__(nbIndents+1)
        return result       
    def __repr__(self):
        return self.__str__()