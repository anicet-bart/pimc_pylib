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

class SumWithParameters(object):
    def __init__(self, parameters):
        assert(not 'constant' in parameters)
        self.parameters = parameters
        self.values = {'constant':[]}
        
    def add(self, parameter, coefficient=1):
        if parameter != None:
            # It is a parameter to add
            if parameter in self.parameters:
                if not parameter in self.values:
                    self.values[parameter] = coefficient
                else:
                    self.values[parameter] += coefficient
            # It is a constant value to add
            else:
                self.values['constant'].append(str(parameter))
          
    def isConstant(self):
        return (len(self.values) == 1 ) and ('constant' in self.values)         
          
    def getConstant(self):
        return self.values['constant']          
          
    def getCoefficient(self, key):
        if key in self.values:
            return self.values[key]
        return 0

    def getParameters(self):
        return self.parameters
          
    def normalize(self):
        result = []
        for key in self.values:
            if key != 'constant' and self.values[key] == 0:
                result.append(key)
                
        for key in result:
            del self.values[key]
          
    def __str__(self):
        result = ""
        for key in self.values:
            if key != 'constant':
                if result:
                    result += " + "
                if self.values[key] == -1:
                    result += "-"
                elif self.values[key] != 1:
                    result += str(self.values[key])
                result += key
        if self.values['constant'] != 0 or not result:
            if result:
                result += " + "
            result += ("%s" % (self.values['constant']))
        return result
    def __repr__(self):
        return self.values


class Inequation(object):    
    
    def __init__(self, operator, parameters):
        self.operator = operator
        self.lhs = SumWithParameters(parameters)
        self.rhs = SumWithParameters(parameters)
        self.name = ""
        
    def getOperator(self):
        return self.operator        
        
    def getParameters(self):
        return self.lhs.getParameters()
        
    def getCoefficientLHS(self, parameter):
        return self.lhs.getCoefficient(parameter)
     
    def getCoefficientRHS(self, parameter):
        return self.rhs.getCoefficient(parameter)     
     
    def getConstantLHS(self):
        return self.lhs.getConstant()
     
    def getConstantRHS(self):
        return self.rhs.getConstant()       
     
    def addLHS(self, value):
        self.lhs.add(value)
        
    def addRHS(self, value):
        self.rhs.add(value)
        
    def isTautology(self):
        if self.lhs.isConstant() and self.rhs.isConstant():
            return eval(str(self))
        return False
        
    def isContradiction(self):
        if self.lhs.isConstant() and self.rhs.isConstant():
            return not eval(str(self))
        return False
    
    def normalize(self):
        coef = 0

        for key in self.rhs.values:
            if key != 'constant':
                coef = -self.rhs.getCoefficient(key)
                self.lhs.add(key, coef)
                self.rhs.add(key, coef)
            else:
                coef = -self.lhs.getCoefficient(key)
                self.rhs.add(coef)
                self.lhs.add(coef)
        self.lhs.normalize()
        self.rhs.normalize()
        return self
        
    @staticmethod
    def tautology():
        result = Inequation("==", [])
        result.addLHS(0)
        result.addRHS(0) 
        return result
        
    @staticmethod
    def contradiction():
        result = Inequation("==", [])
        result.addLHS(0)
        result.addRHS(1)    
        return result
        
    def size(self):
        return 1      
        
    def __str__(self, nbIndents=0):
        indent = ' ' * nbIndents
        return indent + str(self.lhs) + ' ' + self.operator + ' ' + str(self.rhs)
        
    def __repr__(self):
        return self.__str__()