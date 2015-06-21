#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""
This module provides some functionality related to S-CODE vectors
such as reading, vector concetanation and so on.
"""

from nlp_utils import fopen
from collections import defaultdict as dd
from collections import Counter, namedtuple
import numpy as np
import sys
import gzip


SubstituteDistribution = namedtuple('SubstituteDistribution',
                                    'substitute, probability')


def exclude_missing_subs_and_normalize(sub_probs, vectors):
    sub_probs = [e for e in sub_probs if e.substitute in vectors]
    total_prob = sum(e.probability for e in sub_probs)
    return [(e.substitute, e.probability / total_prob) for e in sub_probs]


def get_X(embeddings):
    return embeddings[0]


def get_Y(embeddings):
    if len(embeddings.keys()) >= 2:
        return embeddings[1]
    else:
        return embeddings[0]


def read_embedding_vectors(embedding_f, wordset=None, not_scode_f=False):
    """ word_set is a set that indicates the tokens to fetch
        from embedding file.
    """
    if not_scode_f:
        print >> sys.stderr, "INFO: %s not S-CODE Embedding" % embedding_f
    else:
        print >> sys.stderr, "INFO: %s S-CODE Embedding" % embedding_f

    assert isinstance(wordset, set) or wordset == None, "wordset should be a set"

    d = dd(lambda: dict())
    for line in fopen(embedding_f):
        line = line.split()
        if not_scode_f:
            typ = 0
            w = line[0]
            start = 1
            count = 1
        else:
            typ = int(line[0][0])
            w = line[0][2:]
            start = 2
            count = int(line[1])
        if wordset is None or w in wordset :
            d[typ][w] = (np.array(line[start:], dtype='float64'), count)
    for typ in d:
        print >> sys.stderr, "Total # of embeddings: %d for type: %d" % \
                             (len(d[typ]), typ)
    return d

def concat_XY(embedding_d, subs):
    d = dd(lambda : dict())
    for X, s in subs.viewitems():
        Xs = Counter(s)
        for Y, count in Xs.viewitems():
            d[X][Y] = (np.concatenate([embedding_d[0][X][0], embedding_d[1][Y][0]]), count)
    return d

def concat_XYbar(embedding_d, subs, dim=25):
    d = dict()
    for X, s in subs.viewitems():
        Y_bar = np.zeros(dim)
        Xs = Counter(s)
        for Y, count in Xs.viewitems():
            Y_bar += embedding_d[1][Y][0] * count
        Y_bar /= (Y_bar.dot(Y_bar) ** 0.5)
        d[X] = (np.concatenate(embedding_d[0][X][0], Y_bar), 1)
    return d


def concat_XYw(embedding_d1, embedding_d2, sub_vecs, target_word_strip_func=None):
    """ Combined embedding, weighted by substitute probabilities (i.e, Volkan's method) 
        original_X_embeddings indicates that sub_vecs target words and embeddings are matches.
        We need this because this method can concatenate embeddings that are not based on
        the data which we get substitute distributions.
    """

    func = target_word_strip_func

    to_return = []
    target_words = []

    dim = len(embedding_d2[embedding_d2.keys()[0]][0])# Y vectors dimensionality
    total_context_word_used = 0
    total_context_word = 0
    for target_word, sub_probs in sub_vecs:
        # make it namedtuple: (substitute, probability)
        sub_probs = map(SubstituteDistribution._make, sub_probs)
        t = target_word
        if func is not None:
            t = func(target_word)
        try:
            X = embedding_d1[t][0]  # [0] -> vector, [1] -> #of occurrences
        except KeyError:
            print >> sys.stderr, "no X embedding for %s" % t
            continue  # pass this on
        total_context_word += len(sub_probs)
        Y_bar = np.zeros(dim)
        sub_probs = exclude_missing_subs_and_normalize(sub_probs, embedding_d2)
        total_context_word_used += len(sub_probs)
        for sub, prob in sub_probs:
            try: 
                Y_bar += embedding_d2[sub][0] * prob
            except KeyError:
                print >> sys.stderr, "no Y embedding for %s" % sub
        to_return.append(np.concatenate((X, Y_bar)))
        target_words.append(target_word)
    print >> sys.stderr, "Ratio of used_context word and total context " \
                         "word: %f" % \
                         (total_context_word_used / float(total_context_word))
    return target_words, to_return


def write_vec(embedding_d, fn=None):
    f = sys.stdout
    if fn is not None:
        f = gzip.open(fn, 'w')
    for word, (vec, count) in embedding_d.viewitems():
        f.write("{}\t{}\t{}".format(word, count, "\t".join(map(str, vec))))

    if fn is not None:
        f.close()
