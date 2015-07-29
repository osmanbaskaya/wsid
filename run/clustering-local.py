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
from sklearn.cluster import DBSCAN, SpectralClustering
import numpy as np
from wsid_utils import prepare_logger
from nlp_utils import find_num_senses_of_each_word


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

    LOGGER.debug(
        "key_file: {}, weighted= {}".format(key_file, is_weighted))

    inputs = prepare_tw_input(input_files, is_weighted)
    run_test(inputs, key_file)
    run_with_gold_k_vals(inputs, key_file)


def run_test(inputs, key_file):
    clustering_algorithms = []

    # Spectral Clustering
    num_of_clusters = (2, 4, 5, 6, 8, 10, 11)
    group = []
    for k in num_of_clusters:
        spectral = SpectralClustering(n_clusters=k, eigen_solver='arpack',
                                      affinity='nearest_neighbors',
                                      random_state=42,
                                      n_init=32)
        group.append(('Spectral_k=%d,' 'affinity=nearest_neighbors' %
                      k, spectral))

    clustering_algorithms.append(group)
    group = []
    for k in num_of_clusters:
        spectral = SpectralClustering(n_clusters=k, eigen_solver='arpack',
                                      affinity='rbf',
                                      random_state=42,
                                      n_init=32)
        group.append(('Spectral_k=%d,' 'affinity=rbf' % k, spectral))

    clustering_algorithms.append(group)

    # DBSCAN
    epsilons = [.001, .003, 0.01, 0.1, 0.15, 0.17, .2, .5]
    group = []
    for eps in epsilons:
        dbscan = DBSCAN(eps=eps)
        group.append(('DBSCAN_eps=%.5f' % eps, dbscan))

    clustering_algorithms.append(group)
    for group in clustering_algorithms:
        for name, algorithm in group:
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


def run_with_gold_k_vals(inputs, key_file):
    sense_dict = find_num_senses_of_each_word(key_file)
    algorithms = (("Spectral_k=gold,affinity=nearest_neighbors", SpectralClustering,
                   dict(eigen_solver='arpack', affinity='nearest_neighbors',
                        random_state=42, n_init=32)),
                  ("Spectral_k=gold,affinity=rbf", SpectralClustering,
                   dict(eigen_solver='arpack', affinity='rbf',
                        random_state=42, n_init=32)))
    for name, cls, kwargs in algorithms:
        all_preds = []
        LOGGER.debug("Running gold with following: %s %s", name, kwargs)
        for fn in sorted(inputs):
            algorithm = cls(n_clusters=sense_dict[fn], **kwargs)
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
    parser.add_argument('--log-level', default='info')
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
