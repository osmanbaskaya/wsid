#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"

"""
After dists, this module create a key file using dists output.
test etmedim son editleri
"""

#TODO: It returns only one sense now. It may be more appropriate to return 
#      m number of sense with threshold t.

from optparse import OptionParser
import gzip, sys
from itertools import izip
from collections import defaultdict as dd
from operator import itemgetter

parser = OptionParser()
parser.add_option("-g", "--gold", dest="gold_file", default=None,
                  help="gold dataset file", metavar="GOLD")
parser.add_option("-t", "--type", dest="dtype", default=None,
        help="which type of dists output to be used: fastsub or scode", metavar="TYPE")
parser.add_option("-s", "--source_file", dest="source", default=None,
        help="knn file. Input file", metavar="SOURCE")
parser.add_option("-k", "--knn", dest="k", default=10,
        help="Number of neighbors will be considered", metavar="NUM_NEIGHBORS")
parser.add_option("-w", "--weight", dest="is_weighted", default=0,
        help="if 1 then weights will be considered to determined", metavar="WEIGHT")


def input_check(opts, mandatories):
    """ Making sure all mandatory options appeared. """ 
    run = True
    for m in mandatories:
        if not opts.__dict__[m]: 
            print >> sys.stderr, "mandatory option is missing: %s" % m
            run = False
    if not run:
        print >> sys.stderr
        parser.print_help()
        exit(-1)


def file_open(filename):
    if filename.endswith('.gz'):
        func = gzip.open 
    else:
        func = open
    return func(filename)


def gold_process(filename):
    """ Gold file preprocessor for Semeval 2013 Task 13 """
    dsense = dict()
    g = open(filename).readlines()
    for line in g:
        line = line.split()
        inst_id = line[1]
        senses = line[2:]
        # e.g: add.v: [(sense1, 4), (sense2, 2), ...]
        dsense[inst_id] = [(s.split('/')[0], int(s.split('/')[1])) for s in senses]

    return dsense

def calc_sense(dsense, neighbors, weights=None):
    d = dd(int)
    if weights is None:
        weights = [1] * len(neighbors)
    for n, w in izip(neighbors, weights):
        for neigh_sense, rating in dsense[n]:
            d[neigh_sense] += rating * w

    #TODO: only one sense return, need more?
    return sorted(d.iteritems(), key=itemgetter(1))[0]


def eval_knn(source, gold_file, k, is_weighted):

    #print k, is_weighted, gold_file
    #exit()
    
    dsense = gold_process(gold_file)
    source_lines = file_open(source).readlines()

    if not len(dsense.keys()) == len(source_lines):
        print >> sys.stderr, "lengths do not match", 
        print >> sys.stderr, len(source_lines), len(dsense.keys())
        print >> sys.stderr, source, gold_file, k, is_weighted
        exit(-1)

    for line in source_lines:
        line = line.split()
        curr_inst = line[0]
        neighbors = line[1::2]
        neighbors = neighbors[:k]
        weights = None
        if is_weighted:
            weights = map(float, line[2::2])
            weights = weights[:k]
            assert len(neighbors) == len(weights)
        pred_senses = calc_sense(dsense, neighbors, weights)
        # for printing: sense1/4
        strf = "{}/{} " * (len(pred_senses) / 2)
        #FIXME line[0] dogru olmayabilir check et.
        print line[0], curr_inst, strf.format(*pred_senses)

def main():

    (opts, args) = parser.parse_args() 
    mandatories = ['dtype', 'gold_file', 'source']
    input_check(opts, mandatories)

    gold_file = opts.gold_file
    k = int(opts.k)
    is_weighted = bool(int(opts.is_weighted))
    source = opts.source

    if opts.dtype in ['fastsub', 'scode']:
        eval_knn(source, gold_file, k, is_weighted)
    else:
        raise ValueError, "you need to give fastsub or scode input"

if __name__ == '__main__':
    main()


