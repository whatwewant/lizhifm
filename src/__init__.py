#!/usr/bin/env python
# coding=utf-8
import sys

from .each_anchor import Anchor
from .search_keyword import ListRadio

def usage(options=None):
    print('%s options arg' % sys.argv[0].split('\\').pop())
    print("Usage: ")
    print("\t-i fm_id")
    print("\t-s keyword")

option_funcs = {
    '-i': 'download',
    '-s': 'search',
}

def main():
    if len(sys.argv) != 3 :
        usage()
        sys.exit(0)

    option = str(sys.argv[1])
    func = eval(option_funcs.get(option, 'usage'))
    func(str(sys.argv[2]))

def download(id):
    oo = Anchor()
    oo.download_mp3(str(id))

def search(keyword):
    OO = ListRadio()
    OO.search(str(keyword))

