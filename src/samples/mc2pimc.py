# Transition Matrix from PRISM to PIMC format
import random as rd
from networks import *

import argparse
parser = argparse.ArgumentParser("Translates a MC transition function into a PIMC")
parser.add_argument('file', help='Transition function file')
parser.add_argument('-init', help='initial state to consider', type=int, default=-1)
parser.add_argument('-o', help='output PIMC file', default='/dev/stdout')
parser.add_argument('-p', help='number of parameters', type=int, default='0')
parser.add_argument('-ri', help='probability to transform a probability to an interval (value between 0. and 1.)', type=float, default='0.')
parser.add_argument('-rp', help='probability to transform a bound of an interval to a parameter (value between 0. and 1.)', type=float, default='0.')
args = parser.parse_args()

fileName = args.file
file = open(fileName, 'r')
out = open(args.o, 'w')

# Parameters
nbStates, nbTransitions = (int(nb) for nb in file.readline().split())
initialState        = args.init
nbParameters        = args.p if args.p > 0 else 0
percentIntervals    = args.ri if (0 < args.ri and args.ri < 1) else 0
percentParametrics  = args.rp if (0 < args.rp and args.rp < 1) else 0
nbIntervals         = 0
nbParamsInIntervals = 0

# Generate parameters
parameters = []
prefix = ""
for i in range(0, nbParameters):
	if i % 26 == 0 and i > 0:
		prefix += "a"
	parameters.append(prefix + chr(ord('a') + (i % 26)))

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
def generateInterval(value):
	global nbIntervals, nbParamsInIntervals

	value = float(value)
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
		return "%s ; %s" % (lb, ub)

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
		value['probabilities'] = generateInterval(tokens[2])
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
if initialState == -1:
	initialState, nbChildren = pimc.guessInitialState()
initialState = str(initialState)

# Generate pIMC
out.write("#nbStates          %s\n" % (nbStates))
out.write("#nbTransitions     %s\n" % (nbTransitions))
out.write("#probaInterval     %s\n" % (percentIntervals))
out.write("#probaParameter    %s\n" % (percentParametrics))
out.write("#nbIntervals       %s\n" % (nbIntervals))
out.write("#nbParameters      %s\n" % (nbParameters))
out.write("#nbParamInBounds   %s\n" % (nbParamsInIntervals))
out.write("#initialState      %s\n" % (initialState))

out.write('Type: pIMC\n')
out.write('Nodes: %s\n' % (nbStates))
out.write('Parameters: %s\n' % (nbParameters))
for param in parameters:
	out.write('%s\n' % (param))
out.write('Labels:\n')
out.write('%s : %s\n' % (initialState, initialState))
for state in states:
	if state != initialState:
		out.write('%s : %s\n' % (state, state))

out.write('Edges:\n')
for transition in transitions:
	out.write("%s->%s | %s\n" % (transition['stateFrom'], transition['stateTo'], transition['probabilities']))
out.close()

print("pIMC exported in plain text format to file '%s'" % (args.o))