#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import tempfile
from collections import defaultdict as dd
from subprocess import check_output


kmeans_base = "../bin/wkmeans -r {} -l -w -s {} -k {} 2>/dev/null"
#kmeans_out_base = "gzip >> {}/{}.km.gz & \n"

scorer = '/usr/bin/java -jar ../bin/ss.jar -s'


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def run(input, enrichment, kmeans_input_base, key_file, k, column, num_of_iter=10,
        evaluate_separately=False):

    output_formatter = "python kmeans_output_formatter.py > {}/{}.km"
    for pos, files in input.iteritems():
        additional_file = enrichment[pos]
        inp = kmeans_input_base.format(' '.join(files))
        if kmeans_input_base.startswith('cat'):
            ff = tempfile.NamedTemporaryFile('w', prefix='wsid-tmp')
            p = '%s | gzip > %s' % (inp, ff.name)
            os.system(p)
            filtered = tempfile.NamedTemporaryFile('w', prefix='wsid-tmp')
            p = 'zcat %s | %s | gzip > %s' % (additional_file, column,
                                              filtered.name)
            os.system(p)
            inp = "zcat %s %s" % (ff.name, filtered.name)
        kmeans = kmeans_base.format(num_of_iter, 1, k)
        output = output_formatter.format(path, pos)
        process = ' | '.join([inp, kmeans, output])
        os.system(process)
    return evaluate(key_file, path, evaluate_separately)


def parse_input(files):
    d = dd(list)
    map(lambda f: d[f[-1]].append(f), files)
    return d


def evaluate(key_file, path, evaluate_separately=False):
    scores = []
    total = 0
    if evaluate_separately:
        for i, fn in enumerate(os.listdir(path), 1):
            score = check_output('{} {} {}/{} | tail -2 | head -1'. \
                                 format(scorer, key_file, path, fn), shell=True)
            score = float(score.split('\t')[1])
            scores.append((fn, score))
            total += score

    # print >> sys.stderr, total / i
    os.system('cat {}/*.km > {}/system_file.txt'.format(path, path))
    score = check_output('{} {} {}/system_file.txt | tail -2 | head -1'.format(scorer, key_file, path), shell=True)
    score = score.split()[-1]
    scores.append(('all', score))
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

    path = tempfile.mkdtemp(prefix='wsid-tmp-pos-{}'.format(args.k))

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
    num_of_iter = 32
    scores = run(input, enrichment, kmeans_input_base, args.key_file,
                 args.k, column, num_of_iter, args.evaluate_separately)

    for score in scores:
        print "{}\t{}".format(args.k, '{}\t{}'.format(*score))
