#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 15:38:36 2016

@author: Anicet
"""

#from samples.modeler import *
from samples.readers import *
from samples.dot_modeler import *
from samples.solution import *
from samples.milp_modeler import *
from samples.smt_modeler import *
from samples.smt_translater import *

import sys
import argparse
import samples.utils


sys.setrecursionlimit(100000)

# -i <pimc_file> -o <output_file> [-r | -d] [-smt | -milp [-semitCont] | -dot <sol>] [-vmcai16]

parser = argparse.ArgumentParser("Existencial Consistency")
parser.add_argument('-i', metavar='<pimc_file>', help='input file containing the pIMC', required=True)
parser.add_argument('-o', metavar='<output_file>', help='output file for printing the translation', required=True)

parser.add_argument("-r", action = "store_true", dest='useFractions', help="use rational numbers")
parser.add_argument("-d", action = "store_false", dest='useFractions', help="use double/float numbers")
parser.add_argument("-smt", action = "store_true", help="perform MILP modeling", default=False)
parser.add_argument("-milp", action = "store_true", help="perform MILP modeling", default=False)
parser.add_argument('-semiCont', help='use semi-continuous variables', action="store_true", default=False)
parser.add_argument("-dot", action = "store_true", help="perform .dot  double/float numbers", default=False)
parser.add_argument('-sol', metavar='<labelling_file>', help='solution input file', default="")
parser.add_argument("-vmcai16", action = "store_true", default=False, help="use VMCAI16 modelling")
args = parser.parse_args()

file = args.i
dotFile = args.dot
solFile = args.sol

# Loadding pIMC
utils.printTitle("Loading pIMC")
utils.printInfo("input_pimc", file)
utils.printInfo("input_numbers", "rationals" if args.useFractions else "float")
networkType, pimc2 = TxtFileReader.read(file, useFractions=args.useFractions)
infos = pimc2.getInfos()
infosOrder = ['#states','#transitions','initialState',
              '#intervals','#parameters','#paramInBounds',
              'ratioIntervals','ratioParamInBounds']
for key in infosOrder:
    utils.printInfo(key, infos[key])

# Modelling
utils.printTitle("Modelling")
utils.printInfo("output_format", "smt" if (args.vmcai16 or args.smt) else "milp")
utils.printInfo("output_numbers", "float")
utils.printInfo("output_model", args.o)

if args.vmcai16:
    model = SmtTranslater.consistencyVMCAI16(pimc2, args.o)
elif args.smt:
    model = ModelerSMT.consistency(pimc2, args.o)
else:
    model = ModelerMILP.consistency(pimc2, args.semiCont, args.o)
infos = model.getInfos()
infosOrder = ['#variables','#constraints',
              '#booleanVars','#continuousVars','#semiContinuousVars']
for key in infosOrder:
    utils.printInfo(key, infos[key])

exit(0)


if solFile:
    solution = Solution.parse(solFile)
else:
    solution = None
DotModeler.export(pimc2, dotFile, solution)