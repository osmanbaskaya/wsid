#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

import os
import subprocess
import sys


def s10_f1_run():
    systems = os.listdir('../../systems')
    command = "./sup_eval.sh ../../systems/%s . ../80_20/all/mapping.%d.key ../80_20/all/test.%d.key 2>/dev/null | tail -1 | grep -oP '0.\d+'"

    for system in systems:
        scores = []
        if system != 'filesToSystemsMap':
            for i in range(1,6):
                c = command % (system, i, i)
                s = subprocess.Popen(c, shell=True, stdout=subprocess.PIPE).stdout.read().strip()
                scores.append(float(s))
            print >> sys.stderr, system, scores
            print "%s\t%f" % (system, sum(scores) / len(scores))

def s07_f1_run():
    systems = os.listdir('../../s07/systems')
    command = "./sup_eval.sh ../../s07/systems/%s . ../../s07/keys/random_split/82_18/senseinduction.random82train.key ../../s07/keys/random_split/82_18/senseinduction.random82test.key 2>/dev/null | tail -1 | grep -oP '0.\d+'"

    for system in systems:
        c = command % (system)
        s = subprocess.Popen(c, shell=True, stdout=subprocess.PIPE).stdout.read().strip()
        s = float(s)
        print "%s\t%f" % (system, s)

s07_f1_run()
