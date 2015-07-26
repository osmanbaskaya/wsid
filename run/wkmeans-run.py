#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import tempfile
from collections import defaultdict as dd
from subprocess import check_output


kmeans_base = "../bin/wkmeans -r {} -l -w -s {} -k {} 2>/dev/null";
#kmeans_out_base = "gzip >> {}/{}.km.gz & \n"

scorer = '/usr/bin/java -jar ../bin/ss.jar -s'


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def find_num_senses_of_each_word(key_file):
    d = dd(set)
    with open(key_file) as f:
        for line in f:
            tw, inst_id, sense = line.split()
            d[tw].add(sense)

    return dict(map(lambda tw: (tw, len(d[tw])), d))


def run(input, kmeans_input_base, pair_file, sense_finding, key_file, num_of_iter, k, 
        use_gold_k=False, chunk_size=10, column=None, evaluate_separately=False):

    output_formatter = "python kmeans_output_formatter.py > {}/{}.km & \n"

    if use_gold_k:
        sense_dict = find_num_senses_of_each_word(key_file)
    else:
        sense_dict = {}

    for chunk in chunks(input, chunk_size):
        process = ""
        for f in chunk:
            basename = os.path.basename(f)
            inp = kmeans_input_base.format(f)
            kmeans = kmeans_base.format(num_of_iter, 1, sense_dict.get(basename, k))
            #out = kmeans_out_base.format(path, basename)
            output = output_formatter.format(path, basename)
            if column is None:
                process += ' | '.join([inp, kmeans, output])
            else:
                process += ' | '.join([inp, column, kmeans, output])
        #print >> sys.stderr, process
        os.system(process + "wait")
    return evaluate(key_file, path, evaluate_separately)

def evaluate(key_file, path, evaluate_separately=False):
    scores = []
    if evaluate_separately:
        for fn in os.listdir(path):
            score = check_output('{} {} {}/{} | tail -2 | head -1'.\
                                    format(scorer, key_file, path, fn), shell=True)
            score = score.split('\t')[1]
            scores.append((fn, score))

    os.system('cat {}/*.km > {}/system_file.txt'.format(path, path))
    score = check_output('{} {} {}/system_file.txt | tail -2 | head -1'.format(scorer, key_file, path), shell=True)
    score = score.split()[-1]
    scores.append(('all', score))
    return scores

    #os.system('{} {} {}/system_file.txt'.format(scorer, key_file, path))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--approach', required=True, choices=['locale', 'global', 'pos-based'])
    parser.add_argument('--key-file', required=True)
    parser.add_argument('--input', nargs='+', required=True, 
                        help="System's representation file(s)")
    parser.add_argument('--k', type=int, default=None, help="number of clusters")
    parser.add_argument('--use-gold-k', 
                        help="Using the key file to determine number of cluster",
                        default=False, action='store_true')
    parser.add_argument('--sense-finding', required=True, choices=['substitute', 'word'], 
                        help='This denotes the way of finding the sense.')
    parser.add_argument('--pair-file', help="this file contains substitutes \
                                             of each target word.")
    parser.add_argument('--not-scode', action='store_true', default=False)
    parser.add_argument('--evaluate-separately', action='store_true', default=False)

    args = parser.parse_args()
    
    if args.k is None and not args.use_gold_k:
        parser.error("One of them needs to be set: k OR use_gold_k")

    #print >> sys.stderr, args

    path = tempfile.mkdtemp(prefix='wsid-tmp')

    if args.input[0].endswith('.gz'):
        kmeans_input_base= "zcat {}"
    else:
        kmeans_input_base= "cat {}"

    column = None

    if args.approach == 'locale':
        num_of_iter = 32
    else:
        if args.k is None:
            parser.error("k cannot be None for pos-based or global approaches")
        else:
            num_of_iter = 1
            if args.not_scode:
                raise NotImplementedError("hello hello")
            else:
                column = "perl -ne 'print if s/^[01]://'"

    #print >> sys.stderr, args
    #print >> sys.stderr, [kmeans_input_base, num_of_iter, args.k, column]
    scores = run(args.input, kmeans_input_base, args.pair_file, args.sense_finding, 
                args.key_file, num_of_iter, args.k, args.use_gold_k, 10, column, args.evaluate_separately)

    if args.use_gold_k:
        k = 'gold'
    else:
        k = args.k
    
    print scores
    #print "{}\t{}\t{}\t{}".format(args.approach, k, args.sense_finding, scores)
