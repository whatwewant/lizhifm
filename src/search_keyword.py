#!/usr/bin/env python
# coding=utf-8

import requests
import json
import sys
from prettytable import PrettyTable

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except :
    pass

class ListRadio(object):
    '''搜索电台'''
    def __init__(self):
        self.__search_url = 'http://www.lizhi.fm/api/search_radio/{keyword}/{page}'
        self.__store_file_name = 'ListRadio.txt'
        self.__data_split_char = ' '
    
    def show_result(self, data_list):
        # store data format
        # keyword page name band user_name
        if data_list == []:
            print("no data found")
            return
        data_table = PrettyTable(['', 'Name', 'FMID', 'Author'])
        for each in data_list:
            each_list = each.split(self.__data_split_char)
            name = each_list[2] #+ (40-len(each_list[2]))*' '
            band = each_list[3] #+ (10-len(each_list[3]))*' '
            user_name = each_list[4] #+ (25-len(each_list[4]))*' '
            #print('%40s %-10s %+25s' % (name, band, user_name))
            data_table.add_row([data_list.index(each)+1, 
                                name, band, user_name])
        print(data_table)

    def search(self, keyword):
        data_key = self.load_data_keyword()
        result = []
        if keyword in data_key:
            result = self.load_data_by_keyword(keyword)
        else:
            result = self.search_process(keyword)
        # show data
        self.show_result(result)
        return result

    def search_process(self, keyword):
        # network using
        str = self.get_json_string(keyword, 1)
        return self.resolve_json_string(str)

    def get_json_string(self, keyword, page):
        if page == None:
            page = 1
        url = self.__search_url.format(keyword=keyword, page=page)
        req = requests.get(url)
        return req.content.decode(req.encoding)

    def resolve_json_string(self, json_string):
        jsonObject = json.loads(json_string)
        
        # search result
        keyword = jsonObject.get('kw')
        page = jsonObject.get('p')
        # radio
        radio = jsonObject.get('radio')
        radioCount = radio.get('cnt')
        # detail : List, Each List Element is A Dict
        #   id
        #   name  # fm raido name
        #   band  # fm id
        #   au_cnt
        #   fav_cnt
        #   desc
        #   user_name # anchor name
        #   u_thumb # url jpg
        #   cover # url jpg
        #   uid
        #   tags
        #   audios
        radioDataList = radio.get('data') or []

        # load_data
        stored_data = self.load_data()
        # load_data_band
        stored_data_band = self.load_data_band()

        #
        return_data = []
        for each in radioDataList:
            each_message = keyword + self.__data_split_char + \
                    str(page) + self.__data_split_char + \
                    each['name'] + self.__data_split_char + \
                    each['band'] + self.__data_split_char + \
                    each['user_name']
            if each['band'] not in stored_data_band:
                stored_data.append(each_message)
            return_data.append(each_message)
        # store data
        if radioDataList != []:
            self.store_data(stored_data)

        return return_data
    
    def store_data(self, radioListDict):
        # store data format
        # keyword page name band user_name
        with open(self.__store_file_name, 'w') as fp:
            for each in radioListDict:
                fp.write(each + '\n')
        return True
            
    def load_data(self):
        # store data format
        # keyword page name band user_name
        try:
            origin_data = open(self.__store_file_name).readlines()
            remove_newline_data = []
            for each in origin_data:
                remove_newline_data.append(each.strip())
            return remove_newline_data
        except IOError:
            return []
    
    def load_data_keyword(self):
        # store data format
        # keyword page name band user_name
        #
        # return list
        data_key = []
        data = self.load_data()
        for each in data:
            key = each.split(self.__data_split_char)[0] 
            if key not in data_key:
                data_key.append(key)
        return data_key

    def load_data_by_keyword(self, keyword):
        # store data format
        # keyword page name band user_name
        #
        # return list
        data = self.load_data()
        data_by_key = []
        for each in data:
            if keyword == each.split(self.__data_split_char)[0]: 
                data_by_key.append(each)
        return data_by_key

    def load_data_band(self):
        '''fm id or called it band'''
        # store data format
        # keyword page name band user_name
        #
        # return list
        data = self.load_data()
        data_band = []
        for each in data:
            try:
                band = each.split(self.__data_split_char)[3]
                if band not in data_band:
                    data_band.append(band)
            except IndexError:
                continue
        return data_band

if __name__ == '__main__':
    import sys
    OO = ListRadio()
    OO.search(sys.argv[1])
