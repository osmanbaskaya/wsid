#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"

"""

"""

import sys
import nltk

lemmatizer = nltk.WordNetLemmatizer()

for line in sys.stdin:
    instance, sentence = line.split('\t')
    word, pos, instance_id = instance.split('.')
    s = map(lambda w: lemmatizer.lemmatize(w, pos), sentence.lower().split())
    d = dict(zip(s, range(len(s))))
    try:
        offset = d[word]
    except KeyError:
        sys.stderr.write("%s\n" % instance)
        continue
    sentence = sentence.split()
    print "%s <%s> %s" % (" ".join(sentence[offset-4:offset]), instance,
                          " ".join(sentence[offset+1:min(len(sentence), offset+4)]))



