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
import json
import resource
import threading

def isInstance(variable, clazz):
    if (not isinstance(variable, clazz)):
        raise TypeError('Instance of %s insted of %s.' % (type(variable), clazz))
        
def isType(variable, tyype):
    if (type(variable) != tyype):
        raise TypeError('Variable with type %s insted of %s.' % (type(variable), tyype))
        
def isList(variable):
    return type(variable) is list

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

def getConfigIni():
    configFile = open(getPimcPylibDirectory() + "config.ini", "r")
    result = json.load(configFile)
    configFile.close()
    return result

def printTitle(message, size=70):
    title = "=" * int(((size - len(message) - 2)/2)) + " " + message + " "
    print(title + (size - len(title)) * "=")

def printInfo(name, value, size=25):
    print("c %s %s" % (name.ljust(size), value))


printRU = False
def printResourceUsage():
	global printRU
	if printRU:
		threading.Timer(2.0, printResourceUsage).start()
		usage = resource.getrusage(resource.RUSAGE_SELF)

		# Memory used in Mb
		userTime = usage.ru_utime
		systemTime = usage.ru_stime
		memoryUsed = usage.ru_maxrss / (1024**2)
		print("UserTime: %.2f - SystemTime: %.2f - Memory: %sMb" % (userTime, systemTime, memoryUsed))
		if memoryUsed > 2*1024:
			os._exit(1)


def startPrintResourceUsage():
	global printRU
	printRU = True
	printResourceUsage()

def endPrintResourceUsage():
	global printRU
	printRU = False

def scientificNotation2smtNumber(strNumber):
	result = strNumber
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
	

def string2smtNumber(str):
	return scientificNotation2smtNumber(str)
