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

import os
import sys
import json
import resource
import threading
import fractions
import re
import subprocess

def isInstance(variable, clazz):
    if (not isinstance(variable, clazz)):
        raise TypeError('Instance of %s insted of %s.' % (type(variable), clazz))
        
def isType(variable, tyype):
    if (type(variable) != tyype):
        raise TypeError('Variable with type %s insted of %s.' % (type(variable), tyype))
        
def isList(variable):
    return type(variable) is list

def isDict(variable):
	return type(variable) is dict

def toList(variable):
    return variable if isList(variable) else [variable]

 
def powerset(seq):
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]]+item
            yield item

def getPimcPylibDirectory():
    return os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + os.sep + ".." + os.sep + "..") + os.sep

def getConfigIniLocation():
	return getPimcPylibDirectory() + "config.ini"

def getConfigIni():
    configFile = open(getConfigIniLocation(), "r")
    result = json.load(configFile)
    configFile.close()
    return result

def printTitle(message, size=70, stdout=sys.stdout):
    title = "=" * int(((size - len(message) - 2)/2)) + " " + message + " "
    stdout.write((title + (size - len(title)) * "=") + '\n')

def printInfo(name, value, size=25):
    print("c %s %s" % (name.ljust(size), value))

def exit(status=0):
	sys.stdout.flush()
	sys.stderr.flush()
	os._exit(status)

printRU = False
memoryLimit = 0
timeLimit = 0
def printResourceUsage():
	global printRU, memoryLimit, timeLimit
	if printRU:
		threading.Timer(2.0, printResourceUsage).start()
		usage = resource.getrusage(resource.RUSAGE_SELF)

		# Get time in sec. and memory used in Mb
		userTime = usage.ru_utime
		systemTime = usage.ru_stime
		memoryUsed = usage.ru_maxrss / (1024**2)
		print("UserTime: %.2f - SystemTime: %.2f - Memory: %sMb" % (userTime, systemTime, memoryUsed))
		if memoryUsed > memoryLimit:
			print("Memory limit of %sMb reached " % memoryLimit)
			exit(1)
		if userTime + systemTime > timeLimit:
			print("Time limit of %ssec. reached." % timeLimit)
			exit(1)

def startPrintResourceUsage():
	global printRU, memoryLimit, timeLimit
	if (memoryLimit == 0):
		try:
			config = getConfigIni()
			if not("memory_limit" in config):
				raise Exception("Missing key 'memory_limit' in config.ini.")
			if not("time_limit" in config):
				raise Exception("Missing key 'time_limit' in config.ini.")
			memoryLimit = int(config['memory_limit'])
			timeLimit = int(config['time_limit'])
		except Exception as e:
			print("Please check your configuration file config.ini at %s" % (getConfigIniLocation()))
			print(e)
			exit(2)

	printRU = True
	printResourceUsage()

def endPrintResourceUsage():
	global printRU
	printRU = False

def scientificNotation2smtNumber(strNumber):
	result = strNumber
	if isinstance(strNumber, fractions.Fraction):
		return "(/ %s %s)" % (strNumber.numerator, strNumber.denominator)

	if "e" in strNumber:
		number = strNumber.split("e")
		assert(len(number) == 2)
		power = int(number[1])
		if "." in number[0]:
			numParts = number[0].split(".")
			intPart  = numParts[0]
			decPart  = numParts[1]
		else:
			intPart = number[0]
			decPart = "0"
		intPart = "0" if (len(intPart) == 0) else intPart
		assert(len(intPart) == 1)

		if power > 0:
			result = intPart + decPart[:power] + "." + decPart[power:]
		elif power < 0:
			result = "0." + ("0" * (-power - 1)) + intPart + decPart
		else:
			result = intPart + "." + decPart
	return result		
	

def string2smtNumber(strNumber):
	tokens = strNumber.split(" ")
	for i in range(len(tokens)):
		token = tokens[i]
		# Check if it is a number (possibly starting with '-')
		if token[0].isdigit() or (len(token) > 1 and tokens[0] == '-'and tokens[1].isdigit()):
			tokens[i] = scientificNotation2smtNumber(token)
	return " ".join(tokens)


# Source: https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
def multireplace(string, replacements):
    """
    Given a string and a replacement map, it returns the replaced string.
    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {value to find: value to replace}
    :rtype: str
    """
    # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    substrs = sorted(replacements, key=len, reverse=True)

    # Create a big OR regex that matches any of the substrings to replace
    regexp = re.compile('|'.join(map(re.escape, substrs)))

    # For each match, look up the new string in the replacements
    return regexp.sub(lambda match: replacements[match.group(0)], string)


def string2integer(string):
	try:
		values = string.split(".")
		# No decimal part
		if len(values) == 1:
			return int(string)

		# Test if decimal part equals to zero
		elif int(values[1]) == 0:
			return int(values[0])

		# More than one "." in the string representation
		else:
			return None

	# Catch errors when converting to int
	except:
		return None

def smtFraction2fraction(string):
	try:
		# removes '(' and ')' and characters and splits the string 
		values = re.sub('[\(\)]', '', string).split()
		return str(fractions.Fraction(string2integer(values[1]), string2integer(values[2])))
	except:
		if len(values) == 3:
			raise
		return None

def smtFraction2string(string):
	return str(smtFraction2fraction(string))


def removeBlanckLines(lines):
	result = []
	for line in lines:
		tmp = line.strip()
		if tmp:
			result.append(tmp)
	return result


def getPrismExe():
	PIMC_PYLIB_DIRECTORY = getPimcPylibDirectory()
	try:
		configIni = getConfigIni()
		if not("prism" in configIni):
			raise Exception("Missing key 'prism' in config.ini.")
		if not(os.path.isfile(configIni['prism'])):
			raise Exception("PRISM executable '%s' not found." % (configIni['prism']))
	except Exception as e:
		print("Please check your configuration file config.ini at %s" % (getConfigIniLocation()))
		print(e)
		exit(1)
	return configIni['prism']

def getTra2pimcExe():
	return os.path.dirname(os.path.realpath(__file__)) + "/mc2pimc.py"


def getTmpDir():
	return os.path.dirname(os.path.realpath(__file__)) + "/tmp"

def execute(cmd, stdout=None, stderr=None):
	process = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr)
	result = process.wait()