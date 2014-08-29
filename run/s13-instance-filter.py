#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""

"""

import sys
import re
from nlp_utils import fopen

context_f = fopen(sys.argv[1])
gold_f = fopen(sys.argv[2])


gold_set = set()
regex = re.compile('<(\w+\.\w\.\d+)>')

for line in gold_f:
    gold_set.add(line.split()[1])

print >> sys.stderr, "gold set length:", len(gold_set)

for line in context_f:
    m = regex.search(line)
    if m is not None:
        if m.group(1) in gold_set:
            print line,
