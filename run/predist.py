#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""
Module creates input for dist to use it. It also creates instance file that contains the mapping for dists
results and the instances.
"""

import sys
from itertools import chain
import gzip


instance_file_created = False
if len(sys.argv) == 2:
    instance_f = gzip.open(sys.argv[1], 'w')
    instance_file_created = True


for line in sys.stdin:
    line = line.split()
    m = len(line)
    if instance_file_created:
        print >> instance_f, line[0]
    t = zip(range(m-2), map(float, line[2:]))
    values = sorted(t, key=lambda x: x[1], reverse=True)
    print (m-2) * 2, 
    print " ".join(map(str, chain.from_iterable(values)))

if instance_file_created:
    instance_f.close()



