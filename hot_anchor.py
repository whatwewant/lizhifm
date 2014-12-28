#!/usr/bin/env python
# coding=utf-8

import requests
import sys
import json
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except :
    raise

class HotAnchors:
    '''热榜'''
    def __init__(self):
        self.__base_url = r'http://www.lizhi.fm/api/hot/{page}'
        self.__url = None
        self.__default_page = 0
        self.__count_anchors = 1
        self.__request = None
        self.__request_content = None

        self.__title = u'未知'

    def set_url(self):
        self.__url = self.__base_url.format(page=self.__default_page)

    def get_html(self):
        self.set_url()
        self.__request = requests.get(self.__url)
        self.__request_content = self.__request.content
        #   .decode(self.__request.encoding)

    def resolve_html(self):
        assert self.__request_content
        data = json.loads(self.__request_content)
        self.__title = data.get('model', u'未知')
        self.__radio_list = data.get('radio_list')
        self.__radio_list_cnt = self.__radio_list.get('cnt')
        self.__radio_list_radios = self.__radio_list.get('radios')
        
    def resolve_radios(self):
        assert self.__radio_list_radios
        # self.__radio_list_radios is list, each is dict
        # id
        # name
        # band
        # au_cnt
        # fav_cnt
        # desc
        # user_name
        # u_thumb
        # cover
        # uid
        # tags
        # audios
    
    def print_info(self):
        assert self.__radio_list_radios
        print('Page %d' % self.__default_page)
        print('Anchors Number: %d' % len(self.__radio_list_radios))
        Title = '%s %s %s %s' % ("ID".ljust(4), 
                                "NAME".ljust(15, ' '),
                                "ANCHORS".ljust(15, ' '),
                                "BAND".ljust(10),
                             )
        print('%s' % Title)

        for each in self.__radio_list_radios:
            each_info = '%s %s %s %s' % (str(self.__count_anchors).ljust(4),
                                each.get('name').ljust(15, u'　'),
                                each.get('user_name').ljust(15, u'　'),
                                each.get('band').ljust(10),
                                 )
            print('%s' % each_info)
            self.__count_anchors += 1

    def get_next(self):
        self.__default_page += 1
        self.get_html()
        self.resolve_html()
        self.print_info()

    def run(self):
        choice = 'y'
        while choice.startswith('y') or choice.startswith('Y'):
            self.get_next()
            choice = raw_input('Do you want to go to'
                               ' the next page ? (y | N)')
        sys.exit(0)

if __name__ == '__main__':
    oo = HotAnchors()
    oo.run()
        
