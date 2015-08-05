__author__ = 'thorn'
from sklearn.cluster import SpectralClustering, DBSCAN
from hyperopt import hp
from sklearn.metrics.pairwise import pairwise_distances
from functools import partial

""" Module for algorithm search spaces """


SEARCH_SPACES = {
    'spectralclustering': hp.choice("spectral-type", [
                      {'n_clusters': hp.choice('n_clusters', range(2, 12)),
                       'n_neighbors': hp.choice('n_neighbors', range(2, 20)),
                       'affinity': 'nearest_neighbors',
                       "cls": SpectralClustering,
                       'random_state': 42},
                      {'gamma': hp.lognormal('gamma', 0, 1),
                       'affinity': 'rbf',
                       "cls": SpectralClustering,
                       'random_state': 42}
                  ]),

    'dbscan': hp.choice('dbscan',
        [{'min_samples': hp.choice('min_samples', range(2, 20)),
         'eps': hp.uniform('eps', 0.001, 5),
         'cls': DBSCAN,
         'metric':
             hp.choice('metric', map(lambda x: partial(pairwise_distances,
                                                       metric=x),
                           ['cosine', 'euclidean']))}])
    }


def get_search_space_by_algorithm(algorithm_name):
    try:
        return SEARCH_SPACES[algorithm_name]
    except KeyError:
        raise ValueError('No search space for "%s"' % algorithm_name)

