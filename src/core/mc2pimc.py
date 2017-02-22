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

# Transition Matrix from PRISM to PIMC format
import random as rd
from networks import *
import ast
import json
import re
import argparse
import fractions

parser = argparse.ArgumentParser("Translates a MC transition function into a PIMC")
parser.add_argument('file',     help='Transition function file')
parser.add_argument('-label',   help='states labeling file')
parser.add_argument('-o',       help='output PIMC file', default='/dev/stdout')
parser.add_argument('-params',  help='list of parameters', default='[]')
parser.add_argument('-replace', help='list of parameters', default='{}')
parser.add_argument('-ri',      help='probability to transform a probability to an interval (value between 0. and 1.)', type=float, default='0.')
parser.add_argument('-rp',      help='probability to transform a bound of an interval to a parameter (value between 0. and 1.)', type=float, default='0.')
args = parser.parse_args()

# Parameters
fileName = args.file
file = open(fileName, 'r')

sizeInfo = file.readline().split()
if len(sizeInfo) != 2:
	raise Exception("The given PRISM model does not describe a deterministic process.")
nbStates, nbTransitions = (int(nb) for nb in sizeInfo)
labelingFile        = args.label
parameters          = utils.toList(ast.literal_eval(args.params))
substitutions       = json.loads(args.replace)
nbParameters        = len(parameters)
percentIntervals    = args.ri if (0 <= args.ri and args.ri <= 1) else 0
percentParametrics  = args.rp if (0 <= args.rp and args.rp <= 1) else 0
nbIntervals         = 0
nbParamsInIntervals = 0
out                 = open(args.o, 'w')

# Get labels from labeling file. Example labeling file content (5 states and 3 labels)
# Remark: some states may have no label
# 0="init" 1="deadlock" 2="target"
# 0: 0
# 1: 1
# 2: 1
# 3: 2
# 4: 1
def getInitialStatFromLabelFile(prismLabelFile):
	file = open(prismLabelFile)
	# Read first line to get the key associated to the initial state
	# 0="init" 1="deadlock"
	header = file.readline()
	labels = {x.split("=")[0]:x.split("=")[1] for x in header.split()}
	initialState = ""
	statesLabeling = {}
	for line in file:
		# Grammar: <state> : <label1> <label2> ... <label_n>
		# Example: 1 : 0 2 7
		labeling = line.split(':')
		labeling[0] = labeling[0].strip()
		labeling[1] = [labels[e.strip()] for e in labeling[1].split()]
		if '\"init\"' in labeling[1]:
			if initialState:
				raise Exception("Too many initial states (only one initial state allowed)")
			initialState = labeling[0]
		statesLabeling[labeling[0]] = labeling[1]
	return initialState, statesLabeling

# Get states/nodes from the MC transition probabilities
def getStates(fileName):
	result = set()
	file = open(fileName, 'r')

	# Ignore first line
	file.readline()
	for line in file:
		result.add(line.split()[0].strip())
	file.close()
	return list(result)


# Generate interval from a MC transition probability
def generateInterval(value, parameters):
	global nbIntervals, nbParamsInIntervals

	if value in substitutions:
		for p in parameters:
			if p in substitutions[value]:
				nbParamsInIntervals += 1
				break
		return substitutions[value]

	value = float(value)
	# Try to generate an interval if percentIntervals > 0
	if percentIntervals > 0:
		if rd.random() < percentIntervals:
			nbIntervals += 1
			if rd.random() < percentParametrics:
				nbParamsInIntervals += 1
				lb = parameters[rd.randint(0, nbParameters-1)]
			else:
				lb = rd.uniform(0, value)

			if rd.random() < percentParametrics:
				nbParamsInIntervals += 1
				ub = parameters[rd.randint(0, nbParameters-1)]
			else:
				ub = rd.uniform(value, 1)
			value = "%s ; %s" % (lb, ub)

	# Else try to generate a parameter
	elif rd.random() < percentParametrics:
		value = parameters[rd.randint(0, nbParameters-1)]

	return str(value)


# Generate transitions with parametric intervals
def getTransitionsWithParametricIntervals(fileName):
	transitions = []
	file = open(fileName, 'r')

	# Ignore first line
	file.readline()
	for line in file:
		tokens = line.strip().split()
		value = {}
		value['stateFrom'] = tokens[0]
		value['stateTo'] = tokens[1]
		value['probabilities'] = generateInterval(tokens[2], parameters)
		transitions.append(value)
	file.close()
	return transitions

pimc = PIMC()
states = getStates(fileName)
pimc.setStates(states)
pimc.setParameters(parameters)
transitions = getTransitionsWithParametricIntervals(fileName)
for transition in transitions:
	pimc.setProbabilityFromString(transition['stateFrom'], transition['stateTo'], transition['probabilities'])
if not(labelingFile):
	initialState, nbChildren = pimc.guessInitialState()
	initialState = str(initialState)
	statesLabeling = {}
else:
	initialState, statesLabeling = getInitialStatFromLabelFile(labelingFile)

# Generate pIMC
out.write("#nbStates          %s\n" % (nbStates))
out.write("#nbTransitions     %s\n" % (nbTransitions))
out.write("#probaInterval     %s\n" % (percentIntervals))
out.write("#probaParameter    %s\n" % (percentParametrics))
out.write("#nbIntervals       %s\n" % (nbIntervals))
out.write("#nbParameters      %s\n" % (nbParameters))
out.write("#nbParamInBounds   %s\n" % (nbParamsInIntervals))
out.write("#initialState      %s\n" % (initialState))

print(parameters)

out.write('Type: pIMC\n')
out.write('Nodes: %s\n' % (nbStates))
out.write('Parameters: %s\n' % (nbParameters))
for param in parameters:
	out.write('%s\n' % (param))
out.write('Labels:\n')
out.write('%s : %s\n' % (initialState, " ".join(statesLabeling[initialState])))
for state in sorted(states, key=int):
	if state != initialState:
		label = " ".join(statesLabeling[state]) if (state in statesLabeling) else ''
		out.write('%s : %s\n' % (state, label))

out.write('Edges:\n')
for transition in transitions:
	out.write("%s->%s | %s\n" % (transition['stateFrom'], transition['stateTo'], transition['probabilities']))
out.close()

print("pIMC exported in plain text format to file '%s'" % (args.o))