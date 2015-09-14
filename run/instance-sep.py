#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""

"""

import sys
import re
from collections import defaultdict as dd

# add.v.1

path = sys.argv[1]
regex = re.compile('<((\w+\.\w)\.(\d+))>')  # for s10, s13

if path.startswith('s07-test'):
    regex = re.compile('<((\w+\.\w)\.(.*))>')  # for s10, s13
    print >> sys.stderr, regex

if path.startswith('onto-test'):
    regex = re.compile('<((\w+\.\w)\.on\.(.*))>')
    print >> sys.stderr,  regex.pattern

d = dd(list)
for line in sys.stdin:
    try:
        tt, tw, inst_id = regex.findall(line)[0]
        if path.startswith('onto-test'):
            L = line.split('\t')
            L[0] = "<%s.%s>" % (tw, inst_id)
            line = '\t'.join(L)
        d[tw].append(line)
    except IndexError:
        print line
        raise IndexError()
        

for tw, lines in d.iteritems():
    with open("%s/%s" % (path, tw), 'w') as f:
        f.write(''.join(lines))
