#h! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""

"""

import sys
from nlp_utils import fopen
from itertools import count

c = count(0)

dist_f = fopen(sys.argv[1])
inst_map = dict([(str(c.next()), line.strip()) for line in fopen(sys.argv[2]).readlines()])

for line in dist_f:
    line = line.split()
    print inst_map[line[0]],
    for i, val in enumerate(line[1:]):
        if i % 2 == 0:
            val = inst_map[val]
        print val,
    print
