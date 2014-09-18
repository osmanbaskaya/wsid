#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""
kNN implementation

input (sys.stdin): dist file (dists)
k = # of neighbors that need to be considered
"""

import sys
from nlp_utils import fopen
from collections import defaultdict as dd
import os

#def grouper(n, iterable, fillvalue=None):
    #args = [iter(iterable)] * n
    #return izip_longest(fillvalue=fillvalue, *args)

def majority_voting(neighbors):
    senses = dd(int)
    for neighbor, _ in neighbors:
        key = keys[neighbor]
        senses[key] += 1
    return max(senses, key=lambda x: senses[x])

def min_avg_dist(neighbors):
    senses = dd(list)
    for neighbor, dist in neighbors:
        key = keys[neighbor]
        senses[key].append(float(dist))
    return min(senses, key=lambda x: sum(senses[x]) / len(senses[x]))


def predict(inst, neighbors, evaluation):
    if evaluation == 'majority_voting':
        return majority_voting(neighbors)
    elif evaluation == 'min_avg_dist':
        return min_avg_dist(neighbors)
    else:
        raise AttributeError, "No evaluation setup named %s defined" % evaluation

k = int(sys.argv[1])
eval_metric = sys.argv[2]
input_f = fopen(sys.argv[3])
gold_f = fopen(sys.argv[4])

keys = dict() # building the instance_id -> sense dictionary
for line in gold_f:
    word, instance_id, sense = line.split()
    if not (instance_id.startswith("<") and instance_id.endswith(">")):
        instance_id = "<%s>" % instance_id
    keys[instance_id] = sense

d = dict()
preds = []
for line in input_f:
    line = line.split()
    inst = line[0]
    neighbors = zip(line[1:k*2+1:2], line[2:k*2+1:2])
    pred_sense = predict(inst, neighbors, eval_metric)
    actual_sense = keys[inst]
    preds.append(pred_sense == actual_sense)

print "%s - Accuracy\t%.5f\tk = %d" % (os.path.basename(input_f.name), sum(preds) / float(len(preds)), k)



