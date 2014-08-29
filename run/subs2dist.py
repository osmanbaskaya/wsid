#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""

"""

import sys
import re
from collections import defaultdict as dd

# add.v.1

dataset = sys.argv[1]
regex = re.compile('<((\w+\.\w)\.(\d+))>')

d = dd(list)
for line in sys.stdin:
    tt, tw, inst_id = regex.findall(line)[0]
    d[tw].append(line)

for tw, lines in d.iteritems():
    with open("%s/subs/%s" % (dataset, tw), 'w') as f:
        f.write(''.join(lines))
