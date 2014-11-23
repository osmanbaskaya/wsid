#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import sys
from nlp_utils import read_semeval_key_file, fopen

fn = sys.argv[1]
norm_sub_file = sys.argv[2]  # pre_input output
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

key_dict = label_transf(read_semeval_key_file(key_file))  #  sense into integer for for svm

max_index = -1
values = []
for line in fopen(norm_sub_file):
    line = line.split()[1:]
    indices = map(int, line[0:-1:2])
    vals = line[1:len(line):2]
    values.append(dict(zip(indices, vals)))
    line_max_index = max(indices)
    if line_max_index > max_index:
        max_index = line_max_index

for i, d in enumerate(values):
    print key_dict[instances[i]],
    for j in xrange(1, max_index+1):
        print "%d:%s" % (j, d.get(j, 0)),
    print
