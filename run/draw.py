#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import numpy as np
import os
import re
from fnmatch import fnmatch

import matplotlib.pyplot as plt

from utils.evaluate import evaluate_wsi
from nlp_utils import evaluate_mean_average_perp_diff


def scale(arr, minimum, maximum):
    max_val, min_val = max(arr), min(arr)
    new_arr = []
    for e in arr:
        val = (e - min_val) / (max_val - min_val)
        val = val * (maximum - minimum) + minimum
        new_arr.append(val)
    return new_arr


dataset = sys.argv[1]
key_file = "{}.key".format(dataset)

pattern = 'wsid-wk-pos-based*-%s*' % dataset

d = {}
for dir in os.listdir('/tmp'):
    if fnmatch(dir, pattern):
        fn = os.path.join('/tmp', dir, 'system_file.txt')
        k =  int(re.search('k=(\d+)', fn).group(1))
        precision, recall, f1score = evaluate_wsi(key_file, fn)
        diff, avg_diff = evaluate_mean_average_perp_diff(key_file, fn)
        d[k] = [f1score, avg_diff]

diffs = []
f1scores = []

for k in sorted(d):
    f1score, diff = d[k]
    diffs.append(diff)
    f1scores.append(f1score)

#plt.axis([0, 6, 0, 20])
#x2, x, c = np.polyfit(x, y, 2)
#plt.plot(x, y, 'o')
f1scores = scale(f1scores, 100, 300)
print zip(f1scores, sorted(d))
colors = np.random.rand(len(d))
plt.scatter(sorted(d), diffs, s=f1scores, c=colors, alpha=0.5)
png_file = '%s-pos-based-perplexity-diff-over-k.png' % dataset
plt.ylabel('Avg. Perplexity Diff (System - Gold)')
plt.xlabel('# of clusters (k)')
plt.title('%s Perplexity Difference over # of clusters' % dataset)
plt.savefig(png_file)

print "%s created" % png_file
