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


class PrismModeler(object):

    def __init__(self, pimc, expr2uid):
        self.pimc = pimc
        self.expr2uid = expr2uid

        PrismModeler.normalizeLabels(pimc)
        self.label2id = PrismModeler.indexLabels(pimc)
        self.statesOrder = sorted(self.pimc.getStates(), key=int)
        self.labelOrder = sorted(self.label2id, key=(lambda l: (int(self.label2id[l]) != 0, l)))
        print(self.labelOrder)

    def exportTra(self, file):
        """ Outputs the transition matrix of the given PIMC into the PRISM format (.tra format).
        First line contains the number of states and the number of transitions followed by all the transitions in the PIMC.
        Warning: no variables/parameters allowed in probabilities.
        PRISM format:
        <nb_states> <nb_transitions>
        <state1> <state2> <probability_transition_state1_to_state2>
        ...
        """
        file.write("%s %s\n" % (self.pimc.nbStates(), self.pimc.nbTransitions()))
        for s in self.statesOrder:
            for ss in self.pimc.getSuccessors(s):
                expr = self.pimc.getTransition(s, ss)
                assert(expr['lb'] == expr['ub'])
                expr = expr['lb'].strip()
                expr = self.expr2uid[expr] if (expr in self.expr2uid) else expr
                expr = "1" if expr == "1.0" else expr
                file.write("%s %s %s\n" % (s, ss, expr))

    def exportLab(self, file):
        """ Outputs the labelling of the given PIMC into the PRISM format (.tra format).
        First line indexes the labels/axioms from 0 to the number of labels followed by all the states with their corresponding label indexes
        Warning: labels must be protected with double quotes
        Warning: a state may have zero or many labels (.lab format presents only states with at least one label/axiom)
        Warning: label with index 0 must be the "init" label (identify initial states)
        PRISM format:
        0:"<label_0>" 1="<label_1" 2:"<label_2>"
        <state_1>: <id_label>+
        ...
        Example:
        0="init" 1="deadlock" 2="target"
        0: 0
        1: 1
        2: 2
        3: 1 2
        """
        for l in self.labelOrder:
            file.write("%s=\"%s\" " % (self.label2id[l], l))

        # Print labelling only for states with labels
        initialState = self.pimc.getInitialState()
        for s in self.statesOrder:
            if s == initialState or self.pimc.getLabels(s):
                file.write("\n%s:" % s)
                idLabels = []
                if s == initialState:
                    idLabels.append(self.label2id["init"])
                for l in self.pimc.getLabels(s):
                    if l != "init":
                        idLabels.append(self.label2id[l])	

                for idl in idLabels:
                    file.write(" %s" % idl)


    def exportSta(self, file):
        """
        (a,b)
        0:(false,false)
        1:(true,false)
        2:(false,true)
        """
        file.write("(%s)" % ",".join(self.labelOrder))

        # Print rewards
        initialState = self.pimc.getInitialState()
        for s in self.statesOrder:
            file.write("\n%s:" % s)
            labels = set()
            if s == initialState:
            	labels.add("init")
            for l in self.pimc.getLabels(s):
               	labels.add(l)	

            file.write("(%s)" % ",".join([str(l in labels).lower() for l in self.labelOrder]))

    @staticmethod
    def indexLabels(pimc):
        """ Retreives all the labels in the given PIMC and associate to each one a unique integer id
        Returns a dictionnary associating to each label a unique id.
        Remark: ids starts from zero and are incremented one by one.
        """
        result = {"init": 0}
        for s in pimc.getStates():
            for l in pimc.getLabels(s):
                if not(l in result):
                    result[l] = len(result)
        print(result)
        return result     


    @staticmethod
    def normalizeLabel(label):
        return label.replace(" ", "_").replace('"', "").strip()

    # [TODO] Check unicity normalized names
    @staticmethod
    def normalizeLabels(pimc):
        """ Normalizes all the labels present in the given PIMC
        """
        for s in pimc.getStates():
            labels = set()
            for l in pimc.getLabels(s):
                labels.add(PrismModeler.normalizeLabel(l))
            pimc.setLabel(s, " ".join([PrismModeler.normalizeLabel(l) for l in labels]))

    @staticmethod
    def export (pimc, expr2uid={}, traFile="/dev/stdout", labFile="/dev/stdout", staFile="/dev/stdout"):
        modeler = PrismModeler(pimc, expr2uid)

        file = open(traFile, 'w')
        modeler.exportTra(file)
        file.close()

        file = open(labFile, 'w')
        modeler.exportLab(file)
        file.close()

        file = open(staFile, 'w')
        modeler.exportSta(file)
        file.close()


