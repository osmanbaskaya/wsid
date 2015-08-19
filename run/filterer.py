#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""
This module makes filtering according to provided gold file and the column no.
Column_no starts with zero

"""

import sys
from nlp_utils import fopen
#import argparse


#parser = argparse.ArgumentParser()
#parser.add_argument('--exclude', action='store_true', default=False,
                     #help='exclude keys in the first file from the second.')


gold_file = sys.argv[1]
system_file = sys.argv[2]
gold_column_no = int(sys.argv[3]) # gold file column that matches with the system and gold file
target_column_no = int(sys.argv[4]) # gold file column that matches with the system and gold file
exclude = False
if len(sys.argv) == 6:
    if sys.argv[5] == 'exclude':
        exclude = True
    else:
        raise AttributeError, "check input args"

instances = set()
for line in fopen(gold_file):
    instance_id = line.split()[gold_column_no]
    instances.add(instance_id)

print >> sys.stderr, len(instances), system_file

for line in fopen(system_file):
    instance = line.split()[target_column_no]
    if instance in instances and not exclude:
        print line,
    elif instance not in instances and exclude:
        print line,
        
