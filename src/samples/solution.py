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

class Solution(object):
    
    def __init__ (self):
        self.values = {}

    def setValue(self, variable, value):
        self.values[variable] = value

    def getValue(self, stateFrom, stateTo=None):
        if not(stateTo):
            variable = stateFrom
        else:
            variable = 't_' + str(stateFrom) + ',' + str(stateTo)

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

