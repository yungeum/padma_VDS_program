import pymysql
# import pymssql
from datetime import datetime, timedelta
import time
import math

from calc import CALC_function


class DB_function:
    def __init__(self):
        super().__init__()
        self.calc = CALC_function()

        self.distlong_diff = 30
        self.log_count = 0

        self.last_congestion_list = []
        self.last_outbreak_list = []
        self.current_congestion = None
        self.current_stop = None
        self.current_reverse = None

        self.last_congestion = None
        self.now_congestion = 0

        # ptz_info = self.get_ptz_info(host='127.0.0.1', port=3315, user='root', password='hbrain0372!', db='hbrain_vds', charset='utf8')
        # print(self.get_occupancy_interval_data(lane=6, host='127.0.0.1', port=1433, user='sa', password='hbrain0372!', db='hbrain_vds', charset='utf8'))
        # print(self.get_congestion_data(congestion=43, cycle=30, zone=60, sync_time=time.time(), host='127.0.0.1', port=1433, user='sa', password='hbrain0372!', db='hbrain_vds', charset='utf8'))
        # print(self.get_location_data(host='127.0.0.1', port=1433, user='sa', password='hbrain0372!', db='hbrain_vds', charset='utf8'))
        # print(self.get_controller_station_number_data(host='127.0.0.1', port=1433, user='sa', password='hbrain0372!', db='hbrain_vds', charset='utf8'))

    # DB 초기 데이터베이스 및 테이블 존재 여부 및 생성
    def create_init_DB(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, charset=charset, autocommit=True)
        db_connect = pymysql.connect(host=host, port=port, user=user, password=password, charset=charset, autocommit=True)
        cur = db_connect.cursor()
        use_db = False
        while not use_db:
            try:
                sql = 'CREATE DATABASE IF NOT EXISTS ' + db
                cur.execute(sql)
                use_db = True
            except Exception as e:
                usb_db = False

        time.sleep(1)
        db_connect.close()

        # region sql 구문
        create_obj_info = "CREATE TABLE IF NOT EXISTS obj_info(time datetime(3) NOT NULL, id TINYINT NOT NULL, distlat FLOAT default NULL, distlong FLOAT default NULL, vrellat FLOAT default NULL, vrellong FLOAT default NULL, velocity FLOAT default NULL, rcs FLOAT default NULL, probofexist TINYINT default NULL, arellat FLOAT default NULL, arellong FLOAT default NULL, class TINYINT default NULL, length FLOAT default NULL, width FLOAT default NULL, zone TINYINT default NULL, lane TINYINT default NULL, PRIMARY KEY(time, id));"
        create_traffic_detail = "CREATE TABLE IF NOT EXISTS traffic_detail(time datetime(3) NOT NULL, id TINYINT NOT NULL, distlong FLOAT default NULL, velocity FLOAT default NULL, zone TINYINT default NULL, class TINYINT default NULL, category TINYINT NOT NULL, PRIMARY KEY(time, id, category));"
        create_traffic_info = "CREATE TABLE IF NOT EXISTS traffic_info(lane TINYINT NOT NULL, ntraffic INT default NULL, totalvelocity FLOAT default NULL, PRIMARY KEY(lane));"
        create_outbreak = "CREATE TABLE IF NOT EXISTS outbreak(time datetime(3) NOT NULL, idx TINYINT NOT NULL, class TINYINT NOT NULL, zone TINYINT default NULL, distlat FLOAT default NULL, distlong FLOAT default NULL, distance FLOAT default NULL, PRIMARY KEY(time, idx, class));"
        create_parameter = "CREATE TABLE IF NOT EXISTS parameter(param TINYINT NOT NULL, nbyte TINYINT NOT NULL, data SMALLINT default NULL, PRIMARY KEY (param, nbyte));"
        create_vds_version = "CREATE TABLE IF NOT EXISTS vds_version(time DATE default NULL, version_no TINYINT NOT NULL, release_no TINYINT NOT NULL, year TINYINT default NULL, month TINYINT default NULL, day TINYINT default NULL, PRIMARY KEY (version_no, release_no));"
        create_sw_parameter = "CREATE TABLE IF NOT EXISTS sw_parameter(param CHAR(64) NOT NULL, value CHAR(32) default NULL, PRIMARY KEY(param));"
        create_controlbox_status = "CREATE TABLE IF NOT EXISTS controlbox_status(param CHAR(64) NOT NULL, data INT default NULL, PRIMARY KEY (param));"
        create_vds_log = "CREATE TABLE IF NOT EXISTS vds_log(idx INT NOT NULL, time datetime(3) NOT NULL, opcode CHAR(4) default NULL, packet CHAR(4) default NULL, acknack CHAR(4) default NULL, reason CHAR(32) default NULL, PRIMARY KEY(idx, time));"
        create_outbreak_status = "CREATE TABLE IF NOT EXISTS outbreak_status(zone TINYINT default NULL, type TINYINT default NULL, status TINYINT default NULL);"


        insert_traffic_info = "INSERT INTO traffic_info VALUES(1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 0, 0), (6, 0, 0);"
        insert_parameter = "INSERT INTO parameter VALUES(1, 0, 4), (1, 1, 0), (3, 0, 30), (5, 0, 0), (5, 1, 11), (5, 2, 21), (5, 3, 31), (5, 4, 41), (5, 5, 51), (5, 6, 61), (5, 7, 71), (5, 8, 81), (5, 9, 91), (5, 10, 101), (5, 11, 111), (7, 0, 1), (9, 0, 1), (11, 0, 0), (11, 1, 200), (11, 2, 25), (11, 3, 5), (13, 0, 60), (19, 0, 1);"
        insert_vds_version = "INSERT INTO vds_version VALUES('2022-07-25', 1, 1, 22, 7, 25), ('2022-08-02', 1, 2, 22, 8, 2);"
        insert_sw_parameter_1 = "INSERT INTO sw_parameter VALUES" \
                                "('1_occupancy_min', '45'), ('1_occupancy_max', '70')," \
                                "('2_occupancy_min', '45'), ('2_occupancy_max', '75')," \
                                "('3_occupancy_min', '45'), ('3_occupancy_max', '80')," \
                                "('4_occupancy_min', '35'), ('4_occupancy_max', '75')," \
                                "('5_occupancy_min', '35'), ('5_occupancy_max', '80')," \
                                "('6_occupancy_min', '35'), ('6_occupancy_max', '85');"
        insert_sw_parameter_2 = "INSERT INTO sw_parameter VALUES('1_traffic', '60'), ('2_traffic', '55');"
        insert_sw_parameter_3 = "INSERT INTO sw_parameter VALUES" \
                                "('1_lanePoint', '3.3'), " \
                                "('2_lanePoint', '3.3'), " \
                                "('3_lanePoint', '3.3'), " \
                                "('4_lanePoint', '3.3'), " \
                                "('5_lanePoint', '3.3'), " \
                                "('6_lanePoint', '3.3');"
        insert_sw_parameter_4 = "INSERT INTO sw_parameter VALUES" \
                                "('1_laneShift', '0'), " \
                                "('2_laneShift', '0'), " \
                                "('3_laneShift', '0'), " \
                                "('4_laneShift', '0'), " \
                                "('5_laneShift', '0'), " \
                                "('6_laneShift', '0'), " \
                                "('7_laneShift', '0'), " \
                                "('8_laneShift', '0'), " \
                                "('9_laneShift', '0');"
        insert_sw_parameter_5 = "INSERT INTO sw_parameter VALUES('radarAngle', '0');"
        insert_sw_parameter_6 = "INSERT INTO sw_parameter VALUES('radarShift', '0.0');"
        insert_sw_parameter_7 = "INSERT INTO sw_parameter VALUES('last_time_Cspeed', NULL);"
        insert_sw_parameter_8 = "INSERT INTO sw_parameter VALUES('RADAR_ID', '0');"
        insert_sw_parameter_9 = "INSERT INTO sw_parameter VALUES('doKalman', '1'),('doInterpolation', '1'),('doTracking', '1');"
        insert_sw_parameter_10 = "INSERT INTO sw_parameter VALUES('PTZ_IP', '192.168.0.64'),('PTZ_PORT', '8000'),('PTZ_ID', 'admin'),('PTZ_PW', 'hbrain0372!');"
        insert_sw_parameter_11 = "INSERT INTO sw_parameter VALUES('DB_IP', '127.0.0.1'),('DB_PORT', '0372'),('DB_ID', 'root'),('DB_PW', 'hbrain0372!'),('DB_DB', '" + db + "');"
        insert_sw_parameter_12 = "INSERT INTO sw_parameter VALUES('SOCKET_IP', NULL),('SOCKET_PORT', '30100');"
        insert_sw_parameter_13 = "INSERT INTO sw_parameter VALUES('congestion_criterion', '50'),('congestion_cycle', '30');"
        insert_sw_parameter_14 = "INSERT INTO sw_parameter VALUES('Controller_station_number', NULL);"
        insert_sw_parameter_15 = "INSERT INTO sw_parameter VALUES('latitude', '023.461247'),('longitude', '090.262759');"

        insert_controlbox_status_1 = "INSERT INTO controlbox_status VALUES('Long_Power_Fail', 0),('Short_Power_Fail', 0),('Default Parameter', 1);"
        insert_controlbox_status_2 = "INSERT INTO controlbox_status VALUES('Front_Door_Status', 0),('Back_Door_Status', 0),('Fan_Status', 0),('Heater_Stauts', 0),('Image_Status', 0),('Reset_Status', 0);"
        insert_controlbox_status_3 = "INSERT INTO controlbox_status VALUES('Temperature', 24),('Input_Voltage', 220),('Output_Voltage', 12);"
        time_temp = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        insert_program_start = "INSERT INTO vds_log VALUES(0, '" + time_temp + "',  NULL, NULL, NULL, 'START VDS_COM PROGRAM');"

        # endregion

        if use_db:
            # db_conn = pymssql.connect(server=host, port=port, user=user, password=password, charset=charset, autocommit=True)
            db_conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
            cur_conn = db_conn.cursor()
            try:
                cur_conn.execute(create_obj_info)
            except Exception as e:
                print("err create_obj_info: ", e)

            try:
                cur_conn.execute(create_traffic_detail)
            except Exception as e:
                print("err create_traffic_detail: ", e)

            try:
                cur_conn.execute(create_traffic_info)
            except Exception as e:
                print("err create_traffic_info: ", e)

            try:
                cur_conn.execute(create_outbreak)
            except Exception as e:
                print("err create_outbreak: ", e)

            try:
                cur_conn.execute(create_parameter)
            except Exception as e:
                print("err create_parameter: ", e)

            try:
                cur_conn.execute(create_vds_version)
            except Exception as e:
                print("err create_vds_version: ", e)

            try:
                cur_conn.execute(create_sw_parameter)
            except Exception as e:
                print("err create_sw_parameter: ", e)

            try:
                cur_conn.execute(create_controlbox_status)
            except Exception as e:
                print("err create_controlbox_status: ", e)

            try:
                cur_conn.execute(create_vds_log)
            except Exception as e:
                print("err create_vds_log: ", e)

            try:
                cur_conn.execute(create_outbreak_status)
            except Exception as e:
                print("err create_outbreak_status: ", e)

            try:
                cur_conn.execute(insert_traffic_info)
            except Exception as e:
                print("err insert_traffic_info: ", e)

            try:
                cur_conn.execute(insert_parameter)
            except Exception as e:
                print("err insert_parameter: ", e)

            try:
                cur_conn.execute(insert_vds_version)
            except Exception as e:
                print("err insert_vds_version: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_1)
            except Exception as e:
                print("err insert_sw_parameter_1: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_2)
            except Exception as e:
                print("err insert_sw_parameter_2: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_3)
            except Exception as e:
                print("err insert_sw_parameter_3: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_4)
            except Exception as e:
                print("err insert_sw_parameter_4: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_5)
            except Exception as e:
                print("err insert_sw_parameter_5: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_6)
            except Exception as e:
                print("err insert_sw_parameter_6: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_7)
            except Exception as e:
                print("err insert_sw_parameter_7: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_8)
            except Exception as e:
                print("err insert_sw_parameter_8: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_9)
            except Exception as e:
                print("err insert_sw_parameter_9: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_10)
            except Exception as e:
                print("err insert_sw_parameter_10: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_11)
            except Exception as e:
                print("err insert_sw_parameter_11: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_12)
            except Exception as e:
                print("err insert_sw_parameter_12: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_13)
            except Exception as e:
                print("err insert_sw_parameter_13: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_14)
            except Exception as e:
                print("err insert_sw_parameter_14: ", e)

            try:
                cur_conn.execute(insert_sw_parameter_15)
            except Exception as e:
                print("err insert_sw_parameter_15: ", e)

            try:
                cur_conn.execute(insert_controlbox_status_1)
            except Exception as e:
                print("err insert_controlbox_status_1: ", e)

            try:
                cur_conn.execute(insert_controlbox_status_2)
            except Exception as e:
                print("err insert_controlbox_status_2: ", e)

            try:
                cur_conn.execute(insert_controlbox_status_3)
            except Exception as e:
                print("err insert_controlbox_status_3: ", e)

            try:
                cur_conn.execute(insert_program_start)
            except Exception as e:
                print("err insert_program_start: ", e)
            db_conn.close()

    # DB 연결 체크 함수
    def db_connection_check(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
            cur = db_connect.cursor()
            sql = 'use ' + db
            cur.execute(sql)

            db_connect.close()
            return True
        except Exception as e:
            print("err db_connection_check : ", e)
            return False

    # region get data
    # socket ip & port
    def get_socket_info(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        socket_info = []
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
            cur = db_connect.cursor()

            sql = "select value from sw_parameter where param='SOCKET_IP'"
            cur.execute(sql)
            result = cur.fetchone()
            if result[0] is None:
                socket_info.append(None)
            else:
                socket_info.append(result[0].replace(" ", ""))

            sql = "select value from sw_parameter where param='SOCKET_PORT'"
            cur.execute(sql)
            result = cur.fetchone()
            socket_info.append(int(result[0]))

            db_connect.close()
        except Exception as e:
            print("err get_socket_info : ", e)

        return socket_info

    # Controller station number 값
    def get_controller_station_number_data(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        cont_number = None
        cont_result = ''
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
            cur = db_connect.cursor()

            sql = "select value from sw_parameter where param='Controller_station_number'"
            cur.execute(sql)
            result = cur.fetchone()
            if result[0] is None:
                cont_number = None
            else:
                cont_number = result[0].replace(" ", "")

            if len(cont_number) == 10:
                datalist = []
                for i in range(0, len(cont_number), 2):
                    datalist.append(int(cont_number[i: i + 2], 16))

                for i in datalist:
                    cont_result = cont_result + chr(i)

            db_connect.close()
        except Exception as e:
            print("err get_controller_station_number_data : ", e)

        return cont_number, cont_result

    # 지정체 관련 값
    def get_congestion_info(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        value_list = [50, 30]
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
            cur = db_connect.cursor()

            sql = "select value from sw_parameter where param='congestion_criterion'"
            cur.execute(sql)
            result = cur.fetchone()
            value_list[0] = (int(result[0]))

            sql = "select value from sw_parameter where param='congestion_cycle'"
            cur.execute(sql)
            result = cur.fetchone()
            value_list[1] = (int(result[0]))

            db_connect.close()
        except Exception as e:
            print("err get_socket_info : ", e)

        return value_list

    # 버전
    def get_version_num(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        version_list = []
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
            cur = db_connect.cursor()
            sql = 'SELECT time FROM vds_version'
            cur.execute(sql)

            result = []
            for i in cur:
                result.append(i[0])
            result.sort(reverse=True)

            sql = "SELECT * FROM vds_version WHERE time='" + str(result[0]) + "';"
            cur.execute(sql)
            for i in cur:
                version_list.append(i)

            db_connect.close()
        except Exception as e:
            print("err get_version_num : ", e)

        return version_list

    # 교통량 데이터
    def get_traffic_data(self, cycle=None, sync_time=None, data_start=None, data_end=None, lane=6, max_distance=None,node_interval=None, share_interval=None, host=None, port=None, user=None, password=None,
                         db=None, charset='utf8'):
        traffic_data = []

        try:
            if sync_time is None and node_interval is None:
                print('nack')
            else:
                date_delete = datetime.fromtimestamp(sync_time - 120)  # 점유율에서 오래된 데이터(120초 전) 제거

                # 교통량 및 속도
                # Lane_traffic_data = [[차선별 교통량], [차선별 평균속도]]
                Lane_traffic_data = self.calc.Lane_traffic_data(data_start, data_end, lane, host, port, user, password, db, charset)

                # 점유율
                # occu = [차선별 점유율 Min][차선별 점유율 Max]
                occu = self.get_occupancy_interval_data(lane, host, port, user, password, db, charset)
                # share_data = [차선별 점유율]
                share_data = self.calc.Lane_share_data(occu, data_start, cycle, lane, host, port, user, password, db,
                                                       charset, date_delete)

                # 상하행
                lane_way = self.calc.lane_way(lane)
                if Lane_traffic_data != []:
                    # 전송 데이터 종합
                    if lane >= 1:
                        for i in range(lane):
                            #              [      교통량,                    속도,               점유율,         상/하행]
                            traffic_temp = [Lane_traffic_data[0][i], Lane_traffic_data[1][i], share_data[i],
                                            lane_way[i]]
                            traffic_data.append(traffic_temp)
                else:
                    traffic_data = []

        except Exception as e:
            print("err get_traffic_data : ", e)

        return traffic_data

    # 개별 차량 데이터
    def get_individual_traffic_data(self, cycle=None, sync_time=None, data_start=None, data_end=None, lane=6, host=None, port=None, user=None,
                                    password=None, db=None, charset='utf8'):
        individual_traffic_data = []

        try:
            if sync_time is None:
                print('nack')
            else:
                # 개별 차량 데이터
                individual_traffic_data = self.calc.Individual_car_data(data_start, data_end, lane, host, port, user, password, db, charset)

        except Exception as e:
            print("err get_individual_traffic_data : ", e)

        return individual_traffic_data

    # 차선별 누적 교통량 데이터
    def get_ntraffic_data(self, lane=6, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        ntraffic_data = []

        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset, autocommit=True)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)

            cur = db_connect.cursor()
            # 차선 오름차순으로 데이터 select
            sql = "SELECT * FROM traffic_info order by Lane asc"
            cur.execute(sql)
            result = cur.fetchall()
            if result[0][1] == 0 and result[1][1] == 0 and result[2][1] == 0 and result[3][1] == 0 and result[4][1] == 0 and result[5][1] == 0:
                ntraffic_data = []
            else:
                for i in range(lane):
                    ntraffic_data.append(result[i][1])  # result = [lane, nTraffic, totalVelocity]

                # 초기화 부분
                # mysql
                sql = "update traffic_info set nTraffic=0, totalVelocity=0 where Lane;"
                cur.execute(sql)
                db_connect.commit()
            db_connect.close()
        except Exception as e:
            print("err get_ntraffic_data : ", e)
        return ntraffic_data

    # 카테고리(속도) 기준 차선별 교통량
    def get_speed_data(self, sync_time=None, lane=6, cnum=[], host=None, port=None, user=None, password=None, db=None,
                       charset='utf8'):
        speed_data = []

        try:
            speed_data = self.calc.Category_speed_data(sync_time, cnum, lane, host, port, user, password, db, charset)
            # print(speed_data)
        except Exception as e:
            print("err get_speed_data : ", e)

        return speed_data

    # 함체 정보 데이터
    def get_controllerBox_state_data(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        controllerBox_state_list = []
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
            cur = db_connect.cursor()
            sql = "SELECT * FROM controlbox_status ORDER BY CASE WHEN param='Long_Power_Fail' THEN 1  WHEN param='Short_Power_Fail' THEN 2 WHEN param='Default_Parameter' THEN 3 WHEN param='Front_Door_Status' THEN 4 WHEN param='Back_Door_Status' THEN 5 WHEN param='Fan_Status' THEN 6 WHEN param='Heater_Stauts' THEN 7 WHEN param='Image_Status' THEN 8 WHEN param='Reset_Status' THEN 9 WHEN param='Temperature' THEN 10 WHEN param='Input_Voltage' THEN 11 WHEN param='Output_Voltage' THEN 12  ELSE 13 END;"
            cur.execute(sql)
            result = cur.fetchall()
            for i in range(0, len(result)):
                controllerBox_state_list.append(result[i][1])

            db_connect.close()
        except Exception as e:
            print("err get_controllerBox_state_data : ", e)

        return controllerBox_state_list

    # 지정체 데이터
    def get_congestion_data(self, congestion=None, cycle=None, node_interval=None, sync_time=None, host=None, port=None,
                            user=None, password=None, db=None, charset='utf8'):
        zone_data = []
        congestion_list = []
        try:
            if sync_time is None:
                print('nack')
            else:
                temp = time.localtime(sync_time - cycle)
                data_start = time.strftime("%Y-%m-%d %H:%M:%S", temp)
                zone_data = self.calc.congestion_data(node_interval=node_interval, data_start=data_start, host=host, port=port, user=user,
                                                      password=password, db=db, charset=charset)
                if zone_data is not None:
                    for i, lane_data in enumerate(zone_data):
                        for j, a_velocity in enumerate(lane_data):
                            # i+1 = 차선. j = 구역
                            current_lane = i + 1
                            if current_lane <= 3:
                                current_updown = 0
                            if current_lane >= 4:
                                current_updown = 1
                            if a_velocity < congestion and a_velocity != 0:  # 기준 속도 미만일 경우(30km미만)
                                if not any(item[1] == current_updown for item in self.last_congestion_list):
                                    congestion_list.append([current_lane, current_updown, j])
                                    self.last_congestion_list.append([current_lane, current_updown, j])
                                    print("30미만 last_congestion_list : ", self.last_congestion_list)
                            if a_velocity >= 50 and self.last_congestion_list is not None:  # 지정체 종료 속도이면서 이젠에 보낸 데이터가 있을 경우(50km이상)
                                if any(item[1] == current_updown for item in self.last_congestion_list):
                                    self.last_congestion_list = [item for item in self.last_congestion_list if item[2] != j or item[1] != current_updown]
                                    print("50이상 last_congestion_list : ", self.last_congestion_list)
        except Exception as e:
            print("err get_congestion_data : ", e)
        return zone_data, congestion_list

    # 돌발
    def outbreak(self, congestion=None, sync_time=None, cycle=None, host=None, port=None, user=None, password=None,
                 db=None, charset='utf8'):
        outbreak = []
        zone_data = []
        stop_list = []
        reverse_list = []

        congestion_status = []
        zone = 0
        lane = 0
        distlat = 0.0
        distlong = 0
        distance = 0
        try:
            if sync_time is None and cycle is None:
                print('nack')
            else:
                temp = time.localtime(sync_time - cycle)
                data_start = time.strftime("%Y-%m-%d %H:%M:%S", temp)
                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sync_time))
                zone_data = self.calc.congestion_data(data_start=data_start, host=host, port=port, user=user,
                                                      password=password, db=db, charset=charset)
                outbreak_data = self.calc.outbreak_data(data_start=data_start, now_time=now_time, host=host, port=port,
                                                        user=user, password=password, db=db, charset=charset)

                left_congestion_check = 0
                right_congestion_check = 0
                # 지정체
                if zone_data is not None:
                    for i, lane_data in enumerate(zone_data):  # [ [0,15,86,40,40,50,60] , [2] , [3] , [4]    ]
                        for j, a_velocity in enumerate(lane_data):  # [0,15,86,40,40,50,60]
                            # i+1 = 차선. j = 구역
                            current_lane = i + 1
                            if current_lane <= 3:
                                current_updown = 0
                            elif current_lane >= 4:
                                current_updown = 1

                            if a_velocity < congestion and a_velocity != 0:
                                if current_updown == 0:
                                    left_congestion_check = 1
                                elif current_updown == 1:
                                    right_congestion_check = 1
                                zone = j + 1
                                lane = current_lane

                #현재 지정체 상황 저장.
                if left_congestion_check == 0 and right_congestion_check == 0: # 지정체 없음
                    self.now_congestion = 0
                    self.current_congestion = None

                elif left_congestion_check == 1 and right_congestion_check == 0: # 상행 지정체
                    self.now_congestion = 1
                    self.current_congestion = [1, 1, 0]

                elif left_congestion_check == 0 and right_congestion_check == 1: # 하행 지정체
                    self.now_congestion = 2
                    self.current_congestion = [2, 2, 0]

                elif left_congestion_check == 1 and right_congestion_check == 1: # 양측 지정체
                    self.now_congestion = 3
                    self.current_congestion = [3, 3, 0]

                # insert 전 거리 계산.
                if lane == 1:
                    distlat = 18
                elif lane == 2:
                    distlat = 14.7
                elif lane == 3:
                    distlat = 11.2
                elif lane == 4:
                    distlat = 7.7
                elif lane == 5:
                    distlat = 4.2
                elif lane == 6:
                    distlat = 1.7

                distlong = zone * 25
                distance = math.sqrt(distlat**2 + distlong**2)

                #지정체 중복 검사 후 저장.
                if self.last_congestion != 0:
                    if self.last_congestion == self.now_congestion:
                        self.current_congestion = []
                    elif self.last_congestion != self.now_congestion:
                        outbreak.append([now_time, 0, 4, zone, distlat, distlong, distance])
                        congestion_status = self.current_congestion
                elif self.last_congestion is None:
                    outbreak.append([now_time, 0, 4, zone, distlat, distlong, distance])
                    congestion_status = self.current_congestion # [3,3,0] 저장.

                self.last_congestion = self.now_congestion # 현재 지정체 저장.

                if outbreak_data:
                    if self.last_outbreak_list:
                        for last_data in self.last_outbreak_list:
                            last_class = last_data[2]
                            last_zone = last_data[3]
                            for i in outbreak_data:
                                if last_class == 1 and i[2] == last_class and i[3] != last_zone:
                                    stop_list.append(i)
                                if last_class == 2 and i[2] == last_class and i[3] != last_zone:
                                    reverse_list.append(i)
                    else:
                        for i in outbreak_data:
                            if i[2] == 1:
                                stop_list.append(i)
                                self.last_outbreak_list.append(i)
                            if i[2] == 2:
                                reverse_list.append(i)
                                self.last_outbreak_list.append(i)

                    if stop_list:  # lastlist에 새로운 돌발 데이터가 담겨 있음 [time, ID, class, zone, Distlat, DistLong, distance] 형태
                        self.current_stop = [stop_list[0][3], 0, 0]
                        outbreak.extend(stop_list)
                    else:
                        self.current_stop = None

                    # 역주행
                    if reverse_list:
                        self.current_reverse = [reverse_list[0][3], 0, 0]
                        outbreak.extend(reverse_list)

        except Exception as e:
            print("err outbreak : ", e)
        return zone_data, outbreak

    # 돌발 상황 정보
    def get_outbreak(self, lane=6, zone_num=None, sync_time=None, cycle=None, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        # outbreak = [시간, 차선, 클래스, 거리, 상하행]
        outbreak = []
        try:
            if sync_time is None and cycle is None:
                print('nack')
            else:
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset,
                                             autocommit=True)
                cur = db_connect.cursor()
                # region 차선 간격 = lane_point
                sql = "SELECT value From sw_parameter WHERE param LIKE '%lanePoint' order by param asc;"
                cur.execute(sql)
                result = cur.fetchall()
                lane_point = []
                for data in result:
                    lane_point.append(float(data[0]))
                # endregion
                temp = time.time() - 1
                data_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(temp))
                sql = "SELECT * FROM outbreak WHERE time>='" + data_start + "' GROUP BY Class,ZONE ORDER BY time ASC, class ASC, idx ASC;"
                cur.execute(sql)
                result_ob = cur.fetchall()
                # print(result)
                # 상/하행
                if lane > 0:
                    lane_half = lane / 2
                    if result_ob:
                        for data in result_ob:
                            # out = [time, lane, class, distance, 상하행]
                            out = []
                            out.append(data[0])  # time
                            if data[3] is not None:
                                out.append(data[3])  # lane
                            else:
                                out.append(1)
                            out.append(data[2])  # class
                            out.append(data[6])  # distance
                            if data[3] is not None:
                                if data[3] <= lane_half:
                                    out.append(0)
                                elif lane_half < data[3] <= lane:
                                    out.append(1)
                            else:
                                out.append(0)
                            outbreak.append(out)
                db_connect.close()

        except Exception as e:
            print("err get_outbreak : ", e)
        return outbreak

    def get_ptz_info(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        ptz_info = []
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
            cur = db_connect.cursor()

            # ptz ip, port, id, password
            sql_ip = "SELECT value FROM sw_parameter WHERE Param='PTZ_IP';"
            sql_port = "SELECT value FROM sw_parameter WHERE Param='PTZ_PORT';"
            sql_id = "SELECT value FROM sw_parameter WHERE Param='PTZ_ID';"
            sql_password = "SELECT value FROM sw_parameter WHERE Param='PTZ_PW';"

            cur.execute(sql_id)
            result = cur.fetchone()
            ptz_info.append(result[0])

            cur.execute(sql_password)
            result = cur.fetchone()
            ptz_info.append(result[0])

            cur.execute(sql_ip)
            result = cur.fetchone()
            ptz_info.append(result[0])

            cur.execute(sql_port)
            result = cur.fetchone()
            ptz_info.append(result[0])

            db_connect.close()
        except Exception as e:
            print("error get_ptz_info : ", e)
        return ptz_info

    def get_location_data(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        result = []
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
            cur = db_connect.cursor()

            # 경도
            sql_2 = "SELECT value FROM sw_parameter WHERE param='longitude'"
            cur.execute(sql_2)
            temp = cur.fetchall()
            result.append(str(temp[0][0])[:10])

            # 위도
            sql_1 = "SELECT value FROM sw_parameter WHERE param='latitude'"
            cur.execute(sql_1)
            temp = cur.fetchall()
            result.append(str(temp[0][0])[:10])


            db_connect.close()
        except Exception as e:
            print("error get_location_data : ", e)
        return result

    def get_parameter_data(self, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        lane_num = None
        collect_cycle = None
        category_num = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        max_distance = None
        node_interval = None
        share_interval = None
        use_ntraffic = None
        use_category_speed = None
        outbreak_cycle = None
        use_unexpected = None
        parameter_list = []

        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
            cur = db_connect.cursor()
            sql = "SELECT * FROM parameter"
            cur.execute(sql)
            result = cur.fetchall()

            for i in range(len(result)):
                if result[i][0] == 1:
                    if (result[i][1] == 0) and result[i][2]:
                        tenp = result[i][2]
                        for i in range(0, 8):
                            if (tenp >> i) & 0x01 == 0x01:
                                lane_num = 8 - i

                    if (result[i][1] == 1) and result[i][2]:
                        tenp = result[i][2]
                        for i in range(0, 8):
                            if (tenp >> i) & 0x01 == 0x01:
                                lane_num = (8 - i) + 8


                elif result[i][0] == 3:
                    collect_cycle = result[i][2]
                elif result[i][0] == 5:
                    category_num[result[i][1]] = result[i][2]
                elif result[i][0] == 7:
                    use_ntraffic = result[i][2]
                elif result[i][0] == 9:
                    use_category_speed = result[i][2]
                elif result[i][0] == 11:
                    if result[i][1] == 0:
                        max_distance_f = result[i][2]
                    if result[i][1] == 1:
                        max_distance_b = result[i][2]
                    if result[i][1] == 2:
                        node_interval = result[i][2]
                    if result[i][1] == 3:
                        share_interval = result[i][2]
                elif result[i][0] == 13:
                    outbreak_cycle = result[i][2]
                elif result[i][0] == 19:
                    use_unexpected = result[i][2]

            db_connect.close()
            # index = 1
            parameter_list.append(lane_num)
            # index = 3
            parameter_list.append(collect_cycle)
            # index = 5
            parameter_list.append(category_num)
            # index = 7
            parameter_list.append(use_ntraffic)
            # index = 9
            parameter_list.append(use_category_speed)
            index = 11
            parameter_list.append(max_distance_f)
            print(max_distance_f)
            parameter_list.append(max_distance_b)
            parameter_list.append(node_interval)
            parameter_list.append(share_interval)
            index = 13
            parameter_list.append(outbreak_cycle)
            # index = 19
            parameter_list.append(use_unexpected)
        except Exception as e:
            print("err get_parameter_data : ", e)
        return parameter_list

    def get_occupancy_interval_data(self, lane=6, host=None, port=None, user=None, password=None, db=None,
                                    charset='utf8'):
        occupanvcy_interval_list = []
        try:
            # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
            db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
            cur = db_connect.cursor()

            temp_min = []
            temp_max = []
            # min 값 입력
            sql = "SELECT * FROM sw_parameter WHERE param LIKE '%occupancy_min' order by param asc;"
            cur.execute(sql)
            result = cur.fetchall()
            for i in range(lane):
                # result[1] => parameter value
                temp_min.append(int((result[i][1])))
            occupanvcy_interval_list.append(temp_min)

            # max 값 입력
            sql = "SELECT * FROM sw_parameter WHERE param LIKE '%occupancy_max' order by param asc;"
            cur.execute(sql)
            result = cur.fetchall()
            for i in range(lane):
                # result[1] => parameter value
                temp_max.append(int((result[i][1])))
            occupanvcy_interval_list.append(temp_max)

            db_connect.close()
        except Exception as e:
            print("err get_occupancy_interval_data : ", e)
        return occupanvcy_interval_list

    # endregion

    # region set data
    # socket ip & port
    def set_socket_info(self, socket_info=[], host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        try:
            if socket_info == '':
                print("parameter in none")
            else:
                # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
                cur = db_connect.cursor()
                # socket_info = [ip, socket]
                sql_1 = "UPDATE sw_parameter set value='" + str(socket_info[0]) + "' WHERE param='SOCKET_IP'"
                sql_2 = "UPDATE sw_parameter set value='" + str(socket_info[1]) + "' WHERE param='SOCKET_PORT'"

                cur.execute(sql_1)
                cur.execute(sql_2)

                db_connect.close()
                return True
        except Exception as e:
            print("error set_socket_info : ", e)
            return False

    def set_controller_station_number_data(self, cont_num=None, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        try:
            if cont_num == '':
                print("parameter in none")
            else:
                # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
                cur = db_connect.cursor()

                sql = "UPDATE sw_parameter set value='" + str(cont_num) + "' WHERE param='Controller_station_number'"

                cur.execute(sql)

                db_connect.close()
        except Exception as e:
            print("error set_controller_station_number_data : ", e)

    def set_congestion_info(self, change_list=[], host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        try:
            if change_list == '':
                print("parameter in none")
            else:
                # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
                cur = db_connect.cursor()
                # socket_info = [congestion, zone]
                sql_1 = "UPDATE sw_parameter set value='" + str(change_list[0]) + "' WHERE param='congestion_criterion'"
                sql_3 = "UPDATE sw_parameter set value='" + str(change_list[1]) + "' WHERE param='congestion_cycle'"

                cur.execute(sql_1)
                cur.execute(sql_3)

                db_connect.close()
        except Exception as e:
            print("error set_congestion_info : ", e)

    def insert_outbreak(self, outbreakdata_list=[], node_interval=None, zone=None, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        # congestion_list = 지정체 구역 = [차선 (1부터), 구역 (0부터)]
        # input_time = 지정체 발생 시간
        # zone = 구역 간격
        # zone_num = 차선별 구역 수
        try:
            if outbreakdata_list == '' or zone is None or node_interval is None: # outbreakdata_list = [time, ID, class, zone, Distlat, DistLong, distance]
                print("parameter in none")
            else:
                # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
                cur = db_connect.cursor()

                print("outbreakdata_list: ", outbreakdata_list)
                for i in range(len(outbreakdata_list)):
                    if outbreakdata_list[i][2] == 4:
                        outbreakdata = outbreakdata_list[i]
                        sql = "INSERT INTO outbreak VALUES(%s, %s, %s, %s, %s, %s, %s)"
                        cur.execute(sql, outbreakdata)

                db_connect.close()
        except Exception as e:
            print("error insert_outbreak : ", e)

    # S/W 파라미터 저장
    def set_paramete_data(self, parameter_list=[], host=None, port=None, user=None, password=None, db=None,
                          charset='utf8'):
        try:
            if parameter_list == '':
                print("parameter in none")
            else:
                lane = 1 << (16 - parameter_list[0])
                lane_1 = lane >> 8
                lane_2 = lane & 0xFF
                list = [lane_1, lane_2]
                for i in range(1, len(parameter_list)):
                    list.append(parameter_list[i])
                print("list: ", list)

                # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
                cur = db_connect.cursor()
                sql = "SELECT Param, Nbyte from parameter ORDER BY Param asc"
                cur.execute(sql)
                index_list = []
                for i in cur:
                    index_list.append((i[0], i[1]))
                index = 0
                for i in range(len(list)):
                    if type(list[i]) == type([]):
                        for j in range(len(list[i])):
                            sql = "UPDATE parameter set Data=" + str(list[i][j]) + " WHERE Param=" + str(
                                index_list[index][0]) + " AND Nbyte=" + str(index_list[index][1]) + ";"
                            index += 1
                            cur.execute(sql)
                    else:
                        sql = "UPDATE parameter set Data=" + str(list[i]) + " WHERE Param=" + str(
                            index_list[index][0]) + " AND Nbyte=" + str(index_list[index][1]) + ";"
                        index += 1
                        cur.execute(sql)

                db_connect.close()
        except Exception as e:
            print("err set_paramete_data : ", e)

    # endregion

    # region save
    def save_Log_data(self, msg_list=[], host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        try:
            if msg_list == '':
                print("parameter in none")
            else:
                # db_connect = pymssql.connect(server=host, port=port, user=user, password=password, database=db, charset=charset)
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset, autocommit=True)
                cur = db_connect.cursor()
                sql = ''

                if self.log_count == 100:
                    self.log_count = 0

                if len(msg_list) == 5:
                    sql = "INSERT INTO vds_log values(" + str(self.log_count) + ",'" + msg_list[0] + "', '" + msg_list[1] + "', '" + msg_list[2] + "', '" + msg_list[3] + "', '" + msg_list[4] + "');"
                elif len(msg_list) == 4:
                    sql = "INSERT INTO vds_log values(" + str(self.log_count) + ",'" + msg_list[0] + "', '" + msg_list[1] + "', '" + msg_list[2] + "', '" + msg_list[3] + "', ' ');"
                elif len(msg_list) == 3:
                    sql = "INSERT INTO vds_log values(" + str(self.log_count) + ",'" + msg_list[0] + "', '" + msg_list[1] + "', '" + msg_list[2] + "', ' ', ' ');"
                self.log_count += 1

                # print(sql)
                cur.execute(sql)
                db_connect.close()


        except Exception as e:
            print("err save_Log_data : ", e)
    # endregion
