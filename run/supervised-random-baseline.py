#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import sys
from nlp_utils import fopen
from random import randint, shuffle
from collections import defaultdict as dd
from itertools import izip

test_f = sys.argv[1]
method = sys.argv[2]  # shuffled / weighted

senses = dd(list)
instances = dd(list)
for line in fopen(test_f):
    tw, inst_id, sense = line.split()
    instances[tw].append(inst_id)
    senses[tw].append(sense)

if method == 'weighted':
    for tw in sorted(instances.keys()):
        n = len(senses[tw])
        for instance in instances[tw]:
            print "%s %s %s" % (tw, instance, senses[tw][randint(0, n-1)])
elif method == 'shuffled':
    for tw in sorted(instances.keys()):
        shuffle(senses[tw])
        for instance, sense in izip(instances[tw], senses[tw]):
            print "%s %s %s" % (tw, instance, sense)
else:
    print "Need to call %s test_data shuffled/weigted" % sys.argv[0]
