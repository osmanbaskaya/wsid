#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""
Concatenation of the target word's and the sums of its substitutes' embeddings. After
adding all substitutes' embeddings, normalization is proceeded.

In the thesis, this is named as XY_v with bar. 

"""

import sys
from nlp_utils import fopen
from collections import defaultdict as dd
import numpy as np

scode_f = fopen(sys.argv[1]) # scode output
pairs_f = fopen(sys.argv[2]) # pairs file (wordsub output)

pairs = dd(lambda: dd(int))
substitutes = set() # all substitutes that any X have

for line in pairs_f:
    X, Y = line.split()
    pairs[X][Y] += 1
    substitutes.add(Y)

print >> sys.stderr, "pairs are read."

sc_vectors = dict()
for i, line in enumerate(scode_f):
    line = line.split()
    w = line[0][2:]
    if line[0].startswith("0:") or w in substitutes:
        sc_vectors[w] = np.array(line[2:], dtype="float64")

print >> sys.stderr, "scode vectors are read."

w = sc_vectors.keys()[0] # take an arbitrary key to obtain dimension
dimension = sc_vectors[w].shape[0]
for X, d in pairs.iteritems():
    Y_bar = np.zeros(dimension)
    for Y, count in d.iteritems():
        Y_bar += count * sc_vectors[Y]
    Y_bar /= (Y_bar.dot(Y_bar) ** 0.5)
    print "{0}\t1\t{1}\t{2}".format(X, '\t'.join(map(str, sc_vectors[X])), 
                                 '\t'.join(map(str, Y_bar)))

print >> sys.stderr, "concetanation is done."
