# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 13:08:23 2016

@author: Anicet
"""

from inequation import *
from model import *

class DotModeler(object):
    
    def __init__ (self, pimc, file, solution=None):
        self.pimc = pimc
        self.file = file
        self.solution = solution

        print(solution)
        self.out = open(file, "w")
        self.header()
        self.addNodes()
        self.out.write('\n')
        self.addEdges()
        self.footer()
        self.out.close()

    def header(self):
        self.out.write('strict digraph loopgraph {\n')
        self.out.write('\tnode [fontsize=10 style="rounded,filled" color="grey" margin=0.02 width=0 height=0];\n')
        self.out.write('\tedge [fontsize=10];\n')
        self.out.write('\tgraph [fontsize=10 style="rounded,filled" color=black fillcolor="#ECF0F2"];\n')
        self.out.write('\n')

    def footer(self):
        self.out.write('}\n')

    def addNodes(self):
        for state in self.pimc.getStates():
            label = None
            if self.solution:
                label = self.solution.getValue(state)
            if not(label):
                label = self.pimc.getLabel(state)
            self.addNode(state, label)

    def addNode(self, state, label):
        self.out.write('\tSTATE%s[label="%s" xlabel="%s" fillcolor="#d36b00" shape="circle"];\n' % (state, state, label))

    def addEdges(self):
        for s in self.pimc.getStates():
            for ss in self.pimc.getSuccessors(s):
                label = ""
                reachable = True
                if self.solution:
                    label = self.solution.getValue(s, ss)
                    if label == '0':
                        reachable = False
                    label = label if label else ""

                if reachable:
                    if str(self.transition(s, ss)) != label:
                        label += " " + str(self.transition(s, ss))
                else:
                    label = "0"
                print ("%s -> %s = %s" % (s,ss,label))
                self.addEdge(s, ss, label, reachable)

    def addEdge(self, stateFrom, stateTo, label, reachable=True):
        style =  '' if reachable else 'style="dashed"'
        self.out.write('\tSTATE%s -> STATE%s[color="#d36b00" %s label=" %s"];\n' % (stateFrom, stateTo, style, label))

    def transition(self, stateFrom, stateTo):
        interval = self.pimc.getTransition(stateFrom, stateTo)
        if (interval['lb'] == interval['ub']):
            return interval['lb']
        else:
            return "[%s,%s]" % (interval['lb'], interval['ub'])

    @staticmethod
    def export (pimc, file, solution=None):
        dot = DotModeler(pimc, file, solution)

