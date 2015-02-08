#!/usr/bin/env python
# coding=utf-8

import requests
from prettytable import PrettyTable

try:
    input = raw_input
except :
    pass

class GoodAnchor:
    URL = r'http://www.lizhi.fm/api/promo/{page}'

    def __init__(self):
        pass

    @classmethod
    def display_status(self, page=1):
        url = GoodAnchor.URL.format(page=page)
        jsonData = requests.get(url).json()
        title = jsonData.get('model')

        radios = jsonData.get('radio_list').get('radios')

        data_table = PrettyTable(['', 'NAME', 'FMID', 'AUTHOR'])
        each_page_number = 1
        for each in radios:
            data_table.add_row([20*(page-1)+each_page_number,
                                each.get('name'), 
                                each.get('band'),
                                each.get('user_name')])
            each_page_number += 1
        print(data_table)
    
    @classmethod
    def next_page(self):
        page = 1
        while True:
            self.display_status(page)
            choice = input('下一页? (y|N)')
            if choice not in ['y', 'yes', 'Y', 'YES']:
                return 
            page += 1

if __name__ == '__main__':
    GoodAnchor.next_page()
