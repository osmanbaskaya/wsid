#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import math
from collections import Counter, defaultdict as dd
from data_load import SemevalKeyLoader
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


def calc_perp_for_dataset(fn):
    f = fopen(fn)
    d = dd(list)
    for line in f:
        tw, inst_id, sense = line.split()
        d[tw].append(sense)

    perps = []
    for tw in d:
        entropy = .0
        counts = Counter(d[tw])
        total = float(sum(counts.values()))
        for sense, c in counts.iteritems():
            p = c / total
            entropy += -p * math.log(p, 2)
        perp = 2 ** entropy
        print "%s: perp = %f" % (tw, 2 ** perp)
        perps.append((perp, total))

    total_perp = 0
    num_inst = 0
    for perp, count in perps:
        total_perp += perp * count
        num_inst += count

    print total_perp, num_inst
    print "Avg. Entropy for %s: %f" % (fn, total_perp / num_inst)


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
    # Not tested
    entropy = 0.
    tt = [(key, len(val)) for key, val in d.iteritems()]
    total = sum([x[1] for x in tt])
    for i, j in tt:
        p = j / total
        entropy += -p * math.log(p, 2)
    return 2 ** entropy


def calc_perp_dict_graded(d):
    # Not tested
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


def read_semeval_key_file(fn):
    d = dict()
    for line in fopen(fn):
        line = line.split()
        d[line[1]] = line[2].split('::')[0]
    return d


def find_num_senses_of_each_word(key_file):
    d = dd(set)
    with open(key_file) as f:
        for line in f:
            tw, inst_id, sense = line.split()
            d[tw].add(sense)

    return dict(map(lambda tword: (tword, len(d[tword])), d))


def calc_perp_of_words(keyfile):
    # keyfile: loaded by SemevalKeyLoader
    perplexities = {}
    for word in keyfile:
        entropy = .0
        senses = Counter(keyfile[word][instance][0][0] for instance in keyfile[word])
        total = float(sum(senses.values()))
        for count in senses.values():
            p = count / total
            entropy += -p * math.log(p, 2)
        perplexities[word] = 2 ** entropy

    return perplexities


def evaluate_mean_average_perp_diff(key_file, system_file):
    loader = SemevalKeyLoader()
    gold = loader.read_keyfile(key_file)
    system = loader.read_keyfile(system_file)
    gold_perp = calc_perp_of_words(gold)
    system_perp = calc_perp_of_words(system)
    diff = .0
    for word in gold_perp:
        #diff += abs(gold_perp[word] - system_perp[word])
        diff +=  system_perp[word] - gold_perp[word] 

    return diff, diff / len(gold_perp)

#a = [1, 1, 1, 2, 2, 2, 3, 3]
#b = ['a', 'a', 'a', 'b', 'b', 'b', 'c', 'c']
#print calc_perp(a)
#print calc_perp(b)

