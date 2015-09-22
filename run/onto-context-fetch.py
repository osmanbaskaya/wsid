#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"
import sys

for line in sys.stdin:
    parsed_line = line.split('\t')
    tw, instance = parsed_line[:2]
    offset, sentence = parsed_line[7:]
    offset = int(offset)
    sentence = sentence.split()
    print "%s <%s> %s" % (" ".join(sentence[max(offset-4, 0):offset]), instance,
                          " ".join(sentence[offset+1:min(len(sentence), offset+4)]))
