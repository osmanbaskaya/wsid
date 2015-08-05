#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
from hyperopt import fmin, tpe, STATUS_OK, Trials
import os
from utils.evaluate import evaluate_wsi
from itertools import cycle
import tempfile
from functools import partial
import logging

LOGGER = logging.getLogger(__name__)


def objective(inputs, key_file, kwargs):
    """The most general form of objective function. It takes all necessary
    parameters as arguments (even the algorithm's class) and evaluate the
    algorithm for given parameter set on the dataset given in
    `inputs` variable."""

    cls = kwargs.pop('cls')  # pop up the class of the algorithm
    algorithm = cls(**kwargs)
    precision, recall, f1score = process_wsi_system(algorithm, inputs, key_file)
    to_return = {'loss': 1 - f1score, 'status': STATUS_OK, 'score': f1score,
                 'eval_time': time.time()}
    to_return.update(kwargs)  # add parameters to optimize.
    return to_return


def process_wsi_system(algorithm, inputs, key_file):
    """ The method provides an evaluation process of an algorithm given WSI
    dataset. As input it takes dictionary consisted of matrices. Each matrix
    contains the representation of all instances observed in the test set."""

    name = algorithm.__class__.__name__
    all_preds = []
    for fn in sorted(inputs):
        basename = os.path.basename(fn)
        X, tws = inputs[fn]
        preds = algorithm.fit_predict(X).tolist()
        all_preds.extend(map(lambda e: "%s %s %s.%s/1" %
                                       (e[0], e[1], e[0], e[2]),
                             zip(cycle([basename]), tws, preds)))

    f = tempfile.NamedTemporaryFile('w', prefix='wsid-%s-local' % name)
    f.write('\n'.join(all_preds))
    precision, recall, f1score = evaluate_wsi(key_file, f.name)
    LOGGER.debug("{}\t{}\t{}\t{}".format(f.name, precision, recall, f1score))
    return precision, recall, f1score


def optimize(obj_function, inputs, key_file, space, max_eval):

    trials = Trials()
    f = partial(obj_function, inputs, key_file)
    best = fmin(f, space=space, algo=tpe.suggest, max_evals=max_eval,
                trials=trials)
    LOGGER.info("{}\t{}".format(best, 1 - min(trials.losses())))

    # Some other information:
    # print trials.trials
    # print trials.results
    # print trials.losses()
    # print trials.statuses()
