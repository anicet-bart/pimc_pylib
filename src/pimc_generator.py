#!/usr/bin/python

# PRISM file to pIMC file
import json
import argparse
import itertools
import os
import subprocess

parser = argparse.ArgumentParser(description="Translate PRISM file into PIMC files")
parser.add_argument('c', metavar='<config_file>', help='Configuration file for PIMC generation (in JSON format)')
parser.add_argument('-o', metavar='<output_directory>', help='output directory', default="")
args = parser.parse_args()


def execute(cmd):
	process = subprocess.Popen(cmd, shell=True)
	process.wait()	


def getInitialStatFromLabelFile(prismLabelFile):
	file = open(prismLabelFile)
	# Read first line to get the key associated to the initial state
	# 0="init" 1="deadlock"
	header = file.readline()
	header = {x.split("=")[0]:x.split("=")[1] for x in header.split()}
	keyInitialState = ""
	for key in header:
		if header[key] == '\"init\"':
			keyInitialState = key
	assert(keyInitialState != "")

	for line in file:
		line = line.strip()
		if line.endswith(keyInitialState):
			return int(line.split(":")[0])


configFile = open(args.c, 'r')
config = json.load(configFile)
configFile.close()

# Configuration
PRISM    = '/Users/anicetbart/Documents/These/xp_pimc/prism-4.3.1-osx64/bin/prism'
TRA2PIMC = os.path.dirname(os.path.realpath(__file__)) + "/samples/mc2pimc.py"
outdir = args.o
if outdir == "":
    outdir = os.path.dirname(os.path.realpath(__file__)) + "/../data/generator/outputs/"

expectedKeys = ['instance', 'prismConstants', 'nbParams', 'probaInterval', 'probaParameter']
for key in expectedKeys:
	if not(key in config):
		raise Exception('Missing key "%s" in the configuration file <config>.' % (key))

instanceName = os.path.splitext(os.path.basename(config['instance']))[0]
constantNames  = config['prismConstants'].keys()
constantValues = [config['prismConstants'][c] for c in constantNames]
paramValues = [
	[str(i) for i in config['nbParams']], 
	[str(i) for i in config['probaInterval']], 
	[str(i) for i in config['probaParameter']]]


# PRIMS command
pimcs = []
for constants in itertools.product(*constantValues):
	consts  = ["%s_%s" % (constantNames[i], constants[i]) for i in range(len(constants))]
	benchname = outdir + os.sep + instanceName + "_" + "_".join(consts)
	trafile = benchname + ".tra"

	consts  = ["-const %s=%s" % (constantNames[i], constants[i]) for i in range(len(constants))]
	cmd     = "%s %s %s -exportmodel %s" % (PRISM, config['instance'], " ".join(consts), trafile + ",lab")
	print(cmd)
	execute(cmd)

	initialState = getInitialStatFromLabelFile(benchname + ".lab")

	# TRA2PIMC 
	for params in itertools.product(*paramValues):
		pimcfile = benchname + "_" + "_".join(params) + ".pimc"
		cmd = "python %s %s -o %s -p %s -ri %s -rp %s -init %s" % (TRA2PIMC, trafile, pimcfile, params[0], params[1], params[2], initialState)
		print(cmd)
		execute(cmd)
		pimcs.append(pimcfile)

print("Generated PIMCs:")
for file in pimcs:
    print(file)