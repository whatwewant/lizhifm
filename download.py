#!/usr/bin/env python
# coding=utf-8

import sys
import requests
import os
import time
import traceback

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
        self.__file_already_download = False
        self.__tmp_file_name_exists = False # 9
        self.__tmp_file_name_size = 0 # 10
        self.__range_headers = None # 11
        self.__requests_stream_object = None # 12
        self.__requests_ok = False
        self.__file_modified = False # 13
        self.__all_file_size = 0 # 14

        self.__logdir = os.path.abspath('.') # 15
        self.__logfile = 'client_error.log'
        self.__logfile_path = os.path.join\
                (self.__logdir, self.__logfile)

        #if os.path.exists(self.__logfile_path):
        #    os.remove(self.__logfile_path)

    def set_all_info(self, url, file_name, file_path):
        assert url
        assert file_name
        self.set_url(url)
        self.set_file_path_and_name(file_name, file_path)
        self.set_server_response_header()
        self.set_accept_range()
        self.set_content_length()
        self.set_file_size_unit()
        self.set_file_name_exists()
        self.set_tmp_file_name_exists()
        self.set_tmp_file_name_size()
        self.set_open_file_mode()
        self.set_range_headers()
        self.set_requests_stream_object()
        self.set_file_modified()
        self.set_all_file_size()

    def set_all_file_size(self):
        self.__all_file_size = self.__content_length + \
                self.__tmp_file_name_size

    def set_url(self, url):
        assert url
        self.__url = url

    def set_server_response_header(self):
        assert self.__url
        self.__server_response_headers = requests.head(self.__url, \
                                headers={'Range': 'bytes=0-'}).headers

    def set_accept_range(self):
        assert self.__server_response_headers
        if self.__server_response_headers.get('Accept-Range'):
            self.__accept_range = True

    def set_open_file_mode(self):
        if self.__accept_range:
            self.__open_file_mode = 'ab'

    def set_file_path_and_name(self, file_name, file_path=None):
        assert file_name
        self.__file_name = str(file_name)
        self.__tmp_file_name = str(file_name) + '.tmp'
        if file_path:
            self.__file_path = str(file_path)
        self.__file_final = os.path.join(self.__file_path, self.__file_name)
        self.__tmp_file_final = os.path.join(self.__file_path, 
                                             self.__tmp_file_name)

    def set_file_name_exists(self):
        path = os.path.join(self.__file_path, self.__file_name)
        self.__file_name_exists = os.path.exists(path)
        if self.__file_name_exists:
            print('File %s Exists;' % self.__file_name)
            self.__file_already_download = True
       # print path
       # print self.__file_name_exists
       # if self.__file_name_exists:
       #     try:
       #         if self.__content_length == os.path.getsize(path):
       #             print('File %s Exists: length: %d byte' % 
       #                   (self.__file_name, os.path.getsize(path)))
       #     except OSError:
       #         traceback.print_exc()
       #         with open(self.__logfile_path, 'a') as log:
       #             log.write('OSError' + '\n')
       #         raise

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
        # print self.__server_response_headers
        # assert self.__content_length
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
        elif file_size_dl > 1024:
            unit = 'KB'
            file_size = file_size_dl / float(1024)
        return (file_size, unit)

    def set_requests_stream_object(self):
        assert self.__url
        if not self.__accept_range:
            self.__requests_stream_object = requests.get(self.__url, 
                        stream=True)
            self.__requests_ok = self.__requests_stream_object.ok
        else:
            assert self.__range_headers
            self.__requests_stream_object = requests.get(self.__url, 
                        stream=True, headers=self.__range_headers)
            self.__requests_ok = self.__requests_stream_object.ok

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

    def set_tmp_file_name_size(self):
        if self.__tmp_file_name_exists:
            path = os.path.join(self.__file_path, self.__tmp_file_name)
            self.__tmp_file_name_size = os.path.getsize(path)

    def set_range_headers(self):
        if self.__tmp_file_name_size >= 0:
            self.__range_headers = {'Range': 'bytes=%d-' % self.__tmp_file_name_size}

    def delete_file(self, file_path, file_name):
        assert file_path
        assert file_name
        if self.file_exists(file_path, file_name):
            os.remove(os.path.join(file_path, file_name))
        else:
            print('File %s Doesnot Exist' % file_name)

    def set_file_modified(self):
        # assert self.__content_length
        if self.__file_name_exists:
           # local_file_size = self.get_file_name_size()
           # print self.__content_length + self.__tmp_file_name_size
           # exit(-1)
           # if self.__content_length+self.__tmp_file_name_size \
           # != local_file_size:
           #     print('File %s Modified' % self.__file_name)
           #     self.delete_file(self.__file_path, self.__file_name)
           #     self.__file_modified = True
           # else:
           #     print('File %s Already Download; Length: %d' %
           #          (self.__file_name, self.get_file_name_size()))
            self.__file_already_download = True

    def rename_old_to_new(self, old, new):
        os.rename(old, new)

    def calculate_percent(self, part, all):
        assert all
        return part * 100/ float(all)

    def calculate_time(self, left_time):
        left_time = int(left_time)
        second = left_time % 60
        second = '0' + str(second) if second < 10 else str(second)
        minute = left_time / 60 % 60
        minute = '0' + str(minute) if minute < 10 else str(minute)
        hour = left_time / 3600
        hour = '0' + str(hour) if hour < 10 else str(hour)

        return '%s:%s:%s' % (hour, minute, second)

    def print_status(self, already_download_size, start_second, id=0):
        assert already_download_size
        assert self.__content_length
        id = 0 if not id else id

        end_second = int(time.time())
        time_segment = end_second - start_second
        if time_segment <= 0:
            return

        download_speed = (already_download_size - \
                          self.__tmp_file_name_size)/ float(time_segment)
        left_time = (self.__all_file_size - already_download_size) / float(download_speed)
        left_time_str = self.calculate_time(left_time)

        (already_download, already_download_unit) = self.tranform_file_size_and_unit(already_download_size)
        (speed, speed_unit) = self.tranform_file_size_and_unit(download_speed)
        percent = self.calculate_percent(already_download_size, 
                                         self.__all_file_size)

        if percent > 100:
            assert self.__url
            assert self.__file_name
            assert self.__file_path
            assert self.__file_already_download
            self.delete_file(self.__file_path, self.__tmp_file_name)
            self.download(self.__url, self.__file_name, self.__file_path, id)

        # ID:1 File: Hear.h [ 12.3MB ] [ 27% ] [ Speed: 123kb/s Left Time: 00:00:00]
        #status = 'ID:%d File: %s [ %.2f %s ] [ %3.2f%% ] [ Speed: %.2f %s left Time: %f ]' % \
        #            (id, self.__file_name, already_download, already_download_unit, percent, speed, speed_unit, left_time)
        status = '%03.2f%s [%03.2f%%] [Speed:%03.2f%s/s Timeleft:%s]' % \
                    (already_download, already_download_unit, percent, speed, speed_unit, left_time_str)

        # status = status + chr(8)*(len(status)+1)
        sys.stdout.write(status + ' \b      \r')
        # sys.stdout.write(status + '\r')
        sys.stdout.flush()
        

    def download(self, url, file_name, file_path=None, id=0):
        '''
            download main
        ''' 
        # assert when url, file_name is None
        assert url
        assert file_name
        self.set_all_info(url, file_name, file_path)

        if not self.__requests_ok:
            with open(os.path.join(self.__logdir, 
                        self.__logfile), 'a') as log:
                log.write('Error Download: ' +
                         self.__url + '\n')
            return (0, 0)

        #print self.__file_already_download
        #assert self.__file_already_download
        if self.__file_already_download:
            return (0, 0)

        assert self.__server_response_headers
        assert self.__requests_stream_object
        assert self.__file_name
        assert self.__file_final
        assert self.__open_file_mode
        
        if not self.__requests_stream_object.ok:
            print('Requests Error')
            return

        (all_size, all_size_unit) = \
                self.tranform_file_size_and_unit(self.__all_file_size)
        print('ID:%d File: %s [ %.2f %s ] \b                   ' % \
              (id, self.__file_name, all_size, all_size_unit))

        tf = ''
        file_size_dl = 0
        if self.__tmp_file_name_size:
            file_size_dl = self.__tmp_file_name_size
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
                # if int(time.time() - start_second) % 2 == 0:
                self.print_status(file_size_dl, start_second, id)
            tf.close()
        except :
            raise
            tf.close()
            print("Something Wrong!")

        self.rename_old_to_new(self.__tmp_file_final, self.__file_final)

        return (self.__all_file_size, file_size_dl)

