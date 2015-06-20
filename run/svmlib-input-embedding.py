#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

# Creating an input file for libsvm from embedding file in scode format

# S-CODE Format:
"""
<access.n.1>    1       0.114621        0.13825 -0.003325       -0.032303
-0.116092       -0.148589     -0.102534       0.054985        0.077873"""

import sys
from nlp_utils import read_semeval_key_file, fopen

fn = sys.argv[1]  # subs_file for instance_id
embedding_file = sys.argv[2]  # pre_input output
key_file = sys.argv[3]

instances = map(lambda s: s[1:-2], fopen(fn))

def label_transf(key_dict):
    d = dict()
    c = 1
    mapper = dict()
    for instance, sense in key_dict.iteritems():
        if sense not in mapper:
            mapper[sense] = c
            c += 1
        d[instance] = mapper[sense]
    return d

# sense into integer for svm
key_dict = label_transf(read_semeval_key_file(key_file))

max_index = -1
values = []
for line in fopen(embedding_file):
    line = line.split()[2:]
    values.append(dict(zip(xrange(1, len(line)+1), line)))

for i, d in enumerate(values):
    print key_dict[instances[i]],
    for column_number, val in d.iteritems():
        print "%d:%s" % (column_number, val),
    print
