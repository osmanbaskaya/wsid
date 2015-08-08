import logging
from subprocess import check_output
from operator import itemgetter
from itertools import izip
from collections import defaultdict as dd
from sklearn.cross_validation import StratifiedKFold, KFold
from nlp_utils import calc_perp
from data_load import SemevalKeyLoader

SCORER = '/usr/bin/java -jar ../bin/ss.jar -s'
LOGGER = logging.getLogger(__name__)


def evaluate_wsi(key_file, filename):
    """Agirre's single sense WSI system evaluation is used.  Details:
    http://www.aclweb.org/anthology/S07-1002"""

    score = check_output('{} {} {} | tail -2 | head -1'
                         .format(SCORER, key_file, filename), shell=True)
    _, precision, recall, f1score = score.split()
    return map(float, [precision, recall, f1score])


def any_chunk_is_empty(chunks):
    is_empty = False
    for train, test in chunks:
        if len(test) == 0 or len(train) == 0:
            is_empty = True

    return is_empty


def _get_train_and_test_inst(answers, instances, n_folds):
    # Try StratifiedKFold first until n_folds = 2. Still you can't split the
    # data balanced, then KFold.

    train_test_splits = []
    chunks = None

    cls = "StratifiedKFold"
    n_fold = n_folds

    # Try StratifiedKFold until n_folds = 2.
    # No shuffling. We'll need the order below when indexing with itemgetter.
    for i in xrange(n_folds, 1, -1):
        chunks = StratifiedKFold(answers, n_folds=i, shuffle=False,
                                 random_state=42)
        if any_chunk_is_empty(chunks):
            chunks = None
        else:
            n_fold = i
            break

    # If chunks is still not defined then KFold.
    if chunks is None:
        chunks = KFold(len(answers), n_folds=n_folds, shuffle=False,
                       random_state=42)
        cls = "KFold"

    for train, test in chunks:
        train_instances = itemgetter(*train)(instances)
        test_instances = itemgetter(*test)(instances)

        if isinstance(test_instances, int):
            test_set = (itemgetter(*test)(instances),)
        else:
            test_set = itemgetter(*test)(instances)

        if isinstance(train_instances, int):
            train_set = (itemgetter(*train)(instances),)
        else:
            train_set = itemgetter(*train)(instances)

        train_test_splits.append((train_set, test_set))

    LOGGER.debug("Data splitted %d with %s", n_fold, cls)
    print "Data splitted %d with %s" % (n_fold, cls)
    return train_test_splits


def get_max_sense(instance_dict, instances=None):
    """
    Return a list of senses with maximum graded sense score.

    >>> d = {1: [('s1', 9), ('s2', 8.9), ('s6', 12)], 2: [('s2', 1), ('s3', 7)]}
    >>> get_max_sense(d)
    ['s6', 's3']
    >>> get_max_sense(d, [1])
    ['s6']
    """

    if instances is not None:
        senses = []
        for i in instances:
            senses.append(max(instance_dict[i], key=lambda x: x[1])[0])
    else:
        senses = [max(e, key=lambda x: x[1])[0] for e in instance_dict.values()]

    return senses


def get_mapped_senses(gold_instance_dict, sys_instance_dict, train_test_splits):
    mapped_senses = []
    for train, test in train_test_splits:

        gold_train_senses = get_max_sense(gold_instance_dict, train)
        sys_train_senses = get_max_sense(sys_instance_dict, train)

        d = dd(lambda: dd(int))
        # build the sense mapping matrix. Each system-gold occurrence equals
        # 1 point.
        for g_sense, s_sense in izip(gold_train_senses, sys_train_senses):
            d[s_sense][g_sense] += 1

        # Make majority vote among gold senses for each system sense occurred
        # together with the same instances.
        mapping = dict([(s_sense, max(d[s_sense], key=lambda e: e[1])) for
                              s_sense in d])
        LOGGER.debug("Mapping: %s", mapping)

        # Map test senses. If mapping doesn't contain any sense mapping for
        # particular system sense; skip it.
        sys_test_senses = get_max_sense(sys_instance_dict, test)
        mapped_test_chunk = dict([(instance, mapping[s_sense]) for instance, s_sense
                             in izip(test, sys_test_senses) if s_sense in mapping])
        mapped_senses.extend(mapped_test_chunk)

    return mapped_senses


def calculate_scores_for_word(word, gold_instance_dict, mapped_system_senses):
    instances = gold_instance_dict.keys()
    gold_senses = get_max_sense(gold_instance_dict, instances)

    correct = 0
    for instance, g_sense in izip(instances, gold_senses):
        s_sense = mapped_system_senses.get(instance, None)
        if g_sense == s_sense:
            correct += 1

    correct = float(correct)
    precision = correct / len(mapped_system_senses)
    recall = correct / len(instances)
    f1_score = (2 * precision * recall) / (precision + recall)

    return precision, recall, f1_score


def evaluate(key_file, system_file, n_folds=5):
    loader = SemevalKeyLoader()

    gold_answers = loader.read_keyfile(key_file)
    system_answers = loader.read_keyfile(system_file)

    for word in gold_answers:
        sys_instance_dict = system_answers.get(word, None)
        gold_instance_dict = gold_answers.get(word)
        if sys_instance_dict is not None:
            # Convert into list because we'll use indexing on it later.
            instances = list(set(gold_instance_dict).intersection(
                set(sys_instance_dict)))

            # Get only instances that both gold and system have.
            sys_senses = get_max_sense(sys_instance_dict, instances)
            gold_senses = get_max_sense(gold_instance_dict, instances)

            # find more perplex sense set and use for splitting.
            more_perplex_senses = sys_senses \
                if calc_perp(sys_senses) > calc_perp(gold_senses) \
                else gold_senses

            train_test_splits = _get_train_and_test_inst(more_perplex_senses,
                                                         instances, n_folds)
            mapped_system_senses = get_mapped_senses(gold_instance_dict,
                                                     sys_instance_dict,
                                                     train_test_splits)
            if len(mapped_system_senses) == 0:
                LOGGER.warning("No instance mapped for %s", word)
            else:
                calculate_scores_for_word(word, gold_instance_dict,
                                          mapped_system_senses)
        else:
            LOGGER.warning("Target word %s not found in system file", word)


def run_doctest():
    import doctest
    doctest.testmod()


def run_test(key_file, system_file):
    evaluate(key_file, system_file)


if __name__ == '__main__':
    # run_doctest()
    run_test('../../s13-test.key', '../../system10.ans')
    LOGGER.setLevel(logging.DEBUG)