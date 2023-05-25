import os
import sys
import csv
import time


class Log_function:
    def __init__(self):
        super().__init__()
        self.fp = None
        self.file_open_time = None
        self.file_name = None
        self.file_path = None

        self.exe_path = os.path.abspath(".")

    def make_directory(self, folder_path=''):
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # else:
            #     print("해당 폴더 이미 존재")
            return True
        except Exception as e:
            return False

    def log_save(self, msg_list=[]):
        now_e = time.time()
        now = time.localtime()
        wr = None

        if self.file_open_time is None:
            self.file_open_time = time.time()

        if self.file_path is None:
            file_name = (str("Log\system_log_%04d-%02d-%02d_%02d-%02d-%02d.csv" %
                                     (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)))

            self.file_path = os.path.join(self.exe_path, file_name)
            self.file_open_time = time.time()
            self.fp = open(self.file_path, 'a', newline='')
            wr = csv.writer(self.fp)
            wr.writerow(['TIME', 'OPCODE', 'ACK/NACK', 'REASON'])
            self.fp.close()

        file_delay = now_e - self.file_open_time
        if file_delay > 600:
            file_name = (str("Log\system_log_%04d-%02d-%02d_%02d-%02d-%02d.csv" %
                                  (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)))
            self.file_path = os.path.join(self.exe_path, file_name)
            self.file_open_time = time.time()

            self.fp = open(self.file_path, 'a', newline='')
            wr = csv.writer(self.fp)
            wr.writerow(['TIME', 'OPCODE', 'ACK/NACK', 'REASON'])
            wr.writerow(msg_list)
        else:
            self.fp = open(self.file_path, 'a', newline='')
            wr = csv.writer(self.fp)
            wr.writerow(msg_list)

        self.fp.close()

    def log_path(self):
        return self.file_path

