# -*- coding: utf-8 -*-
"""
Created on Wed Sep 2 13:08:23 2016

@author: Anicet
"""

class Solution(object):
    
    def __init__ (self):
        self.values = {}

    def setValue(self, variable, value):
        self.values[variable] = value

    def getValue(self, stateFrom, stateTo=None):
        if not(stateTo):
            variable = stateFrom
        else:
            variable = 'x_' + str(stateFrom) + ',' + str(stateTo)

        if variable in self.values:
            return self.values[variable]
        else:
            return None

    def __str__(self):
        return str(self.values)
    def __repr__(self):
        return self.values

    @staticmethod
    def parse(file):
        solution = Solution()
        f = open(file, 'r')

        for line in f:
            variable = line.split('=')
            solution.setValue(variable[0].strip(), variable[1].strip())
        return solution

    @staticmethod
    def export (pimc, file):
        dot = DotModeler(pimc, file)

