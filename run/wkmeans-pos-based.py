#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import tempfile
from collections import defaultdict as dd
from subprocess import check_output
from utils.evaluate import geometric_mean


# WARNING: Weighted version of POS-based clustering. Follow the WEIGHTS COMMENTS.

#kmeans_base = "../bin/wkmeans -r {} -l -w -s {} -k {} 2>/dev/null"
kmeans_base = "../bin/wkmeans -r {} -l -s {} -k {} 2>/dev/null"  # WEIGHTS
#kmeans_out_base = "gzip >> {}/{}.km.gz & \n"

scorers = ['/usr/bin/java -jar ../bin/ss.jar -s', 
           '/usr/bin/java -jar ../bin/fuzzy-nmi.jar',
           '/usr/bin/java -jar ../bin/fuzzy-bcubed.jar']


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def run(input, enrichment, kmeans_input_base, key_file, k, column, num_of_iter=10,
        evaluate_separately=False):

    output_formatter = "python kmeans_output_formatter.py > {}/{}.km"
    path = tempfile.mkdtemp(prefix='wsid-wk-pos-based-k={}-{}'.format(args.k, key_file))
    for pos, files in input.iteritems():
        additional_file = enrichment[pos]
        inp = kmeans_input_base.format(' '.join(files))
        if kmeans_input_base.startswith('cat'):
            ff = tempfile.NamedTemporaryFile('w', prefix='wsid-tmp')
            p = '%s | cut -f1,3- | gzip > %s' % (inp, ff.name)  # remove WEIGHTS.
            # p = '%s | gzip > %s' % (inp, ff.name)
            os.system(p)
            filtered = tempfile.NamedTemporaryFile('w', prefix='wsid-tmp')
            # p = 'zcat %s | %s | gzip > %s' % (additional_file, column,
            #                                   filtered.name)
            # remove WEIGHTS
            p = 'zcat %s | %s | cut -f1,3- | gzip > %s' % (additional_file,
                                                           column, filtered.name)
            os.system(p)
            print >> sys.stderr, p
            inp = "zcat %s %s" % (ff.name, filtered.name)
        kmeans = kmeans_base.format(num_of_iter, 1, k)
        output = output_formatter.format(path, pos)
        process = ' | '.join([inp, kmeans, output])
        print >> sys.stderr, process
        os.system(process)
    return evaluate(key_file, path, evaluate_separately)


def parse_input(files):
    d = dd(list)
    map(lambda f: d[f[-1]].append(f), files)
    return d


def evaluate(key_file, path, evaluate_separately=False):
    scores = []
    if evaluate_separately:
        for i, fn in enumerate(os.listdir(path), 1):
            metric_scores = []
            for scorer in scorers:
                score = check_output('{} {} {}/{} | tail -2 | head -1'.\
                                        format(scorer, key_file, path, fn), shell=True)
                score = score.split('\t')[1]
                metric_scores.append(score)
            nmi = metric_scores[1]
            bcubed = metric_scores[2]
            metric_scores.append(str(geometric_mean(float(nmi), float(bcubed))))
            scores.append((fn, '\t'.join(metric_scores)))
            print >> sys.stderr, fn, '\n', scores

    os.system('cat {}/*.km > {}/system_file.txt'.format(path, path))
    metric_scores = []
    for scorer in scorers:
        score = check_output('{} {} {}/system_file.txt | tail -2 | head -1'.format(scorer, key_file, path), shell=True)
        score = score.split()[-1]
        metric_scores.append(score)

    nmi = metric_scores[1]
    bcubed = metric_scores[2]
    metric_scores.append(str(geometric_mean(float(nmi), float(bcubed))))
    scores.append(('all', '\t'.join(metric_scores)))
    return scores


    #os.system('{} {} {}/system_file.txt'.format(scorer, key_file, path))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--key-file', required=True)
    parser.add_argument('--input', nargs='+', required=True,
                        help="System's representation file(s)")
    parser.add_argument('--k', type=int, default=None, help="number of clusters")
    parser.add_argument('--enrichment', nargs='+', required=True,
                        help="file(s) that used for enrichment. Format is as follows:"
                             "pos_tag embedded_file pos_tag embedded_file ...")
    parser.add_argument('--not-scode', action='store_true', default=False)
    parser.add_argument('--evaluate-separately', action='store_true', default=False)

    args = parser.parse_args()

    if args.k is None and not args.use_gold_k:
        parser.error("One of them needs to be set: k OR use_gold_k")

    #print >> sys.stderr, args


    if args.input[0].endswith('.gz'):
        kmeans_input_base = "zcat {}"
    else:
        kmeans_input_base = "cat {}"

    column = None

    if args.not_scode:
        raise NotImplementedError("hello hello")
    else:
        column = "perl -ne 'print if s/^1://'"

    #print >> sys.stderr, args
    #print >> sys.stderr, [kmeans_input_base, num_of_iter, args.k, column]
    input = parse_input(args.input)
    enrichment = dict(chunks(args.enrichment, 2))
    num_of_iter = 8
    scores = run(input, enrichment, kmeans_input_base, args.key_file,
                 args.k, column, num_of_iter, args.evaluate_separately)

    for score in scores:
        print "{}\t{}".format(args.k, '{}\t{}'.format(*score))
