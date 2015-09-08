#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import math
import numpy as np

def homogeneity(m):
    # m sense distribution matrix.
    # rows are clusters, columns are gold stardard.
    nrow, ncol = m.shape
    N = m.sum()

    # conditional part
    conditional_entropy = .0
    for i in xrange(nrow):
        for j in xrange(ncol):
            val = m[i,j]
            if val != 0:
                conditional_entropy -= (val / N) * math.log(val / m[i].sum())
                
    # total part
    total_entropy = .0
    for i in xrange(ncol):
        val = m.T[i].sum()
        if val != 0:
            total_entropy -= (val / N) * math.log(val / N)

    return 1 - (conditional_entropy / total_entropy)


def completeness(m):
    return homogeneity(m.T)


def vmeasure(m):
    h = homogeneity(m)
    c = completeness(m)
    return (2 * h * c) / (h + c)


def example():
    m = np.matrix([[10, 10, 15],[20, 50, 0], [1, 10, 60], [5, 0, 0]])
    print "Contingency Matrix: {}".format(m)
    print "-" * 50
    print "Homogeneity={:.3f}, Completeness={:.3f}, and V-Measure={:.3f}".format(homogeneity(m), completeness(m), vmeasure(m))

if __name__ == '__main__':
    example()

