#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import sys
from nlp_utils import fopen
from random import randint
from collections import defaultdict as dd

test_f = sys.argv[1]

senses = dd(list)
instances = dd(list)
observed_senses = set()
for line in fopen(test_f):
    tw, inst_id, sense = line.split()
    instances[tw].append(inst_id)
    if sense not in observed_senses:
        senses[tw].append(sense)
        observed_senses.add(sense)

for tw in sorted(instances.keys()):
    n = len(senses[tw])
    for instance in instances[tw]:
        print "%s %s induced-%s-%d/1.0" % (tw, instance, tw, randint(0, n-1))
