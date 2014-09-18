#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"


import sys
import random

n = int(sys.argv[1]) # number of substitutes
s = int(sys.argv[2]) # seed

random.seed(s)

for line in sys.stdin:
    tokens = line.split()
    for i in xrange(n):
        total = 0
        for j in range(1, len(tokens), 2):
            tok, p = tokens[j], 10 ** float(tokens[j+1])
            total += p
            if total * random.random() <= p:
                sub = tok
        print "{}\t{}".format(tokens[0], sub)
