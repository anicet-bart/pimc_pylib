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
import re

class Solution(object):
    
    def __init__ (self):
        self.values = {}

    def setValue(self, variable, value):
        value = value.strip()
        if value == "1.0":
            value = "1"
        elif value == "0.0":
            value = "0"

        fraction = utils.smtFraction2fraction(value)
        if fraction:
            value = str(fraction)

        self.values[variable] = value

    def getValue(self, stateFrom, stateTo=None):
        if not(stateTo):
            variable = 'r' + stateFrom
        else:
            variable = 't_' + str(stateFrom) + '_' + str(stateTo)

        if variable in self.values:
            return self.values[variable]
        else:
            return None

    def isReachable(self, state):
        variable = 'r' + state
        if variable in self.values:
            value = self.values[variable]
            return (value == "true" or value == "1")
        return False

    def __str__(self):
        return str(self.values)
    def __repr__(self):
        return self.values

    @staticmethod
    def parse(file):
        solution = Solution()
        f = open(file, 'r')
        solution.parseFormatSmtlib(f)
        return solution
        #for line in f:
        #    variable = line.split('=')
        #    solution.setValue(variable[0].strip(), variable[1].strip())
        #return solution


    def parseFormatSmtlib(self, file):
        content = file.read()
        valuations = [e[1:-1] for e in re.findall(r'\([a-zA-Z0-9_]+ [^\)]+\)', content)]
        for valuation in valuations:
            iSeparator = valuation.index(" ")
            self.setValue(valuation[:iSeparator], valuation[iSeparator:])


