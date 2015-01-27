#!/usr/bin/env python
# coding=utf-8
import sys

from .each_anchor import Anchor

def main():
    if len(sys.argv) < 2 :
        print "Usage: " + sys.argv[0] + " fm_id"
        exit(0)

    for id in sys.argv:
        if id == sys.argv[0]:
            continue
        anchor = Anchor()
        anchor.download_mp3(str(id))

