#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""
Script that calculate absolute difference between different systems"
Example: python absolute-diff.py 3 s13-test-globalcontext-svm-scores.txt s13-test-glove-svm-scores.txt s13-test-multilingual-svm-scores.txt s13-test-orig-XYw-svm-scores.txt
"""

import sys
from itertools import combinations, izip
import numpy as np

score_field = int(sys.argv[1]) # indicate the score field
file_comb = list(combinations(sys.argv[2:], 2))
score_files = map(lambda f: open(f).readlines(), sys.argv[2:])
score_lists = map(lambda L: map(lambda line: float(line.split()[score_field]), L), score_files)
score_lists = map(np.array, score_lists)
score_comb = list(combinations(score_lists, 2))

for (f1, f2), (score1, score2) in izip(file_comb, score_comb):
    print "%s\t%s\t%f" % (f1, f2, sum(abs(score1-score2)) / len(score1))
