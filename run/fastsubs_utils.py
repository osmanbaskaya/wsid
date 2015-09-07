#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""

"""
import sys
from nlp_utils import fopen
from collections import defaultdict as dd

def read_sub_vectors(sub_f, wordset=None):
    """ word_set is a set that indicates the tokens to fetch
        from substitute file.
    """
    assert isinstance(wordset, set) or wordset is None, "wordset should be a set or None"
    to_return = []
    for line in fopen(sub_f):
        line = line.split()
        w = line[0] # 
        if wordset is None or w in wordset:
            unnormalized = map(lambda x: 10**(float(x)), line[2:-1:2])
            Z = sum(unnormalized)
            normalized = [e / Z for e in unnormalized]
            to_return.append((w, zip(line[1:-1:2], normalized)))
    
    return to_return

#read_sub_vectors('dummy.sub.gz', set(['fail.v', 'maintain.v']))
