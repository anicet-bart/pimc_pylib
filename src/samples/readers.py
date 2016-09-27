# -*- coding: utf-8 -*-
"""
Created on Fri May 20 15:26:00 2016

@author: Anicet
"""
from networks import MC, IMC, PIMC

class TxtFileReader(object):
                   
    @staticmethod
    def read(file, useFractions=False):   
        f = open(file, 'r')
        lines = f.readlines()        
        line = 0
        while (lines[line][0] == '#'):
            line += 1


        # Type: [MC|IMC|PIMC]
        networkType = TxtFileReader.getValueAfterKey(lines[line], 'Type: ').upper()
        networkType = "".join(networkType.split())
        if (networkType == 'MC'):
            result = MC()
        elif (networkType == 'MC'):
            result = IMC()
        else:
            result = PIMC(useFractions)
        line += 1

        # Nodes: <node> (one per line)
        nbNodes = int(TxtFileReader.getValueAfterKey(lines[line], 'Nodes: '))
        line += 1

        # Parameters: <number> 
        # <parameter> (onr per line)
        if networkType == 'PIMC':
            nbParameters = int(TxtFileReader.getValueAfterKey(lines[line], 'Parameters: '))
            line += 1
            result.setParameters([x.strip() for x in lines[line:line+nbParameters]])
            line += nbParameters
        
        # Labels: 
        # <node>:<label> (one per line)
        line += 1
        labels = {}
        for l in lines[line:line + nbNodes]:
            elts = l.split(':')
            labels[elts[0].strip()] = elts[1].strip()
        initialState = lines[line].split(':')[0].strip()
        result.setInitialState(initialState)
        result.setStates(labels.keys())
        result.setLabels(labels)
        if len(labels.keys()) != nbNodes:
            raise Exception("%d nodes declared and %d instanciated with labels." % (nbNodes, len(labels.keys())))
        line += nbNodes + 1
        
        # Edges:
        # <fromNode> -> <toNode> | <lowerBound> ; <upperBound> (one per line)
        for l in lines[line:]:
            elts = l.split('|')
            nodes = elts[0].split('->')
            nodeFrom = "".join(nodes[0].split())
            nodeTo = "".join(nodes[1].split())
            result.setProbabilityFromString(nodeFrom, nodeTo, elts[1])
        
        return networkType, result

    @staticmethod
    def getValueAfterKey(line, key):
        if line.startswith(key):
            return line[len(key):]
        return None
        