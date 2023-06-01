import os.path
import sys
from PyQt5.QtCore    import QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *

import time
from datetime import datetime
import queue
from multiprocessing import Process
import threading
# import win32api

import numpy as np
import cv2
import math

from db import DB_function
from Socket import Socket_function
from other import Other_function
from log import Log_function
# statis window
from status_function import Status_function

# RGB
# 주황 : rgb(244,143,61)
# 남색 : rgb(40,43,48)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class main_function(QWidget):
    def __init__(self, ui):
        super().__init__()

        self.ui = ui

        self.db = DB_function()
        self.sock = Socket_function()
        self.ot = Other_function()
        self.log = Log_function()
        # region status window
        self.status = Status_function()
        # endregion

        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.time_bar_timeout)

        # system scenario value
        self.client_test = None
        self.client_connect = None
        self.status_connect = None    # value_setting
        self.status_disconnect = None # value_setting
        self.client_request_time = None
        self.recv_count = None
        self.fe_send_time = None
        self.fe_check = None
        self.fe_num = None
        self.read_thread = None
        # self.outbreak_thread = None

        self.request_timer = QTimer()
        self.request_timer.start(5000)
        self.request_timer.timeout.connect(self.request_check_timer)

        self.outbreak_timer = QTimer()
        self.outbreak_timer.start(1000)
        self.outbreak_timer.timeout.connect(self.read_outbreak_data)

        # S/W value
        self.local_ip = None
        # self.external_ip = None
        self.center_ip = None
        self.db_ip = None
        self.db_port = None
        self.db_id = None
        self.db_pw = None
        self.db_name = None
        self.controller_type = None
        self.controller_index = None
        self.controller_station = None
        self.client_socket = None
        self.frame_number_04 = None
        self.frame_number_16 = None
        self.connect_time = None
        self.sync_time = None
        self.outbreak_send_Last_time = None
        self.outbreak_cycle = None
        self.last_outbreak_status = None
        self.last_send_outbreak = None
        self.lane_num = None
        self.collect_cycle = None
        self.category_num = None
        self.use_ntraffic = None
        self.max_distance = None
        self.node_interval = None
        self.share_interval = None
        self.use_category_speed = None
        self.use_unexpected = None
        self.individual_traffic_data = None
        self.traffic_data = None
        self.ntraffic_data = None
        self.speed_data = None
        self.controllerBox_state_list = None
        self.congestion_criterion = None
        self.congestion_cycle = None
        self.zone_criterion = None
        self.m_log_save = None

        self.value_setting()

        self.set_ui()
        self.ui_event()
        # auto start
        # init_thread = threading.Thread(target=self.auto_initialize, args=(), daemon=True)
        # init_thread.start()

    def auto_initialize(self):
        # DB Connect Part
        db_conn = False
        while not db_conn:
            print("DB connect ...")
            result = self.db_connect_btn_click()
            if result:
                db_conn = True
            time.sleep(1)
        print("DB connect success")

        # Socket Open Part
        socket_conn = False
        while not socket_conn:
            print("Socket open ...")
            result = self.socket_open_btn_click()
            if result:
                socket_conn = True
            time.sleep(1)

    def value_setting(self):
        # system scenario value
        self.fe_check = True
        self.fe_num = 0
        self.read_thread = []
        # self.client_test = []
        self.status_connect = QPixmap()
        self.status_disconnect = QPixmap()
        self.status_connect.load(resource_path('connect_1.png'))
        self.status_disconnect.load(resource_path('disconnect_1.png'))

        # S/W value
        self.client_connect = False
        self.local_ip = '127.000.000.001'
        self.center_ip = '000.000.000.000'
        self.controller_type = 'VD'
        self.controller_index = self.ot.get_controller_number(self.ui.cont_num_edit.text())
        self.controller_station = self.controller_type + self.controller_index
        self.lane_num = 6
        self.collect_cycle = 30
        self.category_num = [0, 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111]
        self.use_ntraffic = 1
        self.use_category_speed = 1
        self.max_distance = 200  # 최대검지거리
        self.node_interval = 25  # 셀 간격
        self.share_interval = 5  # 점유율 간격
        self.outbreak_cycle = 60
        self.use_unexpected = 1
        self.congestion_criterion = 50
        self.congestion_cycle = 30
        self.zone_criterion = 10
        self.m_log_save = True
        self.status.get_data(max_distance=self.max_distance,
                             lane=self.lane_num,
                             congestion_criterion=self.congestion_criterion,
                             node_interval=self.node_interval)

    def time_bar_timeout(self):
        now = time.localtime()
        self.ui.time_bar.setText(str("%04d/%02d/%02d %02d:%02d:%02d" %
                                     (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)))

    def set_ui(self):
        # socket
        # self.ui.sock_ip_input.setText("121.190.45.181")
        # self.ui.sock_port_input.setText("30100")
        # self.ui.sock_ip_input.setText("192.168.0.7")
        # self.ui.sock_port_input.setText("30100")

        # 엠큐닉
        # self.ui.db_ip_input.setText("183.98.24.70")
        # self.ui.db_port_input.setText("53307")
        # self.ui.db_id_input.setText("admin")
        # self.ui.db_name_input.setText("hbrain_vds")

        # hbrain
        # mssql
        # self.ui.db_ip_input.setText("127.0.0.1")
        # self.ui.db_port_input.setText("1433")
        # self.ui.db_id_input.setText("sa")
        # self.ui.db_pw_input.setText("hbrain0372!")
        # self.ui.db_name_input.setText("hbrain_vds")
        # mysql
        # DB 정보 설정 후 실행 하기~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.ui.db_ip_input.setText("127.0.0.1")
        self.ui.db_id_input.setText("root")
        self.ui.db_port_input.setText("0372")
        self.ui.db_pw_input.setText("hbrain0372!")
        self.ui.db_name_input.setText("hbrain_vds")
        # self.ui.db_name_input.setEnabled(False)

        self.ui.socket_open_btn.setEnabled(False)
        self.ui.socket_save_btn.setEnabled(False)
        self.ui.congestion_change_btn.setEnabled(False)
        self.ui.status_btn.setEnabled(False)
        self.ui.socket_open_btn.setStyleSheet("color: gray;")
        self.ui.socket_save_btn.setStyleSheet("color: gray;")
        self.ui.congestion_change_btn.setStyleSheet("color: gray;")
        self.ui.status_btn.setStyleSheet("color: gray;")
        self.update_server_icon(False)
        self.update_client_icon(False)
        # self.ui.socket_open_btn.setStyleSheet("background-color:rgb(244,143,61); color: gray;")
        # self.ui.congestion_change_btn.setStyleSheet("background-color:rgb(244,143,61); color: gray;")
        # self.ui.status_btn.setStyleSheet("background-color:rgb(244,143,61); color: gray;")

        # congestion
        self.ui.congestion_criterion_edit.setValue(40)
        self.ui.congestion_criterion_edit.setSingleStep(5)
        self.ui.congestion_criterion_edit.setMinimum(10)
        self.ui.congestion_criterion_edit.setMaximum(100)

        self.ui.zone_criterion_edit.setValue(10)
        self.ui.zone_criterion_edit.setSingleStep(10)
        self.ui.zone_criterion_edit.setMinimum(10)
        self.ui.zone_criterion_edit.setMaximum(60)

        self.ui.congestion_cycle_edit.setValue(30)
        self.ui.congestion_cycle_edit.setSingleStep(10)
        self.ui.congestion_cycle_edit.setMinimum(10)
        self.ui.congestion_cycle_edit.setMaximum(60)

        # RX, TX
        self.ui.tx_table.setColumnWidth(0, 200)
        self.ui.tx_table.setColumnWidth(1, 80)
        self.ui.tx_table.setColumnWidth(2, 90)
        self.ui.tx_table.setColumnWidth(3, 210)
        self.ui.tx_table.setStyleSheet("color:rgb(244,143,61);"
                                       "background-color:rgb(40,43,48); "
                                       "font-size:12px; "
                                       "font: 'Cambria';")
        self.ui.rx_table.setColumnWidth(0, 200)
        self.ui.rx_table.setColumnWidth(1, 80)
        self.ui.rx_table.setColumnWidth(2, 90)
        self.ui.rx_table.setColumnWidth(3, 210)
        self.ui.rx_table.setStyleSheet("color:rgb(244,143,61);"
                                       "background-color:rgb(40,43,48); "
                                       "font-size:12px; "
                                       "font: 'Cambria';")

        if not self.ui.Log_check_box.isChecked():
            self.ui.Log_check_box.toggle()

    def ui_event(self):
        # region btn event
        self.ui.socket_open_btn.clicked.connect(self.socket_open_btn_click)
        self.ui.socket_save_btn.clicked.connect(self.socket_save_btn_click)
        self.ui.db_connect_btn.clicked.connect(self.db_connect_btn_click)
        self.ui.cont_num_change_btn.clicked.connect(self.cont_num_change_btn_click)
        self.ui.congestion_change_btn.clicked.connect(self.congestion_change_btn_click)
        # endregion

        # region ui event
        self.ui.Log_check_box.stateChanged.connect(self.log_check_box_check)
        # endregion

        # region test
        self.ui.status_btn.clicked.connect(self.status_btn_click)
        # endregion

        # region request btn event
        # self.ui.op_FF_btn.clicked.connect(self.op_FF_btn_click)
        # self.ui.op_FE_btn.clicked.connect(self.op_FE_btn_click)
        # self.ui.op_01_btn.clicked.connect(self.op_01_btn_click)
        # self.ui.op_04_btn.clicked.connect(self.op_04_btn_click)
        # self.ui.op_05_btn.clicked.connect(self.op_05_btn_click)
        # self.ui.op_07_btn.clicked.connect(self.op_07_btn_click)
        # self.ui.op_0C_btn.clicked.connect(self.op_0C_btn_click)
        # self.ui.op_0D_btn.clicked.connect(self.op_0D_btn_click)
        # self.ui.op_0E_btn.clicked.connect(self.op_0E_btn_click)
        # self.ui.op_0F_btn.clicked.connect(self.op_0F_btn_click)
        # self.ui.op_11_btn.clicked.connect(self.op_11_btn_click)
        # self.ui.op_12_btn.clicked.connect(self.op_12_btn_click)
        # self.ui.op_13_btn.clicked.connect(self.op_13_btn_click)
        # self.ui.op_15_btn.clicked.connect(self.op_15_btn_click)
        # self.ui.op_16_btn.clicked.connect(self.op_16_btn_click)
        # self.ui.op_17_btn.clicked.connect(self.op_17_btn_click)
        # self.ui.op_18_btn.clicked.connect(self.op_18_btn_click)
        # self.ui.op_19_btn.clicked.connect(self.op_19_btn_click)
        # self.ui.op_1E_btn.clicked.connect(self.op_1E_btn_click)
        # # test
        # self.ui.test_btn.clicked.connect(self.test_btn_click)
        # endregion

    # region status window
    def status_btn_click(self):
        self.status.show()

    # endregion

    # region btn click function
    def socket_open_btn_click(self):
        socket_info = self.db.get_socket_info(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
        cont_num, self.controller_index = self.db.get_controller_station_number_data(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
        self.controller_station = self.controller_type + self.controller_index

        if self.controller_index != '':
            self.ui.cont_num_edit.setText(str(cont_num))
            sock_ip = socket_info[0]
            sock_port = socket_info[1]

            if sock_ip is None or sock_port is None:
                self.update_Statusbar_text("Enter IP and Port and save!!")
                self.ui.socket_save_btn.setEnabled(True)
                self.ui.socket_save_btn.setStyleSheet("background-color:rgb(244,143,61); color: white;")
            else:
                self.local_ip = self.ot.make_16ip(sip=socket_info[0])
                self.update_Statusbar_text("Socket server open..")
                # ip, port 입력칸에 DB에서 읽은 값 입력
                self.ui.sock_ip_input.setText(socket_info[0])
                self.ui.sock_port_input.setText(str(socket_info[1]))
                try:
                    self.sock.socket_server_open(sock_ip, sock_port)
                    self.update_Statusbar_text("Socket server '" + sock_ip + "', '" + str(sock_port) + "' open !")
                    self.ui.sock_ip_input.setEnabled(False)
                    ##
                    # self.ui.external_sock_ip_input.setEnabled(False)
                    self.ui.sock_port_input.setEnabled(False)
                    self.ui.socket_open_btn.setEnabled(False)
                    self.ui.cont_num_edit.setEnabled(False)
                    self.ui.sock_ip_input.setStyleSheet("color: gray;")
                    self.ui.sock_port_input.setStyleSheet("color: gray;")
                    self.ui.socket_open_btn.setStyleSheet("color: gray;")
                    self.update_server_icon(True)
                    self.ui.socket_open_btn.setStyleSheet("color:gray;")
                    t = threading.Thread(target=self.client_accept_check, args=(), daemon=True)
                    t.start()
                    # Socket ip,port DB update
                    self.db.set_socket_info(socket_info=[sock_ip, sock_port], host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
                    return True
                except Exception as e:
                    self.update_Statusbar_text("socket server open fail")
                    return False
        else:
            self.ui.cont_num_edit.setText("Input Controller station number!!")
            self.update_Statusbar_text("controller number는 10자로 입력해주세요")

        return False

    def socket_save_btn_click(self):
        socket_ip = self.ui.sock_ip_input.text()
        socket_port = self.ui.sock_port_input.text()

        if socket_ip and socket_port:
            result = self.db.set_socket_info(socket_info=[socket_ip, socket_port], host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
            if result:
                self.ui.socket_save_btn.setEnabled(False)
                self.ui.socket_save_btn.setStyleSheet("color: gray;")
                self.update_Statusbar_text("Socket IP and Port save completed")

    def client_accept_check(self):
        while True:
            self.client_test = self.sock.client_accept()
            # read thread
            t = threading.Thread(target=self.read_socket_msg, args=(), daemon=True)
            self.read_thread.append(t)
            if len(self.read_thread) > 2:
                self.read_thread.pop(0)
            self.read_thread[-1].start()
            # 돌발 thread
            # self.outbreak_thread = threading.Thread(target=self.read_outbreak_data, args=(), daemon=True)
            # dt.start()
            # 파라미터값 초기화
            parameter_list = self.db.get_parameter_data(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
            if parameter_list:
                self.lane_num = parameter_list[0]
                self.collect_cycle = parameter_list[1]
                self.category_num = parameter_list[2]
                self.use_ntraffic = parameter_list[3]
                self.use_category_speed = parameter_list[4]
                max_distance_f = parameter_list[5] << 8
                max_distance_b = parameter_list[6]
                self.max_distance = max_distance_f + max_distance_b
                self.node_interval = parameter_list[7]
                self.share_interval = parameter_list[8]
                self.outbreak_cycle = parameter_list[9]
                self.use_unexpected = parameter_list[10]
            else:
                self.lane_num = 6
                self.collect_cycle = 30
                self.category_num = [0, 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111]
                self.use_ntraffic = 1
                self.use_category_speed = 1
                self.max_distance = 200
                self.node_interval = 25
                self.share_interval = 5
                self.outbreak_cycle = 60
                self.use_unexpected = 1

            self.status.get_data(lane=self.lane_num, max_distance=self.max_distance, node_interval=self.node_interval)

    def db_connect_btn_click(self):
        try:
            self.db_ip = self.ui.db_ip_input.text()
            self.db_port = self.ui.db_port_input.text()
            self.db_id = self.ui.db_id_input.text()
            self.db_pw = self.ui.db_pw_input.text()
            self.db_name = self.ui.db_name_input.text()

            self.db.create_init_DB(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')

            if self.db.db_connection_check(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8'):
                self.ui.socket_open_btn.setEnabled(True)
                self.ui.congestion_change_btn.setEnabled(True)
                self.ui.status_btn.setEnabled(True)
                self.ui.db_connect_btn.setEnabled(False)
                self.ui.socket_open_btn.setStyleSheet("background-color:rgb(244,143,61); color:white;")
                self.ui.congestion_change_btn.setStyleSheet("background-color:rgb(244,143,61); color:white;")
                self.ui.status_btn.setStyleSheet("background-color:rgb(244,143,61); color:white;")
                self.ui.db_connect_btn.setStyleSheet("color:gray;")
                self.update_Statusbar_text("DB connect success")

                self.ui.db_ip_input.setEnabled(False)
                self.ui.db_port_input.setEnabled(False)
                self.ui.db_id_input.setEnabled(False)
                self.ui.db_name_input.setEnabled(False)
                self.ui.db_pw_input.setEnabled(False)
                self.ui.db_connect_btn.setEnabled(False)
                self.ui.db_ip_input.setStyleSheet("color: gray;")
                self.ui.db_port_input.setStyleSheet("color: gray;")
                self.ui.db_id_input.setStyleSheet("color: gray;")
                self.ui.db_name_input.setStyleSheet("color: gray;")
                self.ui.db_pw_input.setStyleSheet("color: gray;")
                self.ui.db_connect_btn.setStyleSheet("color:gray;")

                # ui setting
                temp = self.db.get_congestion_info(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
                # temp = [지정체 기준 값, 지정체 read cycle]
                self.congestion_criterion = int(temp[0])
                self.congestion_cycle = int(temp[1])
                self.status.get_data(congestion_criterion=self.congestion_criterion)
                self.ui.congestion_criterion_value.setText(str(self.congestion_criterion))
                self.ui.zone_criterion_value.setText(str(self.node_interval))
                self.ui.congestion_cycle_value.setText(str(self.congestion_cycle))
                return True
        except Exception as e:
            self.update_Statusbar_text("DB connect fail")

        return False
        # self.ui.db_ip_input.setEnabled(False)
        # self.ui.db_port_input.setEnabled(False)
        # self.ui.db_id_input.setEnabled(False)
        # self.ui.db_name_input.setEnabled(False)
        # self.ui.db_pw_input.setEnabled(False)
        # self.ui.db_connect_btn.setEnabled(False)
        # self.ui.db_ip_input.setStyleSheet("color: gray;")
        # self.ui.db_port_input.setStyleSheet("color: gray;")
        # self.ui.db_id_input.setStyleSheet("color: gray;")
        # self.ui.db_name_input.setStyleSheet("color: gray;")
        # self.ui.db_pw_input.setStyleSheet("color: gray;")
        # self.ui.db_connect_btn.setStyleSheet("color:gray;")
        #
        # # ui setting
        # temp = self.db.get_congestion_info(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
        # # temp = [지정체 기준 값, 간격 기준 값, 지정체 read cycle]
        # self.congestion_criterion = int(temp[0])
        # self.zone_criterion = int(temp[1])
        # self.congestion_cycle = int(temp[2])
        # self.status.get_data(congestion_criterion=self.congestion_criterion, zone_criterion=self.zone_criterion)
        # self.ui.congestion_criterion_value.setText(str(self.congestion_criterion))
        # self.ui.zone_criterion_value.setText(str(self.zone_criterion))
        # self.ui.congestion_cycle_value.setText(str(self.congestion_cycle))

    def cont_num_change_btn_click(self):
        # cont_num = self.ot.get_controller_number(self.ui.cont_num_edit.text())
        cont_num = self.ui.cont_num_edit.text()
        self.db.set_controller_station_number_data(cont_num=cont_num, host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')

        # type : VD
        self.controller_index = self.ot.get_controller_number(cont_num)
        self.controller_station = self.controller_type + self.controller_index

        if self.controller_index == '':
            self.update_Statusbar_text("controller number는 10자로 입력해주세요")
        else:
            self.update_Statusbar_text("controller number: " +
                                       str(hex(ord(self.controller_index[0]))) + "/" +
                                       str(hex(ord(self.controller_index[1]))) + "/" +
                                       str(hex(ord(self.controller_index[2]))) + "/" +
                                       str(hex(ord(self.controller_index[3]))) + "/" +
                                       str(hex(ord(self.controller_index[4]))))
    def congestion_change_btn_click(self):
        change_list = []
        change_list.append(self.ui.congestion_criterion_edit.value())
        change_list.append(self.ui.zone_criterion_edit.value())
        change_list.append(self.ui.congestion_cycle_edit.value())

        self.db.set_congestion_info(change_list, host=self.db_ip, port=int(self.db_port), user=self.db_id,
                                           password=self.db_pw, db=self.db_name, charset='utf8')

        # ui setting
        temp = self.db.get_congestion_info(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
        # temp = [지정체 기준 값, 간격 기준 값, 지정체 read cycle]
        self.congestion_criterion = int(temp[0])
        self.congestion_cycle = int(temp[2])
        self.status.get_data(congestion_criterion=self.congestion_criterion)
        self.ui.congestion_criterion_value.setText(str(self.congestion_criterion))
        self.ui.congestion_cycle_value.setText(str(self.congestion_cycle))
    # endregion

    # region ui click function
    def log_check_box_check(self):
        if self.ui.Log_check_box.isChecked():
            self.m_log_save = True
        else:
            self.m_log_save = False

        # print(self.m_log_save)
    # endregion

    # region socket_msg

    def read_socket_msg(self):
        try:
            while 1:
                recv_msg = self.sock.socket_read()
                if recv_msg == '':
                    # if len(self.read_thread) > 1:
                    # self.read_thread.pop(0)
                    # self.sock.client_socket_close()
                    break
                else:
                    self.parsing_msg(recv_msg)
                    # print(recv_msg.decode('utf-16'))
            # self.sock.client_socket_close()
        except Exception as e:
            print("read_socket_msg error: ", e)
        self.client_connect = False
        self.update_client_icon(False)
        print("client close")

    # 돌발
    def read_outbreak_data(self):
        # while self.client_connect:
        if self.client_connect:
            if self.use_unexpected == 1:

                # --------지정체 계산-----------------------------------------------------------------------------------
                lane_cell_num = 10  # 디폴트 값 초기화
                if self.node_interval > 0:
                    lane_cell_num = self.max_distance / self.node_interval  # 차선별 구역 수
                if self.client_connect:
                    sync_time = time.time()
                    cell_data, congestion_list = self.db.get_congestion_data(cycle=self.congestion_cycle,
                                                                             congestion=self.congestion_criterion,
                                                                             node_interval=self.node_interval,
                                                                             sync_time=sync_time,
                                                                             host=self.db_ip, port=int(self.db_port),
                                                                             user=self.db_id, password=self.db_pw,
                                                                             db=self.db_name)
                    if congestion_list:
                        outbreak_time = datetime.now()
                        self.db.insert_outbreak(congestion_list=congestion_list,
                                                input_time=outbreak_time,
                                                zone = self.lane_num,
                                                node_interval=self.node_interval,
                                                host=self.db_ip, port=int(self.db_port), user=self.db_id,
                                                password=self.db_pw, db=self.db_name)
                    if cell_data:
                        self.status.get_data(congestion_data=cell_data)

                    # -------DB Table read----------------------------------------------------------------------------------
                    outbreakdata = self.db.get_outbreak(lane=self.lane_num,
                                                        cycle=self.outbreak_cycle,
                                                        host=self.db_ip, port=int(self.db_port), user=self.db_id,
                                                        password=self.db_pw, db=self.db_name)

                    # ------outBreak send-----------------------------------------------------------------------------------
                    if outbreakdata:
                        # outbreak = [ [시간, 차선, 클래스, 거리, 상하행], [시간, 차선, 클래스, 거리, 상하행], ... ]
                        outbreak_status = min([data[2] for data in outbreakdata])  # 위험 순위가 제일 낮은 돌발값 (돌발 생성)

                        # print("************************************")
                        # print("돌발: ", outbreakdata)
                        # print("현재 제일 높은 위험 순위: ", outbreak_status)
                        outbreak_temp = []

                        if self.last_outbreak_status is None:  # 최근 돌발 상태가 없으면
                            # print("현재 진행중인 돌발 없음")
                            self.last_outbreak_status = outbreak_status  # last_outbreak_status = 생성된 돌발값 (outbreak_status) 업데이트

                        elif outbreak_status < self.last_outbreak_status:  # 위험 순위 비교 (생성된 돌발 < 최근 돌발 상태)
                            # print("새로 생성된 돌발 < 최근 돌발 상태")
                            self.last_outbreak_status = outbreak_status  # last_outbreak_status = 생성된 돌발값 (outbreak_status) 업데이트

                        elif outbreak_status == self.last_outbreak_status:  # 위험 순위 비교 (생성된 돌발 == 최근 돌발 상태)
                            # print("새로 생성된 돌발 == 최근 돌발 상태")
                            pass

                        elif outbreak_status > self.last_outbreak_status:  # 위험 순위 비교 (생성된 돌발 > 최근 돌발 상태)
                            # print("새로 생성된 돌발 > 최근 돌발 상태")         # 위험 순위 60초가 지나서 그 다음 위험 순위로 내려감
                            # print("최근 돌발 60초 초과 ")
                            self.last_outbreak_status = outbreak_status

                        for i, data in enumerate(outbreakdata):
                            if data[2] == outbreak_status:  # outbreakdata중에서 클래스가 outbreak_status와 같은 값들만
                                outbreak_temp.append(data)

                        # print("1. self.last_send_outbreak: ", self.last_send_outbreak)

                        if self.last_send_outbreak is None:
                            self.last_send_outbreak = outbreak_temp
                        # print("outbreak_temp:        ", outbreak_temp)

                        for temp in outbreak_temp[:]:
                            if temp in self.last_send_outbreak:
                                outbreak_temp.remove(temp)

                        if outbreak_temp:
                            location = self.db.get_location_data(host=self.db_ip, port=int(self.db_port),
                                                                 user=self.db_id, password=self.db_pw, db=self.db_name,
                                                                 charset='utf8')
                            self.sock.send_19_res_msg(self.local_ip, self.center_ip, self.controller_type,
                                                      self.controller_index, outbreak_temp, location)
                            self.update_TX_Log(chr(0x19), [0])
                            for i in outbreak_temp:
                                self.last_send_outbreak.append(i)

                        # print("outbreak_temp_remove: ", outbreak_temp)
                        # print("2. self.last_send_outbreak: ", self.last_send_outbreak)

                        out_time = datetime.fromtimestamp(sync_time - self.outbreak_cycle)
                        for data in self.last_send_outbreak[:]:
                            if data[0] < out_time:
                                self.last_send_outbreak.remove(data)

    def parsing_msg(self, recv_msg):
        print("---------------------------------------------------------------------------")
        d_recv_msg = recv_msg.decode('utf-16')
        # for i in range(len(d_recv_msg)):
        #     print(i,": ", ord(d_recv_msg[i]))
        if (d_recv_msg[43] == chr(0xFE)) or (d_recv_msg[43] == chr(0x19)):
            if d_recv_msg[44] == chr(0x06): # ack
                self.update_RX_Log(d_recv_msg[43], [1])
            elif d_recv_msg[44] == chr(0x15): # nack
                self.update_RX_Log(d_recv_msg[43], [2, d_recv_msg[45]])
        else:
            self.update_RX_Log(d_recv_msg[43], [0])

        # nack 확인
        result = self.ot.nack_find(msg=d_recv_msg, csn=self.controller_station)

        if result[0] == True:
            msg_op = d_recv_msg[43]
            msg_sender_ip = d_recv_msg[0:15]
            destination_ip = d_recv_msg[16:31]

            # 수신메시지의 목적지 IP == local IP --> RX 메시지
            if destination_ip == self.local_ip:
                self.center_ip = msg_sender_ip
                self.client_request_time = time.time()
                # print("RX_msg: [", recv_msg.decode('utf-16'), "]")
                # print("RX: [", recv_msg, "]")
                print("RX OPCode: ", "0x{:02X}".format(ord(msg_op)))
                if msg_op == chr(0xFF):
                    self.client_connect = True
                    # client connect icon
                    self.update_client_icon(True)

                    # response
                    self.sock.send_FF_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index)
                    self.update_TX_Log(chr(0xFF), [1])
                    # if not self.outbreak_thread.is_alive():
                    #     self.outbreak_thread.start()
                    self.connect_time = time.time()
                elif msg_op == chr(0xFE):
                    self.fe_check = True
                    print('0xFE response')
                elif msg_op == chr(0x01):
                    # self.device_sync(msg_op, d_recv_msg)
                    self.frame_number_04 = d_recv_msg[44]
                    self.frame_number_16 = d_recv_msg[44]
                    self.sync_time = time.time()
                    print("not ack")
                elif msg_op == chr(0x04):
                    self.traffic_data = self.db.get_traffic_data(cycle=self.collect_cycle, sync_time=self.sync_time, lane=self.lane_num, host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name)
                    if self.traffic_data != [] and self.frame_number_04 is not None:
                        # print
                        print("0x04 교통량: ", self.traffic_data)
                        self.sock.send_04_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, self.frame_number_04, self.lane_num, self.traffic_data)
                        self.update_TX_Log(chr(0x04), [1])
                        # self.frame_number_04 = None
                    else:
                        list = [False, chr(0x04), chr(0x06)]
                        self.sock.send_nack_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, list)
                        self.update_TX_Log(chr(0x04), [2, list[2]])
                elif msg_op == chr(0x05):
                    self.speed_data = self.db.get_speed_data(sync_time=self.sync_time, lane=self.lane_num, cnum=self.category_num, host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name)
                    if self.speed_data:
                        # print
                        print("0x05 차로 카테고리별 속도: ", self.speed_data)
                        if self.use_category_speed:
                            self.sock.send_05_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, self.speed_data)
                            self.update_TX_Log(chr(0x05), [1])
                elif msg_op == chr(0x07):
                    self.ntraffic_data = self.db.get_ntraffic_data(lane=self.lane_num, host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name)
                    if self.ntraffic_data:
                        # print
                        print("0x07 누적교통량: ", self.ntraffic_data)
                        if self.use_ntraffic:
                            self.sock.send_07_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, self.ntraffic_data)
                            self.update_TX_Log(chr(0x07), [1])
                elif msg_op == chr(0x0C):
                    self.device_sync(msg_op, d_recv_msg)
                    self.sock.send_0C_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index)
                    self.update_TX_Log(chr(0x0C), [1])
                elif msg_op == chr(0x0D):
                    self.sock.send_0D_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index)
                    self.update_TX_Log(chr(0x0D), [1])
                elif msg_op == chr(0x0E):
                    self.device_sync(msg_op, d_recv_msg)
                    self.sock.send_0E_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index)
                    self.update_TX_Log(chr(0x0E), [1])
                elif msg_op == chr(0x0F):
                    index = int(ord(d_recv_msg[44]))
                    self.sock.send_0F_res_msg(self.local_ip, self.center_ip, self.controller_type,
                                              self.controller_index, index,
                                              self.lane_num, self.collect_cycle, self.category_num, self.use_ntraffic,
                                              self.use_category_speed, self.max_distance, self.node_interval,
                                              self.share_interval, self.outbreak_cycle, self.use_unexpected)
                    self.update_TX_Log(chr(0x0F), [1])
                elif msg_op == chr(0x11):
                    request_time = time.time()
                    if self.connect_time is not None:
                        self.sock.send_11_res_msg(self.local_ip, self.center_ip, self.controller_type,
                                                  self.controller_index, self.connect_time, request_time)
                        self.update_TX_Log(chr(0x11), [1])
                    else:
                        list = [False, chr(0x11), chr(0xFF)]
                        self.sock.send_nack_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, list)
                        self.update_TX_Log(chr(0x11), [2, list[2]])
                elif msg_op == chr(0x13):
                    self.sock.send_13_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, d_recv_msg)
                    self.update_TX_Log(chr(0x13), [1])
                elif msg_op == chr(0x15):
                    version_list = self.db.get_version_num(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name)
                    if version_list:
                        self.sock.send_15_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, version_list)
                        self.update_TX_Log(chr(0x15), [1])
                    else:
                        list = [False, chr(0x15), chr(0x06)]
                        self.sock.send_nack_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, list)
                        self.update_TX_Log(chr(0x15), [2, list[2]])
                elif msg_op == chr(0x16):
                    self.individual_traffic_data = self.db.get_individual_traffic_data(cycle=self.collect_cycle, sync_time=self.sync_time, lane=self.lane_num, host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name)
                    if self.individual_traffic_data != [] and self.frame_number_16 is not None:
                        # print
                        print("0x16 개별차랑: ", self.individual_traffic_data)
                        self.sock.send_16_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, self.frame_number_16, self.individual_traffic_data)
                        self.update_TX_Log(chr(0x16), [1])
                        # self.frame_number_16 = None
                    else:
                        list = [False, chr(0x16), chr(0x06)]
                        self.sock.send_nack_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, list)
                        self.update_TX_Log(chr(0x16), [2, list[2]])
                elif msg_op == chr(0x17):
                    ptz_info = self.db.get_ptz_info(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name, charset='utf8')
                    ptz_url = 'rtsp://' + ptz_info[0] + ':' + ptz_info[1] + '@' + ptz_info[2] + ':' + ptz_info[3]
                    try:
                        # rtsp://admin:1q2w3e4r!@183.99.41.239:554
                        cap = cv2.VideoCapture(ptz_url)
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                        _, img = cap.read()
                    except Exception as e:
                        img = None

                    if str(type(img)) != "<class 'NoneType'>":
                        self.sock.send_17_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, img)
                        self.update_TX_Log(chr(0x17), [1])
                    else:
                        list = [False, chr(0x17), chr(0x06)]
                        self.sock.send_nack_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, list)
                        self.update_TX_Log(chr(0x17), [2, list[2]])
                elif msg_op == chr(0x18):
                    result = self.device_sync(msg_op, d_recv_msg)
                    if True in result:
                        self.sock.send_18_res_msg(self.local_ip, self.center_ip, self.controller_type,
                                                  self.controller_index)
                        self.update_TX_Log(chr(0x18), [1])
                    else:
                        list = result
                        self.sock.send_nack_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, list)
                        self.update_TX_Log(chr(0x18), [2, list[2]])
                elif msg_op == chr(0x19):
                    # msg read와 별개의 스레드를 돌면서 돌발 테이블을 계속 확인.
                    # 확인하다가 걸리면 밑에 코드 사용
                    # send함수 파라미터로 보낼 데이터 전송해야함 -> db모듈에서 get
                    if self.use_unexpected == 1:
                        self.sock.send_19_res_msg(self.local_ip, self.center_ip, self.controller_type,
                                                  self.controller_index)
                        self.update_TX_Log(chr(0x19), [1])
                elif msg_op == chr(0x1E):
                    self.controllerBox_state_list = self.db.get_controllerBox_state_data(host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name)
                    if self.controllerBox_state_list:
                        self.sock.send_1E_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, self.controllerBox_state_list)
                        self.update_TX_Log(chr(0x1E), [1])
                    else:
                        list = [False, chr(0x1E), chr(0x06)]
                        self.sock.send_nack_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, list)
                        self.update_TX_Log(chr(0x1E), [2, list[2]])

            elif destination_ip == self.center_ip:
                print("msg   : [", recv_msg.decode('utf-16'), "]")
            else:
                print("TX_msg: [", recv_msg.decode('utf-16'), "]")
        else:
            self.center_ip = d_recv_msg[0:15]
            msg_op = d_recv_msg[43]
            list = result
            print("???: ", list)
            self.sock.send_nack_res_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index, list)
            self.update_TX_Log(msg_op, [2, list[2]])   # chr(0xFF)아님..
    # endregion

    def request_check_timer(self):
        if self.client_connect:
            self.ui.client_status_bar.setStyleSheet("margin:10px; color:rgb(146, 208, 80);") # 녹색
            self.ui.client_status_bar.setText("Client connecting")
            now_time = time.time()
            time_delay = now_time - self.client_request_time
            # print("delay: ", time_delay)

            if (time_delay > 300) and self.fe_check:
                self.sock.send_FE_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index)
                self.update_TX_Log(chr(0xFE), [0])
                self.fe_send_time = time.time()
                self.fe_check = False

            if not self.fe_check:
                fe_delay = now_time - self.fe_send_time
                if (fe_delay > 5) and (self.fe_num < 2):
                    self.sock.send_FE_msg(self.local_ip, self.center_ip, self.controller_type, self.controller_index)
                    self.update_TX_Log(chr(0xFE), [0])
                    self.fe_send_time = time.time()
                    self.fe_num += 1
                # else:
                #     self.client_connect = False
                #     self.fe_num = 0
            if self.fe_num == 2:
                self.client_connect = False
                self.fe_num = 0
                self.fe_check = True
                self.update_client_icon(False)
                self.ui.client_status_bar.setStyleSheet("margin:10px; color:rgb(102,186,255);") # 하늘색
                self.ui.client_status_bar.setText("Client disconnecting")
        else:
            print("Waiting for Client...")
            self.ui.client_status_bar.setStyleSheet("margin:10px; color:rgb(102,186,255);") # 하늘색
            self.ui.client_status_bar.setText("Waiting for Client...")

    def device_sync(self, op, msg):
        lane = 1
        # if op == chr(0x01):
        #     self.frame_number_set = msg[44]
        if op == chr(0x0C):
            self.lane_num = 6
            self.collect_cycle = 30
            self.category_num = [0, 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111]
            self.use_ntraffic = 1
            self.use_category_speed = 1
            self.max_distance = 200  # 최대검지거리
            self.node_interval = 25  # 셀 간격
            self.share_interval = 5  # 점유율 간격
            self.outbreak_cycle = 60
            self.use_unexpected = 1
            # 이외의 설정값 등 리셋
        elif op == chr(0x0D):
            self.ot.win_reboot()
        elif op == chr(0x0E):
            index = int(ord(msg[44]))
            # 차로 지정
            if index == 1:
                data = msg[45:]
                data_1 = int(ord(data[0]))
                data_2 = int(ord(data[1]))
                if data_1 != 0:  # 1byte
                    for i in range(0, 8):
                        if (data_1 >> i) & 0x01 == 0x01:
                            self.lane_num = (8-i)
                else:  # 2 byte
                    for i in range(0, 8):
                        if (data_2 >> i) & 0x01 == 0x01:
                            self.lane_num = (8 - i) + 8

            # 수집 주기
            elif index == 3:
                data = int(ord(msg[45]))
                self.collect_cycle = data
            # 차량 속도 구분
            elif index == 5:
                data = msg[45:]
                print(len(data))
                for i in range(len(data)):
                    self.category_num[i] = int(ord(data[i]))
            # 누적 교통량
            elif index == 7:
                data = int(ord(msg[45]))
                self.use_ntraffic = data
            # 속도 데이터 (카테고리)
            elif index == 9:
                data = int(ord(msg[45]))
                self.use_category_speed = data
            # 최대검지거리, 노드 간격, 점유율 간격
            elif index == 11:
                data = msg[45:]
                max_distance_f = int(ord(data[0])) * 256
                max_distance_b = int(ord(data[1]))
                self.max_distance = max_distance_f + max_distance_b
                self.node_interval = int(ord(data[2]))
                self.share_interval = int(ord(data[3]))
            # index 13
            elif index == 13:
                data = int(ord(msg[45]))
                self.outbreak_cycle = data
            # 돌발 사용 여부
            elif index == 19:
                data = int(ord(msg[45]))
                self.use_unexpected = data
        elif op == chr(0x18):
            data = msg[44:]
            day_list = list()
            for i in data:
                temp = hex(ord(i))
                day_list.append(temp[2:])
            try:
                self.ot.win_set_time(day_list)
                return [True]
            except Exception as e:
                return [False, chr(0x18), chr(0x01)]

        share_data = [self.max_distance >> 8, self.max_distance & 0xFF, self.node_interval, self.share_interval]
        parameter_list = [self.lane_num, self.collect_cycle, self.category_num, self.use_ntraffic, self.use_category_speed, share_data, self.outbreak_cycle, self.use_unexpected]
        self.db.set_paramete_data(parameter_list=parameter_list, host=self.db_ip, port=int(self.db_port), user=self.db_id, password=self.db_pw, db=self.db_name)
        self.status.get_data(lane=self.lane_num, max_distance=self.max_distance, node_interval=self.node_interval)

    # region ui update
    def update_server_icon(self, b):
        if b:
            self.ui.server_status_icon.setPixmap(self.status_connect)
        else:
            self.ui.server_status_icon.setPixmap(self.status_disconnect)

    def update_client_icon(self, b):
        if b:
            self.ui.client_status_icon.setPixmap(self.status_connect)
        else:
            self.ui.client_status_icon.setPixmap(self.status_disconnect)

    def update_Statusbar_text(self, msg):
        self.ui.status_bar.setText(msg)

    def update_RX_Log(self, OPCODE, list):
        log_list = []
        MAX_ROWS = 20  # 표출할 최대 행 개수

        date_s = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # 새로운 행을 추가하기 전에 현재 행의 개수 확인
        numRows = self.ui.rx_table.rowCount()

        # Add text to the row
        self.ui.rx_table.insertRow(numRows)
        self.ui.rx_table.setItem(numRows, 0, QTableWidgetItem(date_s))
        self.ui.rx_table.setItem(numRows, 1, QTableWidgetItem("0x{:02X}".format(ord(OPCODE))))

        # 표출할 최대 행 개수보다 현재 행 개수가 크다면 가장 위의 행을 제거
        if numRows >= MAX_ROWS:
            self.ui.rx_table.removeRow(0)
            numRows -= 1

        # list에 추가
        log_list.append(date_s)
        log_list.append("0x{:02X}".format(ord(OPCODE)))
        log_list.append("RX")

        # list[0] { 0 : None, 1 : ACK, 2 : NACK}
        if list[0] == 1:
            self.ui.rx_table.setItem(numRows, 2, QTableWidgetItem('ACK'))
            log_list.append('ACK')
        elif list[0] == 2:
            self.ui.rx_table.setItem(numRows, 2, QTableWidgetItem('NACK'))
            log_list.append('NACK')
            if list[1] == chr(0x01):
                self.ui.rx_table.setItem(numRows, 3, QTableWidgetItem('System Error'))
                log_list.append('System Error')
            elif list[1] == chr(0x02):
                self.ui.rx_table.setItem(numRows, 3, QTableWidgetItem('Data Length Error'))
                log_list.append('Data Length Error')
            elif list[1] == chr(0x03):
                self.ui.rx_table.setItem(numRows, 3, QTableWidgetItem('CSN Error'))
                log_list.append('CSN Error')
            elif list[1] == chr(0x04):
                self.ui.rx_table.setItem(numRows, 3, QTableWidgetItem('OP Code Error'))
                log_list.append('OP Code Error')
            elif list[1] == chr(0x05):
                self.ui.rx_table.setItem(numRows, 3, QTableWidgetItem('Out of Index Error'))
                log_list.append('Out of Index Error')
            elif list[1] == chr(0x06):
                self.ui.rx_table.setItem(numRows, 3, QTableWidgetItem('Not Ready Error'))
                log_list.append('Not Ready Error')
            elif list[1] == chr(0xFF):
                self.ui.rx_table.setItem(numRows, 3, QTableWidgetItem('Error'))
                log_list.append('Error')
            else:
                self.ui.rx_table.setItem(numRows, 3, QTableWidgetItem('Reserved'))
                log_list.append('Reserved')

        if self.m_log_save:
            print(log_list)
            self.log.log_save(log_list)
            self.ui.log_status_bar.setText(self.log.log_path())
            self.db.save_Log_data(msg_list=log_list, host=self.db_ip, port=int(self.db_port), user=self.db_id,
                                  password=self.db_pw, db=self.db_name)
        self.ui.rx_table.scrollToBottom()

    def update_TX_Log(self, OPCODE, list):
        log_list = []
        MAX_ROWS = 20  # 표출할 최대 행 개수

        date_s = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

        # 새로운 행을 추가하기 전에 현재 행의 개수 확인
        numRows = self.ui.tx_table.rowCount()

        self.ui.tx_table.insertRow(numRows)
        # Add text to the row
        self.ui.tx_table.setItem(numRows, 0, QTableWidgetItem(date_s))
        self.ui.tx_table.setItem(numRows, 1, QTableWidgetItem("0x{:02X}".format(ord(OPCODE))))

        # 표출할 최대 행 개수보다 현재 행 개수가 크다면 가장 위의 행을 제거
        if numRows >= MAX_ROWS:
            self.ui.tx_table.removeRow(0)
            numRows -= 1

        log_list.append(date_s)
        log_list.append("0x{:02X}".format(ord(OPCODE)))
        log_list.append("TX")

        # list[0] { 0 : None, 1 : ACK, 2 : NACK}
        if list[0] == 1:
            self.ui.tx_table.setItem(numRows, 2, QTableWidgetItem('ACK'))
            log_list.append('ACK')
        elif list[0] == 2:
            self.ui.tx_table.setItem(numRows, 2, QTableWidgetItem('NACK'))
            log_list.append('NACK')
            if list[1] == chr(0x01):
                self.ui.tx_table.setItem(numRows, 3, QTableWidgetItem('System Error'))
                log_list.append('System Error')
            elif list[1] == chr(0x02):
                self.ui.tx_table.setItem(numRows, 3, QTableWidgetItem('Data Length Error'))
                log_list.append('Data Length Error')
            elif list[1] == chr(0x03):
                self.ui.tx_table.setItem(numRows, 3, QTableWidgetItem('CSN Error'))
                log_list.append('CSN Error')
            elif list[1] == chr(0x04):
                self.ui.tx_table.setItem(numRows, 3, QTableWidgetItem('OP Code Error'))
                log_list.append('OP Code Error')
            elif list[1] == chr(0x05):
                self.ui.tx_table.setItem(numRows, 3, QTableWidgetItem('Out of Index Error'))
                log_list.append('Out of Index Error')
            elif list[1] == chr(0x06):
                self.ui.tx_table.setItem(numRows, 3, QTableWidgetItem('Not Ready Error'))
                log_list.append('Not Ready Error')
            elif list[1] == chr(0xFF):
                self.ui.tx_table.setItem(numRows, 3, QTableWidgetItem('Error'))
                log_list.append('Error')
            else:
                self.ui.tx_table.setItem(numRows, 3, QTableWidgetItem('Reserved'))
                log_list.append('Reserved')

        if self.m_log_save:
            self.log.log_save(log_list)
            self.db.save_Log_data(msg_list=log_list, host=self.db_ip, port=int(self.db_port), user=self.db_id,
                                  password=self.db_pw, db=self.db_name)
        self.ui.tx_table.scrollToBottom()

    # endregion
