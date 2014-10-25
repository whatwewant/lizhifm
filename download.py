#!/usr/bin/env python
# coding=utf-8

import sys
import requests
import os
import time

reload(sys)
sys.setdefaultencoding('utf-8')

class Download:
    '''
        download class
    '''
    def __init__(self):
        self.__url = '' # 1
        self.__file_path = '.' # 2default current dir
        self.__file_name = ''
        self.__file_final = ''
        self.__tmp_file_name = '' # .tmp
        self.__tmp_file_final = ''

        self.__server_response_headers = '' # 3
        self.__accept_range = False # 4
        self.__open_file_mode = 'wb' # 5
        self.__content_length = 0 # 6
        self.__file_size_unit = 'byte' # 7
        self.__file_size = 0

        self.__file_name_exists = False # 8
        self.__tmp_file_name_exists = False # 9
        self.__tmp_file_name_size = 0 # 10
        self.__range_headers = None # 11
        self.__requests_stream_object = None # 12
        self.__file_modified = False # 13

    def set_all_info(self, url, file_name, file_path):
        assert url
        assert file_name
        self.set_url(url)
        self.set_file_path_and_name(file_name, file_path)
        self.set_server_response_header()
        self.set_accept_range()
        self.set_open_file_mode()
        self.set_content_length()
        self.set_file_size_unit()
        self.set_file_name_exists
        self.set_tmp_file_name_exists()
        self.set_tmp_file_name_size()
        self.set_range_headers()
        self.set_requests_stream_object()
        self.set_file_modified()

    def set_url(self, url):
        assert url
        self.__url = url

    def set_server_response_header(self):
        assert self.__url
        self.__server_response_headers = requests.head(self.__url).headers

    def set_accept_range(self):
        assert self.__server_response_headers
        if self.__server_response_headers.get('Accept-Range'):
            self.__accept_range = True

    def set_open_file_mode(self):
        if self.__accept_range:
            self.__open_file_mode = 'ap'

    def set_file_path_and_name(self, file_name, file_path=None):
        assert file_name
        self.__file_name = file_name
        self.__tmp_file_name = file_name + '.tmp'
        if file_path:
            self.__file_path = file_path
        self.__file_final = os.path.join(self.__file_path, self.__file_name)
        self.__tmp_file_final = os.path.join(self.__file_path, self.__tmp_file_name)

    def set_file_name_exists(self):
        path = os.path.join(self.__file_path, self.__file_name)
        self.__file_name_exists = os.path.exists(path)

    def set_tmp_file_name_exists(self):
        assert self.__file_path
        assert self.__tmp_file_name
        self.__tmp_file_name_exists =  self.file_exists( \
            self.__file_path, self.__tmp_file_name)
        

    def set_content_length(self):
        assert self.__server_response_headers
        length = self.__server_response_headers.get('Content-Length', None)
        if length:
            self.__content_length = int(length)

    def set_file_size_unit(self):
        assert self.__content_length
        if self.__content_length > 1024 * 1024 * 1024:
            self.__file_size_unit = 'GB'
            self.__file_size = self.__content_length / float(1024*1024*1024)
        elif self.__content_length > 1024 * 1024:
            self.__file_size_unit = 'MB'
            self.__file_size = self.__content_length / float(1024*1024)
        elif self.__content_length > 1024:
            self.__file_size_unit = 'KB'
            self.__file_size = self.__content_length / float(1024)

    def tranform_file_size_and_unit(self, file_size_dl):
        file_size = file_size_dl
        unit = 'byte'
        if file_size_dl > 1024 * 1024 * 1024:
            unit = 'GB'
            file_size = file_size_dl / float(1024*1024*1024)
        elif file_size_dl > 1024 * 1024:
            unit = 'MB'
            file_size = file_size_dl / float(1024*1024)
        elif self.__content_length > 1024:
            unit = 'KB'
            file_size = file_size_dl / float(1024)
        return (file_size, unit)

    def set_requests_stream_object(self):
        assert self.__url
        if not self.__accept_range:
            self.__requests_stream_object = requests.get(self.__url, 
                        stream=True)
        else:
            assert self.__range_headers
            self.__requests_stream_object = requests.get(self.__url, 
                        stream=True, headers=self.__range_headers)

    def file_exists(self, file_path, file_name):
        assert file_path
        assert file_name
        return os.path.exists(os.path.join(file_path, file_name))

    def get_file_name_size(self):
        assert self.__file_path
        assert self.__file_name
        if self.file_exists(self.__file_path, self.__file_name):
            path = os.path.join(self.__file_path, self.__file_name)
            return os.path.getsize(path)
        else:
            return 0

    def set_tmp_file_size(self):
        if self.__tmp_file_name_exists:
            path = os.path.join(self.__file_path, self.__tmp_file_name)
            self.__tmp_file_name_size = os.path.getsize(path)

    def set_range_headers(self):
        if self.__tmp_file_name_size > 0:
            self.__range_headers = {'Range': 'bytes=%d-' % self.__tmp_file_name_size}

    def delete_file(self, file_path, file_name):
        assert file_path
        assert file_name
        if self.file_exists(file_path, file_name):
            os.remove(os.path.join(file_path, file_name))
        else:
            print('File %s Doesnot Exist' % file_name)

    def set_file_modified(self):
        assert self.__content_length
        if self.file_name_exists():
            local_file_size = self.get_file_name_size()
            if self.__content_length != local_file_size:
                print('File %s Modified' % self.__file_name)
                self.delete_file(self.__file_path, self.__file_name)
                self.__file_modified = True

    def rename_old_to_new(self, old, new):
        os.rename(old, new)

    def calculate_percent(self, part, all):
        assert all
        return part / float(all)

    def print_status(self, already_download_size, start_second, id=None):
        assert already_download_size
        assert self.__content_length
        id = ' ' if not id else id

        end_second = int(time.time())
        time_segment = end_second - start_second
        if time_segment <= 0:
            return

        download_speed = already_download_size / float(time_segment)
        left_time = (self.__content_length - already_download_size) / float(download_speed)

        (already_download, already_download_unit) = self.tranform_file_size_and_unit(already_download_size)
        (speed, speed_unit) = self.tranform_file_size_and_unit(download_speed)
        percent = self.calculate_percent(already_download, self.__content_length)

        # ID:1 File: Hear.h [ 12.3MB ] [ 27% ] [ Speed: 123kb/s Left Time: 00:00:00]
        status = 'ID:%d File: %s [ %.2f %s ] [ %3.2%% ] [Speed: %.2f %s left Time: %s]' % \
                    (id, self.__file_name, already_download, already_download_unit, percent, 
                    speed, speed_unit, left_time)

        sys.stdout.write(status + '\r')
        sys.stdout.flush()
        

    def download(self, url, file_name, file_path=None, id=None):
        '''
            download main
        ''' 
        # assert when url, file_name is None
        assert url
        assert file_name
        self.set_all_info(url, file_name, file_path)
        assert self.__server_response_headers
        assert self.__requests_stream_object
        assert self.__file_name
        assert self.__file_final
        assert self.__open_file_mode

        tf = ''
        file_size_dl = 0
        try:
            tf = open(self.__tmp_file_final, self.__open_file_mode)
            response = self.__requests_stream_object
            if not response.ok:
                print('Requests Status Error.')
                return
            start_second = int(time.time())
            for block in response.iter_content(8192):
                if not block:
                    break
                tf.write(block)
                file_size_dl += len(block)
                self.print_status(file_size_dl, start_second, id)
            tf.close()
        except :
            tf.close()
            print("Something Wrong!")
            raise

        self.rename_old_to_new(self.__tmp_file_final, self.__file_final)

        return (self.__content_length, file_size_dl)

