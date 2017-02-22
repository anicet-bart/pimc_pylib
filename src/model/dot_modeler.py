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

from core.inequation import *
from core.model import *

from cStringIO import StringIO

class DotModeler(object):
    COLOR_ACTIVE   = "#4d839d"
    COLOR_INACTIVE = "#ECF0F2"
    COLOR_ACTIVE_DARK   = "black"
    COLOR_INACTIVE_DARK = "gray"

    def __init__ (self, pimc, file=None, solution=None):
        self.pimc = pimc
        self.file = file
        self.solution = solution

        if file:
            self.out = open(file, "w")
        else:
            self.out = StringIO()

        self.header()
        self.addNodes()
        self.out.write('\n')
        self.addEdges()
        self.footer()
        #self.out.close()

    def header(self):
        self.out.write('strict digraph loopgraph {\n')
        self.out.write('\tnode [fontsize=10 style="rounded,filled"  margin=0.02 width=0 height=0];\n')
        self.out.write('\tedge [fontsize=10];\n')
        self.out.write('\tgraph [fontsize=10 style="rounded,filled" color=black fillcolor="#ECF0F2"];\n')
        self.out.write('\n')

    def footer(self):
        self.out.write('}\n')

    def addNodes(self):
        self.addNode(self.pimc.getInitialState())
        for state in sorted(self.pimc.getStates(), key=int):
            self.addNode(state)

    def addNode(self, state):
        label = self.pimc.getLabel(state).replace('"', '\\"')
        reachable = self.solution.isReachable(state) if self.solution else False
        fillcolor = DotModeler.COLOR_ACTIVE if reachable else DotModeler.COLOR_INACTIVE
        arrowcolor = DotModeler.COLOR_ACTIVE_DARK if reachable else DotModeler.COLOR_INACTIVE_DARK
        self.out.write('\tSTATE%s[label="%s" xlabel="%s" fillcolor="%s" color="%s" shape="circle"];\n' % (state, state, label, fillcolor, arrowcolor))

    def addEdges(self):
        for s in self.pimc.getStates():
            for ss in self.pimc.getSuccessors(s):
                label = ""
                reachable = True
                if self.solution:
                    label = self.solution.getValue(s, ss)
                    if label == '0':
                        reachable = False
                    label = label + " | " if label else ""

                if str(self.transition(s, ss)) != label:
                    label += str(self.transition(s, ss))
                #print ("%s -> %s = %s" % (s,ss,label))
                self.addEdge(s, ss, label, reachable)

    def addEdge(self, stateFrom, stateTo, label, reachable=True):
        style =  '' if reachable else 'style="dashed"'
        arrowcolor = DotModeler.COLOR_ACTIVE_DARK if reachable else DotModeler.COLOR_INACTIVE_DARK
        self.out.write('\tSTATE%s -> STATE%s[%s label=" %s" color="%s" fillcolor="%s"];\n' % (stateFrom, stateTo, style, label, arrowcolor, arrowcolor))

    def transition(self, stateFrom, stateTo):
        interval = self.pimc.getTransition(stateFrom, stateTo)
        replace = {"0.":"0", "0.0": "0", "1.":"1", "1.0":"1"}
        if interval['lb'] in replace:
            interval['lb'] = replace[interval['lb']]
        if interval['ub'] in replace:
            interval['ub'] = replace[interval['ub']]

        if (interval['lb'] == interval['ub']):
            return interval['lb']
        else:
            return "[%s,%s]" % (interval['lb'], interval['ub'])

    @staticmethod
    def export (pimc, file=None, solution=None):
        dot = DotModeler(pimc, file, solution)
        if file:
            return file
        else:
            return dot.out.getvalue()


