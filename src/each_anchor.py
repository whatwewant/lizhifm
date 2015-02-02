#!/usr/bin/env python
# coding=utf-8

import sys
import json
import os
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except :
    pass

# from bs4 import BeautifulSoup
try:
    from downloadhelper import Download, MultiDownloadThread
    import requests
except ImportError:
    pass

class Anchor(object):
    '''每个主播的节目'''
    def __init__(self):
        # html encoding
        self.__decode_type = None
        self.__encode_type = sys.getfilesystemencoding() if \
                sys.getfilesystemencoding != 'mbcs' \
                else 'gbk'

        self.__fm_id = int() #
        # main Page
        self.__url_home_of_anchor = "http://www.lizhi.fm/#/{fm_id}"
        # anchor info
        self.__url_anchor_info = "http://www.lizhi.fm/api/radio?band={fm_id}&flag=3"
        self.__anothor_info_json = ""
        # Anchor store mp3 dir path
        self.__home_dir = os.environ.get('HOME', '.')
        self.__store_anochor_path = os.path.join(self.__home_dir, 
                                                 'Music/LizhiFM')
        self.__store_anochor_dirname = ""
        self.__final_path = ""

        # audios
        self.__url_audios_json = "http://www.lizhi.fm/api/radio_audios?s={start}&l={length}&band={fm_id}"
        # total audios
        self.__total_audios_list = []

        self.__source_html = None

        self.__req = requests.Session()

    def get_anchor_info_json(self, fm_id):
        resp = self.__req.get(self.__url_anchor_info\
                              .format(fm_id=fm_id, encoding='utf-8'))
        self.__decode_type = resp.encoding
        try:
            return json.loads(resp.content\
                          .decode(self.__decode_type)\
                          .encode(self.__encode_type))
        except TypeError:
            return json.loads(resp.content.decode(resp.encoding))

    def resolve_anchor_info_json(self, anchor_info_json):
        info = anchor_info_json
        self.__anothor_info_json = info
        self.__store_anochor_dirname = info.get('name').strip() + '--' + info.get('user_name').strip()
        return info

    def create_anchor_main_dir(self, path='.'):
        final_path = os.path.join(self.__store_anochor_path, 
                                  self.__store_anochor_dirname)
        self.__final_path = final_path

        if not os.path.isdir(final_path):
            os.makedirs(final_path)

    def get_audios_json(self, fm_id, start, length):
        # get json : audios
        tmp_url = self.__url_audios_json.format(fm_id=fm_id,start=start,length=length)
        resp = self.__req.get(tmp_url)
        try:
            content = json.loads(resp.content)
        except TypeError:
            content = json.loads(resp.content.decode(resp.encoding))
        return content

    def resolve_audios_json(self, audios_json):
        # resolve json : audios
        # each mp3
        each_page = list()
        for ep3 in audios_json:
            ep3_dict = {}
            for key, value in ep3.items():
                ep3_dict[key] = value
            each_page.append(ep3_dict)
            self.__total_audios_list.append(ep3_dict)
        return each_page

    #def store_mp3(self, file_name, file_format, url):
    #    final_file = self.__final_path + '/' + file_name + '.' + file_format
    #    file_size = int(requests.head(url).headers.get('Content-Length'))
    #    file_size = 1 if not file_size else file_size
    #    with open(final_file, 'wb') as fp:
    #        response = requests.get(url, stream=True)
    #        if not response.ok:
    #            print("Requests Status Error.")
    #            return 
    #        file_size_dl = 0
    #        for block in response.iter_content(1024):
    #            if not block:
    #                break
    #            fp.write(block)
    #            file_size_dl += len(block)
    #            status = r"%.2f MB  [%3.2f%%]" % (file_size_dl/float(1024*1024), file_size_dl * 100 / float(file_size))
    #            sys.stdout.write(status + '\r')
    #            sys.stdout.flush()

            
    def download_mp3(self, fm_id):
        import time
        self.resolve_anchor_info_json(self.get_anchor_info_json(fm_id))
        self.create_anchor_main_dir()

        start = 0
        length = 20
        id = 1
        threads = []
        ids = 0
        for i in range(5):
            ep3s = self.resolve_audios_json(self.get_audios_json(fm_id, start, length))
            ids += len(ep3s)
            for ep3 in ep3s:
                c = time.localtime(ep3['create_time']/1000)
                create_time = '%02d%02d%02d%s' % (c.tm_year, c.tm_mon, c.tm_mday, '-')
                name = ep3['name'].replace('/', '+').replace(' ', '')
                thread = MultiDownloadThread(ep3['url'], 
                            create_time+name+'.mp3', 
                            self.__final_path, id=id, ids=ids)
                threads.append(thread)
                id += 1
            start += length
            length += 20

        for thread in threads:
            import threading
            thread.start()
            while len(threading.enumerate()) > 5:
                time.sleep(1)

        #for thread in threads:
        #    thread.join()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2 :
        print("Usage: " + sys.argv[0] + " fm_id")
        exit(0)

    for id in sys.argv:
        if id == sys.argv[0]:
            continue
        anchor = Anchor()
        anchor.download_mp3(str(id))
