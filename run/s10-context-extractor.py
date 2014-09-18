#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import sys
from bs4 import BeautifulSoup
from itertools import izip
import re
import string

files = sys.argv[1:]
for filename in files:
    tags = BeautifulSoup(open(filename), 'xml').find_all("TargetSentence")
    sentences = map(lambda s: s.text.strip(), tags)
    instances = re.findall("<(\w+\.\w\.\d+)>", open(filename).read())

    for inst, sentence in izip(instances, sentences):
        print "%s\t%s" % (inst, filter(lambda x: x in string.printable, sentence))
        #try:
            #print "%s\t%s" % (inst, filter(lambda x: x in string.printable, sentence))
        #except UnicodeEncodeError:
            #print inst
            #raise UnicodeEncodeError
