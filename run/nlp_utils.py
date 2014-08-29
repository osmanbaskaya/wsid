#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import math
from collections import defaultdict as dd
from itertools import izip
import gzip
import fnmatch
import os

__author__ = "Osman Baskaya"

""" Utility functions that are used in experiments """

def fopen(filename):
    if filename.endswith('.gz'):
        func = gzip.open
    else:
        func = open
    return func(filename)

def find_files(topdir, pattern):
    for path, dirname, filelist in os.walk(topdir):
        for name in filelist:
            if fnmatch.fnmatch(name, pattern):
                yield os.path.join(path,name)

def calc_perp(X, weight=None):
    
    d = dd(int)
    if weight is None:
        weight = [1] * len(X)

    for tag, w in izip(X, weight):
        d[tag] += w

    total = sum(weight)
    entropy = .0
    for key in d.keys():
        p = d[key] / total
        entropy += -p * math.log(p, 2)
    return 2 ** entropy

def calc_perp_semeval(sense_list):
    # sense list = [['t.1/0.8723', 't.6/0.0851', 't.50/0.0213', 't.18/0.0213'], ...]
    senses = []
    weight = []
    for slist in sense_list:
        m = [s.split('/') for s in slist]
        for t in m:
            senses.append(t[0])
            if len(t) == 1:
                weight.append(1.)
            else:
                weight.append(float(t[1]))

    assert len(senses) == len(weight)
    return calc_perp(senses, weight)

def calc_perp_dict(d):
    # test etmedim
    entropy = 0.
    tt = [(key, len(val)) for key, val in d.iteritems()]
    total = sum([x[1] for x in tt])
    for i, j in tt:
        p = j / total
        entropy += -p * math.log(p, 2)
    return 2 ** entropy

def calc_perp_dict_graded(d):
    # test etmedim
    entropy = 0.
    tt = [(key, len(val)) for key, val in d.iteritems()]
    total = sum([x[1] for x in tt])
    for i, j in tt:
        p = j / total
        entropy += -p * math.log(p, 2)
    return 2 ** entropy
    
def traverse(o, tree_types=(list, tuple)):
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value):
                yield subvalue
    else:
        yield o

#a = [1, 1, 1, 2, 2, 2, 3, 3]
#b = ['a', 'a', 'a', 'b', 'b', 'b', 'c', 'c']
#print calc_perp(a)
#print calc_perp(b)

