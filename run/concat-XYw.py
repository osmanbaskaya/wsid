#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"

"""
Concatenation of the target word's and the each substitute's embeddings.
Volkan's method
"""

from itertools import izip
from fastsubs_utils import read_sub_vectors
from embedding_utils import read_embedding_vectors, concat_XYw, get_X, get_Y
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('x_embedding_file', metavar="X_EMBEDDING_FILE", type=str)
parser.add_argument('y_embedding_file', metavar="Y_EMBEDDING_FILE", type=str)
parser.add_argument('subs_file', metavar="SUBS_FILE", type=str)
parser.add_argument('--x-not-scode', action='store_true', default=False)
parser.add_argument('--y-not-scode', action='store_true', default=False)
parser.add_argument('--subs_embed_same', action='store_true', default=False)

args = parser.parse_args()

embedding_f1 = args.x_embedding_file
embedding_f2 = args.y_embedding_file
sub_f = args.subs_file   # sub file (we need it for weighting)
x_not_scode = args.x_not_scode
y_not_scode = args.y_not_scode

regex = re.compile("<(\w+)\.")
def func(target_word):
    return regex.match(target_word).group(1)

# if we use same embeddings, we don't need to provide strip func
if args.subs_embed_same:
    func = None

subs = read_sub_vectors(sub_f)
embeddingsX = get_X(read_embedding_vectors(embedding_f1, not_scode_f=x_not_scode))

embeddingsY = get_Y(read_embedding_vectors(embedding_f2, not_scode_f=y_not_scode))
tws, vectors = concat_XYw(embeddingsX, embeddingsY, subs, func)

for target_word, vector in izip(tws, vectors):
    print "%s\t1\t%s" % (target_word, '\t'.join(map(str, vector)))
