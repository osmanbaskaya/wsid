#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import sys
from nlp_utils import fopen
from collections import Counter, defaultdict as dd

test_f = sys.argv[1]

senses = dd(list)
instances = dd(list)
for line in fopen(test_f):
    tw, inst_id, sense = line.split()
    instances[tw].append(inst_id)
    senses[tw].append(sense)

for tw in sorted(instances.keys()):
    tw_senses = Counter(senses[tw])
    mfs = max(tw_senses, key=lambda sense: tw_senses[sense])
    for instance in instances[tw]:
        print "%s %s %s" % (tw, instance, mfs)
