#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import sys
from nlp_utils import fopen
from random import randint

test_f = sys.argv[1]
num_of_sense = int(sys.argv[2])

for line in fopen(test_f):
    tw, inst_id = line.split()[:2]
    print "{} {} induced-{}-{}/1.0".format(tw, inst_id, tw, randint(1, num_of_sense))
