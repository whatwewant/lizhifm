#!/usr/bin/env python
# coding=utf-8

import sys
import requests
import os
import time
import random
# import traceback
import threading
import socket

reload(sys)
sys.setdefaultencoding('utf-8')

VERSION = '1.0.0'

class MultiDownloadThread(threading.Thread):

    def __init__(self, url, file_name, file_path, id, ids=0):
        super(MultiDownloadThread, self).__init__()
        self.__url = url
        self.__file_name = file_name
        self.__file_path = file_path
        self.__id = id
        self.__ids = ids

    def run(self):
        do = Download()
        do.download(self.__url, 
                    self.__file_name,
                    self.__file_path,
                    self.__id,
                    self.__ids,
                   )

class Download:
    '''
        download class
    '''
    def __init__(self):
        self.__url = '' # 1
        # test whether internet connection available
        self.__internet_available = False
        # if error. leave the class
        self.__leave_now = False
        self.__file_path = '.' # 2default current dir, file store path
        self.__file_name = '' # file name
        self.__file_final = '' # Absolute path for a file
        self.__tmp_file_name = '' # file temp name, end with `.tmp`
        self.__tmp_file_final = '' # Absolute path for a temp file
        # write file
        self.__real_write_file = '' # Decided by file open mode 'wb' or 'ab'

        self.__server_response_headers = '' # 3
        self.__accept_range = False # 4
        self.__open_file_mode = 'wb' # 5
        self.__content_length = 0 # 6 the whole file content length
        self.__content_length_request = 0 # the request file content length
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

    def reset(self):
        self.__url = '' # 1
        # test whether internet connection available
        self.__internet_available = False
        # if error. leave the class
        self.__leave_now = False
        self.__file_path = '.' # 2default current dir, file store path
        self.__file_name = '' # file name
        self.__file_final = '' # Absolute path for a file
        self.__tmp_file_name = '' # file temp name, end with `.tmp`
        self.__tmp_file_final = '' # Absolute path for a temp file
        # write file
        self.__real_write_file = '' # Decided by file open mode 'wb' or 'ab'

        self.__server_response_headers = '' # 3
        self.__accept_range = False # 4
        self.__open_file_mode = 'wb' # 5
        self.__content_length = 0 # 6 the whole file content length
        self.__content_length_request = 0 # the request file content length
        self.__file_size_unit = 'byte' # 7
        self.__file_size = 0

        self.__file_name_exists = False # 8
        self.__file_already_download = False
        # if not accept range, we don't need tmp_file
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

    #def set_internet_available(self):
    #    assert self.__url
    #    try:
    #        req = requests.head(self.__url, timeout=10)
    #        if req.ok:
    #            self.__internet_available = True
    #    except requests.ConnectionError:
    #        print('No internet connection available')
    #        self.__leave_now = True
    #    except :
    #        raise
    #        sys.exit()

    def do_leave_now(self):
        return self.__leave_now

    def set_all_info(self, url, file_name, file_path):
        assert url
        assert file_name
        self.set_url(url) # 1
        # self.set_internet_available()
        self.set_file_path_and_name(file_name, file_path) # 2
        self.set_server_response_header() # 3
        # if internet is not available, leave
        if self.do_leave_now():
            return 

        self.set_accept_range() # 4
        self.set_open_file_mode() # 5
        self.set_content_length() # 6
        self.set_file_size_unit() # 7 
        self.set_file_name_exists() # 8
        self.set_tmp_file_name_exists() # 9
        self.set_tmp_file_name_size() # 10
        self.set_range_headers() # 11
        self.set_all_file_size() # 
        self.set_file_modified() # 13 @TODO
        self.set_requests_stream_object() # 12

    def isFileDownloaded(self):
        return self.__file_already_download

    def set_all_file_size(self):
        self.__all_file_size = self.__content_length

    def set_url(self, url):
        assert url
        self.__url = url

    def set_server_response_header(self):
        assert self.__url
        try:
            req = requests.head(self.__url, 
                            headers={'Range': 'bytes=0-'},
                            timeout=10)
            if req.ok:
                self.__internet_available = True
                self.__server_response_headers = req.headers
        except requests.ConnectionError:
            print('No internet connection available')
            self.__leave_now = True
        except :
            raise
            sys.exit()

    def set_accept_range(self):
        assert self.__url
        assert self.__server_response_headers
        status = self.__server_response_headers.get('Accept-Ranges')
        status_length = self.__server_response_headers.get('Content-Length')
        if status != None:
            self.__accept_range = True
            do_range = requests.head(self.__url, headers={'Range': 'bytes=2-'})
            do_range_length = do_range.headers.get('Content-Length')
            if status_length == do_range_length:
                self.__accept_range = False

    def set_open_file_mode(self):
        if self.__accept_range:
            self.__open_file_mode = 'ab'
            self.__real_write_file = self.__tmp_file_final
        else:
            self.__real_write_file = self.__file_final

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
        path = self.__file_final # os.path.join(self.__file_path, self.__file_name)
        self.__file_name_exists = os.path.exists(path)
        if self.__file_name_exists:
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

        if not self.__accept_range:
            return

        path = self.__tmp_file_final
        self.__tmp_file_name_exists = os.path.exists(path)
        
    def set_tmp_file_name_size(self):
        if not self.__accept_range:
            return

        if self.__tmp_file_name_exists:
            path = self.__tmp_file_final # os.path.join(self.__file_path, self.__tmp_file_name)
            self.__tmp_file_name_size = os.path.getsize(path)

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
        else :
            self.__file_size_unit = 'byte'
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

        # if downloaded and not Modified, return
        if self.__file_already_download:
            return 

        if not self.__accept_range:
            times = 2
            # Try: if error, then try
            while True:
                if times <=0 :
                    self.__leave_now = True
                    return  

                try:
                    self.__requests_stream_object = \
                            requests.get(self.__url, stream=True, \
                                         timeout=20)
                    break
                except requests.exceptions.ConnectionError as e:
                    print('An error occured: %s' % e)
                    with open(self.__logfile, 'a') as logHandler:
                        logHandler.write('Set Requests Stream Object \
                                         Error: %s\n' % e)
                    time.sleep(random.randint(5, 15))
                    times -= 1
                
            self.__requests_ok = self.__requests_stream_object.ok
            self.__content_length_request = self.__content_length
        else:
            assert self.__range_headers
            self.__requests_stream_object = requests.get(self.__url, 
                        stream=True, headers=self.__range_headers)
            self.__requests_ok = self.__requests_stream_object.ok
            self.__content_length_request = self.__requests_stream_object\
                    .headers.get('Content-Length')

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

    def set_range_headers(self):
        if self.__tmp_file_name_size >= 0:
            self.__range_headers = {'Range': 'bytes=%d-' % self.__tmp_file_name_size}

    def delete_file(self, file_absolute_path):
        if os.path.exists(file_absolute_path):
            os.remove(file_absolute_path)
        else:
            print('File %s Doesnot Exist' % self.__file_name)

    def set_file_modified(self):
        # assert self.__content_length
        # assert self.__all_file_size
        if not self.__all_file_size:
            self.__file_modified = False
            self.__file_already_download = True
            return 

        if self.__file_name_exists:
            local_file_size = os.path.getsize(self.__file_final)
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
            if local_file_size != self.__all_file_size:
                self.__file_modified = True
                self.__file_already_download = False

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
        # assert self.__content_length
        id = 0 if not id else id

        if not self.__content_length:
            return 0

        end_second = int(time.time())
        time_segment = end_second - start_second
        if time_segment <= 0:
            return 0

        download_speed = already_download_size / float(time_segment)
        left_time = (self.__all_file_size - already_download_size - self.__tmp_file_name_size) / float(download_speed)
        left_time_str = self.calculate_time(left_time)

        (already_download, already_download_unit) = \
                self.tranform_file_size_and_unit(already_download_size)
        (speed, speed_unit) = \
                self.tranform_file_size_and_unit(download_speed)
        percent = self.calculate_percent(already_download_size + \
                                         self.__tmp_file_name_size, 
                                         self.__all_file_size)

        if percent > 100:
            print self.__all_file_size
            print already_download_size
            print self.__tmp_file_name_size
            print self.__content_length_request
            print self.__all_file_size - self.__tmp_file_name_size
            assert self.__url
            assert self.__file_name
            assert self.__file_path
            assert self.__file_already_download
            self.delete_file(self.__file_path, self.__tmp_file_name)
            self.download(self.__url, self.__file_name, self.__file_path, id)
            sys.stdout.write('Error: Percent lager than 100%\n')
            sys.stdout.flush()
            return 101

        # ID:1 File: Hear.h [ 12.3MB ] [ 27% ] [ Speed: 123kb/s Left Time: 00:00:00]
        #status = 'ID:%d File: %s [ %.2f %s ] [ %3.2f%% ] [ Speed: %.2f %s left Time: %f ]' % \
        #            (id, self.__file_name, already_download, already_download_unit, percent, speed, speed_unit, left_time)
        status = '%s%s [%s%% ] [Speed:%s%s/s Timeleft: %s]' % \
                    (
                        ('%03.2f' % already_download).rjust(7),
                        already_download_unit,
                        ('%03.2f' % percent).rjust(6),
                        ('%03.2f' % speed).rjust(6),
                        speed_unit,
                        left_time_str,
                    )

        sys.stdout.write(status.ljust(len(status)+3, ' ') + '\r')
        sys.stdout.flush()
        

    def download(self, url, file_name, file_path=None, id=0, ids=0):
        '''
            download main
        ''' 
        if not ids and id:
            ids = id
        # assert when url, file_name is None
        assert url
        assert file_name
        self.reset()
        self.set_all_info(url, file_name, file_path)

        if self.do_leave_now():
            return (0, 0)

        if self.isFileDownloaded():
            sys.stdout.write('ID: [%d/%d] Dir: %s ' % 
                             (id, ids, self.__file_path))
            sys.stdout.write('File: %s already downloaded\n' % 
                             self.__file_name)
            sys.stdout.flush()
            return (self.__content_length, 0)

        if not self.__requests_ok:
            sys.stdout.write('Error: Request Error!\n')
            sys.stdout.flush()
            with open(os.path.join(self.__logdir, 
                        self.__logfile), 'a') as log:
                log.write('Error Download: ' +
                         self.__url + '\n')
            return (self.__content_length, 0)

        if self.__file_modified:
            sys.stdout.write('Modified: %s has been Modified\n' % self.__file_name)
            sys.stdout.flush()

        #print self.__file_already_download
        #assert self.__file_already_download

        assert self.__server_response_headers
        assert self.__requests_stream_object
        assert self.__file_name
        assert self.__file_final
        assert self.__open_file_mode

        (all_size, all_size_unit) = \
                self.tranform_file_size_and_unit(self.__all_file_size)
        dir_log = 'ID:[%d/%d] Dir: %s' % (
                        id, ids, 
                        self.__file_path.ljust(50),
                    )
        file_log = 'File: %s [ %.2f %s]' % ( 
                        self.__file_name, 
                        all_size,
                        all_size_unit,
                        )
        print(dir_log.ljust(50))
        print(file_log.ljust(50))

        tf = ''
        file_size_dl = 0
        #if self.__accept_range and self.__tmp_file_name_size:
        #    file_size_dl = self.__tmp_file_name_size
        try:
            tf = open(self.__tmp_file_final, self.__open_file_mode)
            response = self.__requests_stream_object
            start_second = int(time.time())
            every_second = start_second

            for block in response.iter_content(8192):
                if not block:
                    break
                tf.write(block)
                file_size_dl += len(block)
                if time.time() >= every_second + 0.5:
                    self.print_status(file_size_dl, start_second, id)
                    every_second = time.time()
            tf.close()
        except socket.timeout:
            print('Error: socket.timeout')
            tf.close()
            return (self.__all_file_size, 0)
        except :
            raise
            tf.close()
            print("Something Wrong!")

        self.rename_old_to_new(self.__tmp_file_final, self.__file_final)

        return (self.__all_file_size, file_size_dl)

    @staticmethod
    def usage(command):
        print('NAME:')
        print('  %s - The Download Class write by python.\n' % command)
        print('DESCRIPTION:')
        print('  %s is a Simple Download Class write by python depends \
              on python-requests. Authored by Cole Smith.\n' % command)
        print('USAGE:')
        print('  %s -u URL -n NAME [ -p PATH | -i ID ]\n' % command)
        print('OPTIONS:')
        print('  -h, --help       Get help about usage and description.')
        print('  -i, --id ID      Specify the download id you want.')
        print('  -n, --name NAME  Specify the file name you want to be stored as. This field must not be None.')
        print('  -p, --path PATH  Specify the filepath where you want to store the file.')
        print('  -u,--url URL     Your download file\'s url.This field \
              must not be None.')
        print('  -v, --version    Get download class version.')

if __name__ == '__main__':
    import getopt

    opts = ''
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hu:n:p:i:v:',
            ['help', 'url', 'name', 'path', 'id', 'version']
            )
    except getopt.GetoptError:
        # print('Get Opt Error')
        sys.stdout.write('Get Opt Error\n')
        sys.stdout.write('%s -h for help\n' % sys.argv[0])
        sys.stdout.flush()
        sys.exit(-1)
    finally:
        if opts == []:
            Download.usage(sys.argv[0])
            sys.exit()

    url = None
    name = None
    path = None
    id = 0
    for o, a in opts:
        if o in ('-h', '--help'):
            Download.usage(sys.argv[0])
            sys.exit()
        if o in ('-v', '--version'):
            sys.stdout.write('%s Version %s\n' % (sys.argv[0], VERSION))
            sys.stdout.flush()
            sys.exit()
        if o in ('-u', '--url'):
            url = a
        if o in ('-n', '--name'):
            name = a
        if o in ('-p', '--path'):
            path = a
        if o in ('-i', '--id'):
            id = int(a)

    if url==None or name==None:
        sys.stdout.write('url and file name must be specified\n')
        sys.stdout.flush()
        sys.exit()

    OO = Download()
    OO.download(url, name, path, id)
