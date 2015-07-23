#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import tempfile
from collections import defaultdict as dd


kmeans_base = "../bin/wkmeans -r {} -l -w -s {} -k {} 2>/dev/null";
output_formatter = "python kmeans_output_formatter.py"
kmeans_out_base = "gzip >> {}/{}.km.gz & \n"

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
        use_gold_k=False, chunk_size=10, column=None):

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
            out = kmeans_out_base.format(path, basename)
            if column is None:
                process += ' | '.join([inp, kmeans, output_formatter, out])
            else:
                process += ' | '.join([inp, column, kmeans, output_formatter, out])
        print >> sys.stderr, process
        os.system(process + "wait")
    os.system('zcat {}/*.km.gz > {}/system_file.txt'.format(path, path))
    os.system('{} {} {}/system_file.txt | tail -2 | head -1'.format(scorer, key_file, path))
    #os.system('{} {} {}/system_file.txt'.format(scorer, key_file, path))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--approach', required=True, choices=['local', 'global', 'pos-based'])
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
    parser.add_argument('--not-scode', action='store_false', default=True)

    args = parser.parse_args()
    
    if args.k is None and not args.use_gold_k:
        parser.error("One of them needs to be set: k OR use_gold_k")

    #print >> sys.stderr, args
    print args.approach, args.k, args.use_gold_k, 

    path = tempfile.mkdtemp()

    if args.input[0].endswith('.gz'):
        kmeans_input_base= "zcat {}"
    else:
        kmeans_input_base= "cat {}"

    column = None

    if args.approach == 'local':
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


    run(args.input, kmeans_input_base, args.pair_file, args.sense_finding, args.key_file, 
        num_of_iter, args.k, args.use_gold_k, 10, column)
