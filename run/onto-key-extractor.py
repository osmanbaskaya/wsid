#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import sys
    
for line in sys.stdin:
    parsed_line = line.split('\t')
    tw, instance = parsed_line[:2]
    instance_id = instance.split('.')[-1]
    sense = parsed_line[3]
    print "%s %s.%s %s" % (tw, tw, instance_id, sense)
