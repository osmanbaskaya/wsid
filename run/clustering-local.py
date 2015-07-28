"""
Experiments on different clustering algorithms.
This file contains the locale based approach.
"""

import argparse
import os
from subprocess import check_output
import logging
import tempfile
from itertools import cycle
from sklearn.cluster import DBSCAN, SpectralClustering, KMeans
import numpy as np
from wsid_utils import prepare_logger


SCORER = '/usr/bin/java -jar ../bin/ss.jar -s'
LOGGER = None


def enable_logging(log_level):
    global LOGGER
    prepare_logger(log_level)
    LOGGER = logging.getLogger(__name__)


def get_input_matrix(fn, dim, is_weighted):
    if is_weighted:
        usecols = range(2, dim)
    else:
        usecols = range(1, dim)
    matrix = np.loadtxt(fn, usecols=usecols)
    tw_list = np.loadtxt(fn, usecols=(0,), dtype='str').tolist()
    tw_list = [i[1:-1] for i in tw_list]  # <add.v.13> | removing < and >
    return matrix, tw_list


def prepare_tw_input(input_files, is_weighted):
    dim = len(open(input_files[0]).readline().split())
    d = {}
    for fn in input_files:
        basename = os.path.basename(fn)
        matrix, tw_list = get_input_matrix(fn, dim, is_weighted)
        d[basename] = (matrix, tw_list)
    return d


def run(input_files, key_file, is_weighted):
    clustering_algorithms = []

    LOGGER.debug(
        "key_file: {}, weighted= {}".format(key_file, is_weighted))

    inputs = prepare_tw_input(input_files, is_weighted)

    # Spectral Clustering
    num_of_clusters = (2, 4, 5, 6, 8, 10, 12, 14)
    for k in num_of_clusters:
        spectral = SpectralClustering(n_clusters=k, eigen_solver='arpack',
                                      affinity='nearest_neighbors')
        clustering_algorithms.append(('Spectral_k=%d' % k, spectral))

    # DBSCAN
    epsilons = [.2, .5, 1., 2, 3, 4]
    for eps in epsilons:
        dbscan = DBSCAN(eps=eps)
        clustering_algorithms.append(('DBSCAN_eps=%.1f' % eps, dbscan))

    for name, algorithm in clustering_algorithms:
        all_preds = []
        for fn in sorted(inputs):
            basename = os.path.basename(fn)
            X, tws = inputs[fn]
            preds = algorithm.fit_predict(X).tolist()
            all_preds.extend(map(lambda e: "%s %s %s.%s/1" %
                                           (e[0], e[1], e[0], e[2]),
                                 zip(cycle([basename]), tws, preds)))
        f = tempfile.NamedTemporaryFile('w', prefix='wsid-%s_' % name)
        f.write('\n'.join(all_preds))
        LOGGER.debug('Algorithm: %s AnswerFile: %s', name, f.name)
        s = evaluate(key_file, f.name)
        print "%s\t%s\t%s" % (key_file.split('.')[0], name, s.split()[-1])
        print


def evaluate(key_file, filename):
    score = check_output('{} {} {} | tail -2 | head -1'
                         .format(SCORER, key_file, filename), shell=True)
    return score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--is-weighted', action='store_false', default=True,
                        help="Whether input contains weights column as #2")
    parser.add_argument('--key-file', required=True)
    parser.add_argument('--log-level', required=True)
    parser.add_argument('--input', nargs='+', required=True,
                        help="System's representation file(s)")

    args = parser.parse_args()

    enable_logging(args.log_level)

    kwargs = dict(key_file=args.key_file,
                  is_weighted=args.is_weighted,
                  input_files=args.input)

    run(**kwargs)


if __name__ == '__main__':
    main()
