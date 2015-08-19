#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import re
import sys

REGEX = re.compile('<((\w+\.\w)\.\d+)>')

for line in sys.stdin:
    s = REGEX.search(line)
    if s:
        sense = line.split()[-1]
        instance_id, tw = s.groups()
        print '%s %s %s.%s/1' % (tw, instance_id, tw, sense)
