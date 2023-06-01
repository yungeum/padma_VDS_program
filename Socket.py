
import socket
import select
import queue
from time import localtime

from other import Other_function

import random
import cv2
import numpy as np
import base64

class Socket_function:
    def __init__(self):
        super().__init__()

        self.server_socket = None
        self.client_socket_list = list()
        self.client_socket = None

        self.ip = None
        self.port = None

        self.ot = Other_function()

    def socket_server_open(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        # self.server_socket.listen(5)

    def client_accept(self):
        c_s, addr = self.server_socket.accept()
        self.client_socket_list.append(c_s)
        if len(self.client_socket_list) > 2:
            # self.client_socket_close()
            self.client_socket_list[0].close()
            self.client_socket_list.pop(0)
        self.client_socket = self.client_socket_list[-1]
        # print("list==", self.client_socket_list)
        return self.client_socket

    def client_socket_close(self):
        # self.client_socket.shutdown(socket.SHUT_RDWR)
        # self.client_socket.close()
        # self.client_socket.detach()
        self.client_socket = None

    def socket_connect(self, ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))

    def socket_send_msg(self, send_msg):
        self.client_socket.send(send_msg.encode('utf-16'))
        print("TX OPCode: ", "0x{:02X}".format(ord(send_msg[43])))
        print("TX_msg: [", ", ".join(str(ord(data)) for data in send_msg[44:]), "]")
        # print("TX_msg: [", send_msg, "]")
        # print("TX: [", send_msg.encode('utf-16'), "]")
        # recv
        # recv_msg = self.client_socket.recv(1024)
        # d_recv_msg = recv_msg.decode()
        # print("recv: " + recv_msg.decode())
        # for i in range(len(recv_msg)):
        #     print("msg[i]: ", recv_msg[i])
        #
        # for i in range(len(recv_msg)):
        #     print("de_msg[i]: ", recv_msg[i])

    def socket_read(self):
        msg = ''
        try:
            msg = self.client_socket.recv(1024)
            # print(self.client_socket)
        except Exception as e:
            # self.client_socket = None
            print("err socket_read : ", e)

        return msg

    # region msg response
    def send_FF_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number):
        point = chr(0x2D)
        opcode = chr(0xFF)
        ack = chr(0x06)
        length = self.ot.length_calc(2 + len(ack))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack
        self.socket_send_msg(send_msg)

    def send_FE_msg(self, sender_ip, destination_ip, controller_kind, controller_number):
        point = chr(0x2D)
        opcode = chr(0xFE)
        length = self.ot.length_calc(1)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_04_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, frame, lane, traffic_data):
        point = chr(0x2D)
        opcode = chr(0x04)
        ack = chr(0x06)
        frame_num = frame
        lane_num = chr(lane)

        # traffic data => [[차량수, 속도, 점유율, 상/하행],[차량수, 속도, 점유율, 상/하행]]
        # print(traffic_data)
        lane_data = ''
        for i in traffic_data:
            # 차량수 + 속도 + 점유율 + 상/하행
            lane_data = lane_data + chr(i[0]) + chr(i[1]) + chr(i[2]) + chr(i[3])

        data = frame_num + lane_num + lane_data
        length = self.ot.length_calc(2 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack + data
        self.socket_send_msg(send_msg)

    def send_05_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, speed_data):
        point = chr(0x2D)
        opcode = chr(0x05)
        ack = chr(0x06)
        lane = len(speed_data)

        data = chr(lane)
        # print(speed_data)
        for temp in speed_data:
            for i in range(len(temp)):
                data = data + chr(temp[i] >> 8) + chr(temp[i] & 0xFF)

        length = self.ot.length_calc(2 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack + data
        self.socket_send_msg(send_msg)

    def send_07_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, ntraffic_data):
        point = chr(0x2D)
        opcode = chr(0x07)
        ack = chr(0x06)

        # ntraffinc_data = [ 1차선 교통량, 2차선 교통량 ]
        data = ''
        for count in ntraffic_data:
            num_high = int(count) >> 8
            num_low = int(count) & 0xFF
            data = data + chr(num_high) + chr(num_low)

        length = self.ot.length_calc(2 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack + data
        self.socket_send_msg(send_msg)

    def send_0C_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number):
        point = chr(0x2D)
        opcode = chr(0x0C)
        data = chr(0x06) # ack
        length = self.ot.length_calc(1 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + data
        self.socket_send_msg(send_msg)

    def send_0D_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number):
        point = chr(0x2D)
        opcode = chr(0x0D)
        data = chr(0x06) # ack
        length = self.ot.length_calc(1 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + data
        self.socket_send_msg(send_msg)

    def send_0E_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number):
        point = chr(0x2D)
        opcode = chr(0x0E)
        data = chr(0x06) # ack
        length = self.ot.length_calc(1 + len(data))
        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + data
        self.socket_send_msg(send_msg)

    def send_0F_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, index, lane_num, collect_cycle, category_num, acc_speed, calc_speed, max_distance, node_interval, share_interval, outbreak_cycle, use_unexpected):
        point = chr(0x2D)
        opcode = chr(0x0F)
        ack = chr(0x06)

        data = ''
        if index == 1:
            # 차로 계산 (1 << 차로-1)
            byte_1 = chr(1 << (lane_num - 1))
            byte_2 = chr(0)
            data = byte_1 + byte_2
        elif index == 3:
            # 수집주기 기본 30, 변경값 60
            byte_1 = chr(collect_cycle)
            data = byte_1
        elif index == 5:
            # 차량 속도 category 단위 기본 10
            byte_1 = chr(category_num[0])
            byte_2 = chr(category_num[1])
            byte_3 = chr(category_num[2])
            byte_4 = chr(category_num[3])
            byte_5 = chr(category_num[4])
            byte_6 = chr(category_num[5])
            byte_7 = chr(category_num[6])
            byte_8 = chr(category_num[7])
            byte_9 = chr(category_num[8])
            byte_10 = chr(category_num[9])
            byte_11 = chr(category_num[10])
            byte_12 = chr(category_num[11])
            data = byte_1 + byte_2 + byte_3 + byte_4 + byte_5 + byte_5 + byte_6 + \
                   byte_7 + byte_8 + byte_9 + byte_10 + byte_11 + byte_12
        elif index == 7:
            data = chr(index)
            # 속도별 누적치 계산 기본 1(사용)
            byte_1 = chr(acc_speed)
            data = data + byte_1
        elif index == 9:
            data = chr(index)
            # 속도 계산 가능 여부 기본 1(사용)
            byte_1 = chr(calc_speed)
            data = data + byte_1
        elif index == 11:
            data = chr(index)
            byte_1 = chr(max_distance >> 8)
            byte_2 = chr(max_distance & 0XFF)
            byte_3 = chr(node_interval)
            byte_4 = chr(share_interval)
            data = data + byte_1 + byte_2 + byte_3 + byte_4
        elif index == 13:
            data = chr(index)
            byte_1 = chr(outbreak_cycle)
            data = data + byte_1
        elif index == 19:
            data = chr(index)
            # 돌발 사용 여부 기본 0(사용안함)
            byte_1 = chr(use_unexpected)
            data = data + byte_1

        length = self.ot.length_calc(2 + len(data))
        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack + data
        self.socket_send_msg(send_msg)

    def send_11_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, connect_time, request_time):
        point = chr(0x2D)
        opcode = chr(0x11)
        ack = chr(0x06)
        if connect_time != None and request_time != None:
            time_cha = int(request_time - connect_time)
            time_1 = time_cha & 0xFF
            time_2 = (time_cha >> 8) & 0xFF
            time_3 = (time_cha >> 16) & 0xFF
            time_4 = (time_cha >> 24) & 0xFF
            data = chr(time_3) + chr(time_3) + chr(time_2) + chr(time_1)
            length = self.ot.length_calc(2 + len(data))

            send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack + data
            self.socket_send_msg(send_msg)
        else:
            print("Please connect 0xFF")


    def send_13_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, msg):
        point = chr(0x2D)
        opcode = chr(0x13)
        ack = chr(0x06)
        data = msg[44:]
        length = self.ot.length_calc(2 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack +data
        self.socket_send_msg(send_msg)

    def send_15_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, version_list):
        if version_list == '':
            print("version_list is None")
        else:
            point = chr(0x2D)
            opcode = chr(0x15)
            ack = chr(0x06)
            version = version_list[0][1] << 4
            release = version_list[0][2] & 0x0F
            version_num = chr(version) + chr(release)
            make_year = chr(version_list[0][3])
            make_month = chr(version_list[0][4])
            make_day = chr(version_list[0][5])
            data = version_num + make_year + make_month + make_day
            length = self.ot.length_calc(2 + len(data))

            send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack + data
            self.socket_send_msg(send_msg)

    # 개별 차량 데이터 응답
    def send_16_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, frame, individual_traffic_data):
        point = chr(0x2D)
        opcode = chr(0x16)
        ack = chr(0x06)
        car_count = chr(len(individual_traffic_data) >> 8) + chr(len(individual_traffic_data) & 0xFF)
        data = frame + car_count
        for i in individual_traffic_data:
            data = data + chr(int(i[0])) + chr(int(i[1])) + chr(int(i[2])) + chr(int(i[3])) + chr(int(i[4]))

        length = self.ot.length_calc(2 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack + data
        self.socket_send_msg(send_msg)

    # 정지 영상 응답
    def send_17_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, img):
        sender_ip += chr(0x2D)
        destination_ip += chr(0x2D)
        controller = controller_kind + controller_number
        opcode = chr(0x17)
        ack = chr(0x06)

        # encode image
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        _, imgencode = cv2.imencode('.jpg', img, encode_param)
        data = np.array(imgencode)
        byteData = base64.b64encode(data)
        stringData = ''
        for i in byteData:
            stringData += chr(i)

        img_length = self.ot.length_calc(len(stringData))
        total_length = self.ot.length_calc(6 + len(stringData))

        print('[total length] : ', len(stringData))

        send_msg = sender_ip + destination_ip + controller + total_length + opcode + ack + img_length + stringData

        self.socket_send_msg(send_msg)



    # RTC 변경 응답
    def send_18_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number):
        point = chr(0x2D)
        opcode = chr(0x18)
        data = chr(0x06)  # ack
        length = self.ot.length_calc(1 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + data
        self.socket_send_msg(send_msg)

    # 돌발 상황 정보
    def send_19_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, outbreak, location):
        point = chr(0x2D)
        opcode = chr(0x19)
        breaktime = chr(len(outbreak))
        stringdata = ''
        for data in outbreak:
            dt = data[0]
            daytime = chr(int(dt.strftime("%Y")[:2])) + chr(int(dt.strftime("%y"))) + chr(int(dt.strftime("%m"))) + chr(int(dt.strftime("%d"))) + chr(int(dt.strftime("%H"))) + chr(int(dt.strftime("%M"))) + chr(int(dt.strftime("%S")))
            temp1 = data[2] & 0xFF
            temp2 = (data[2] >> 8) & 0xFF
            outbreak_class = chr(temp2) + chr(temp1)
            # 감지ID + 차로정보 + 돌발종류 +
            stringdata = stringdata + daytime + chr(data[1]) + outbreak_class + chr(round(data[3])) + chr(data[4])
            #################################
        datafield = breaktime + location[0] + location[1] + stringdata
        length = self.ot.length_calc(1 + len(datafield))
        print("total_length: ", len(datafield))
        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + datafield
        # print(send_msg)
        self.socket_send_msg(send_msg)

    def send_1E_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, controllerBox_state_list):
        point = chr(0x2D)
        opcode = chr(0x1E)
        ack = chr(0x06)
        data = ''
        for i in controllerBox_state_list:
            data += chr(i)
        length = self.ot.length_calc(2 + len(data))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + ack + data
        # print(send_msg)
        # for i in send_msg:
        #     print(ord(i))
        self.socket_send_msg(send_msg)

    def send_nack_res_msg(self, sender_ip, destination_ip, controller_kind, controller_number, list):
        point = chr(0x2D)
        nack = chr(0x15)
        opcode = list[1]
        data = list[2]
        length = self.ot.length_calc(len(opcode) + len(data) + 1)
        print("###NACK: ", list)
        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + nack + data
        self.socket_send_msg(send_msg)
    # endregion

    def send_FF_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)
        point = chr(0x2D)
        opcode = chr(0xFF)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_01_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        point = chr(0x2D)
        opcode = chr(0x01)
        data_frame = chr(120)
        length = self.ot.length_calc(2)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + data_frame
        self.socket_send_msg(send_msg)

    def send_04_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)
        point = chr(0x2D)
        opcode = chr(0x04)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        #send_msg ='123.456.789.123-127.000.000.001-VD123450001chr(0x04)'
        self.socket_send_msg(send_msg)

    def send_05_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)
        point = chr(0x2D)
        opcode = chr(0x05)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_07_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)
        point = chr(0x2D)
        opcode = chr(0x07)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_0C_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)
        point = chr(0x2D)
        opcode = chr(0x0C)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_0D_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        point = chr(0x2D)
        opcode = chr(0x0D)
        length = self.ot.length_calc(1)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_0E_msg(self):
        point = chr(0x2D)
        opcode = chr(0x0E)
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        # length = '0001'
        # index = 1 -> 차로지정
        # index = 3 -> 수집주기
        # index = 5 -> 차량 속도 구분
        # index = 7 -> 속도별 누적치 계산
        index_list = [1, 3, 5, 7, 9, 21]
        index = random.choice(index_list)

        data = ''
        if index == 1:
            data = chr(index)
            # 차로 계산 (1 << 차로-1)
            byte_1 = chr(1 << (2-1))
            byte_2 = chr(0)
            data = data + byte_1 + byte_2
        elif index == 3:
            data = chr(index)
            # 수집주기 기본 30, 변경값 60
            byte_1 = chr(60)
            data = data + byte_1
        elif index == 5:
            data = chr(index)
            # 차량 속도 category 단위 기본 10
            byte_1 = chr(10)
            byte_2 = chr(10)
            byte_3 = chr(10)
            byte_4 = chr(10)
            byte_5 = chr(10)
            byte_6 = chr(10)
            byte_7 = chr(10)
            byte_8 = chr(10)
            byte_9 = chr(10)
            byte_10 = chr(10)
            byte_11 = chr(10)
            byte_12 = chr(10)
            data = data + byte_1 + byte_2 + byte_3 + byte_4 + byte_5 + byte_5 + byte_6 + \
                   byte_7 + byte_8 + byte_9 + byte_10 + byte_11 + byte_12
        elif index == 7:
            data = chr(index)
            # 속도별 누적치 계산 기본 1(사용)
            byte_1 = chr(0)
            data = data + byte_1
        elif index == 9:
            data = chr(index)
            # 속도 계산 가능 여부 기본 1(사용)
            byte_1 = chr(0)
            data = data + byte_1
        elif index == 21:
            data = chr(index)
            # 속도 계산 가능 여부 기본 0(사용안함)
            byte_1 = chr(1)
            data = data + byte_1

        length = self.ot.length_calc(1 + data)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + data
        self.socket_send_msg(send_msg)

    def send_0F_msg(self):
        point = chr(0x2D)
        opcode = chr(0x0F)
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        index_list = [1, 3, 5, 7, 9, 21]
        index = chr(random.choice(index_list))
        length = self.ot.length_calc(1 + len(index))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + index
        self.socket_send_msg(send_msg)

    def send_11_msg(self):
        point = chr(0x2D)
        opcode = chr(0x11)
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_13_msg(self):
        point = chr(0x2D)
        opcode = chr(0x13)
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        echo_msg = 'qwelkjdasoiweoi2390weiodskl'
        length = self.ot.length_calc(1 + len(echo_msg))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + echo_msg
        self.socket_send_msg(send_msg)

    def send_15_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)
        point = chr(0x2D)
        opcode = chr(0x15)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_16_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)
        point = chr(0x2D)
        opcode = chr(0x16)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_17_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        point = chr(0x2D)
        opcode = chr(0x17)
        cam = chr(random.randrange(0, 3))
        length = self.ot.length_calc(1 + len(cam))

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode + cam
        self.socket_send_msg(send_msg)

    def send_18_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = '0008'
        point = chr(0x2D)
        opcode = chr(0x18)
        # change_rtc_tune =

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)

    def send_1E_msg(self):
        sender_ip = '123.456.789.123'
        destination_ip = '127.000.000.001'
        controller_kind = 'VD'
        controller_number = '12345'
        length = self.ot.length_calc(1)
        point = chr(0x2D)
        opcode = chr(0x1E)

        send_msg = sender_ip + point + destination_ip + point + controller_kind + controller_number + length + opcode
        self.socket_send_msg(send_msg)


