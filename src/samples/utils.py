# -*- coding: utf-8 -*-
"""
Created on Fri May 20 15:28:11 2016

@author: Anicet
"""

import json
import os

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

def powersetList(s):
    r = [[]]
    for e in s:
        #print "r: %-55r e: %r" % (r,e)
        r += [x+[e] for x in r]
    return r
 
def list_powerset(lst):
    # the power set of the empty set has one element, the empty set
    result = [[]]
    for x in lst:
        # for every additional element in our set
        # the power set consists of the subsets that don't
        # contain this element (just take the previous power set)
        # plus the subsets that do contain the element (use list
        # comprehension to add [x] onto everything in the
        # previous power set)
        result.extend([subset + [x] for subset in result])
    return result
 
# the above function in one statement
def list_powerset2(lst):
    return reduce(lambda result, x: result + [subset + [x] for subset in result],
                  lst, [[]])
 
def powersetSet(s):
    return frozenset(map(frozenset, list_powerset(list(s))))

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
