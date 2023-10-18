import pymysql
# import pymysql
import time
import math
import datetime



class CALC_function:
    def __init__(self):
        super().__init__()
        self.car_non_confirm = []
        self.last_data_time = None

    #차선 별 교통량 및 평균 속도  catchline[[교통량][속도]]
    def Lane_traffic_data(self, data_start=None, data_end=None, lane=6, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        Lane_traffic_data = []

        try:
            if data_start is None:
                print('nack')
            else:
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()

                # category = 0 중 data_start 이후 값
                # category 0->교통정보수집선. 1-> 점유율 시작선 2-> 점유율 종료선
                sql = "SELECT * FROM traffic_detail WHERE category = 1 and time >='" + data_start + "' and time <='" + data_end + "' order by Zone asc, ID asc, time asc;"
                cur.execute(sql) # 쿼리 실행
                result = cur.fetchall() # cur.fetchall() -> 이전에 실행한 쿼리의 모든 결과 반환
                if len(result) == 0:
                    Lane_traffic_data = []
                else:
                    traffic = []
                    speed = []

                    # 차선 수 만큼 0값 추가
                    # traffic = [0,0,0, ... ,0,0,0]
                    # speed = [0,0,0, ... ,0,0,0]
                    for i in range(lane):
                        traffic.append(0)
                        speed.append(0)

                    for data in result:
                        # lane_index -> zone - 1 (traffic[0], speed[0]부터 넣기 위함)
                        lane_index = int(data[4] / 8)
                        velocity = data[3]

                        traffic[lane_index] += 1  # 차량 갯수 +1
                        speed[lane_index] += velocity  # 차량 속도 합산

                    # 속도 종합 값을 차량수로 나눈 평균
                    for i in range(lane):
                        if traffic[i] != 0:
                            speed[i] = round((speed[i] / traffic[i]))
                        else:
                            speed[i] = 0

                    # Lane_traffic_data = [[차선별 교통량], [차선별 평균속도]]
                    Lane_traffic_data.append(traffic)
                    Lane_traffic_data.append(speed)
                db_connect.close()
        except Exception as e:
            print("err Lane_traffic_data : ", e)
        return Lane_traffic_data

    # 점유율 계산 lane별
    def Lane_share_data(self, occu=None, data_start=None, cycle = None, lane=6, host=None, port=None, user=None, password=None, db=None, charset='utf8', data_delete=None):
        share_data = []

        try:
            if (occu is None) or (data_start is None):
                print('nack')
            else:
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()
                sql_str = "SELECT * FROM traffic_detail WHERE time >='" + data_start + "' order by Zone asc, ID asc, time asc;"
                cur.execute(sql_str)
                result = cur.fetchall()

                car_data = []  # 차량 데이터 필터링.
                share_time = []  # cell별 시간 점유율 총 시간
                share_time_percent = []  # cell별 시간 점유율 총 시간 / cycle  ==> 점유율 %
                car_count = []  # cell별 차량수

                for i in range(lane):
                    share_time.append(0)
                    share_time_percent.append(0)
                    car_count.append(0)

                result = list(result)

                for i in range(len(self.car_non_confirm)):
                    result.append(self.car_non_confirm[i])
                self.car_non_confirm.clear()  # 삭제
                sorted_result = []

                sorted_result = sorted(result, key=lambda x: (x[4], x[1], x[0].timestamp()))
                for i in range(len(sorted_result)):
                    sorted_result[i] = sorted_result[i] + (None,)  # [i][7] = 정체 check
                # result[i][1] = ID / result[i][2] = DistLong / result[i][4] = zone / result[i][6] = category
                for i in range(0, len(sorted_result) - 1):
                    car_data.append(i)
                    if sorted_result[i][1] == sorted_result[i + 1][1] and sorted_result[i][4] == sorted_result[i + 1][
                        4] and abs(sorted_result[i][2] - sorted_result[i + 1][2]) < 10 and sorted_result[i + 1][6] == 2:
                        car_data.append(i + 1)  # category 1,2 나란히 append
                        i = i + 1
                    else:
                        if sorted_result[i][0] > data_delete and sorted_result[i][6] != 2:  # car_non_confirm에 들어있는 데이터 중 오랫동안 남아있는 데이터 제거.
                            if sorted_result[i][7] == 1:  # [i][7] = 정체 check
                                share_time_percent[sorted_result[i][4]] = 100
                            sorted_result[i] = sorted_result[i] + (1,)
                            self.car_non_confirm.append(sorted_result[i])

                        # category 가 나란히 들어오지 않은 객체 =  아직 빠져 나가지 않은 차량
                        # 전역 리스트에 저장 후 POP.
                        car_data.pop()

                if len(sorted_result) > 1:
                    for i in range(0, len(car_data) - 1, 2):  # 0,2,4 ... 나란히 append 되어 있어서
                        for j in range(lane):
                            if (sorted_result[car_data[i]][4] - 1) == j:  # Cell 이 같을 때
                                endline = sorted_result[car_data[i + 1]][0]  # category = 2
                                startline = sorted_result[car_data[i]][0]  # category = 1
                                delta = endline - startline
                                millseconeds = delta.total_seconds()
                                share_time[j] += millseconeds  # 점유한 시간 계산 후 timegap[j]에 합. # 차량 점유시간
                                car_count[j] += 1  # 차량 수
                for k in range(lane):
                    if car_count[k] != 0:
                        share_time_percent[k] = share_time_percent[k] + round(
                            (share_time[k] / cycle) * 100)  # cell 마다 (차량 점유 시간 )
                        if share_time_percent[k] > 100:
                            share_time_percent[k] = 100
                    else:
                        share_time_percent[k] = 0

                share_data = share_time_percent  # 리턴 해줄 셀 별 점유율
                db_connect.close()
        except Exception as e:
                    print("err Lane_share_data : ", e)
        return share_data

    # 상/하행
    def lane_way(self, lane=6):
        lane_way = []
        try:
            if lane <= 0:
                print('nack')
            else:
                if lane >= 1:
                    lane_half = lane / 2
                    for j in range(1, lane+1):
                        # 상/하행
                        if j <= lane_half:
                            lane_way.append(0)
                        else:
                            lane_way.append(1)

        except Exception as e:
            print("err lane_way : ", e)
        return lane_way

    # 개별 차량 데이터
    def Individual_car_data(self, data_start=None, data_end=None, lane=6, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        Icar_data = []

        try:
            if (data_start is None) :
                print('nack')
            else:
                data_count = datetime.datetime.strptime(data_start, '%Y-%m-%d %H:%M:%S')
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()
                sql = "SELECT * FROM traffic_detail WHERE category = 2 and time >='" + data_start + "' and time <='" + data_end + "' order by Zone asc, ID asc, time asc;"
                cur.execute(sql)
                result = cur.fetchall()
                for res in result:
                    car_data = [0, 0, 0, 0, 0]
                    car_data[0] = res[4]                            # Zone
                    car_data[1] = (res[0] - data_count).seconds     # 경과 시간
                    car_data[2] = res[3]                            # 속도
                    if res[4] <= (lane/2):
                        updown = 0
                    else:
                        updown = 1
                    car_data[3] = updown                             # 상하행
                    car_data[4] = 1     # res[5]                     # 차량 종류
                    Icar_data.append(car_data)

                db_connect.close()
        except Exception as e:
            print("err Individual_car_data : ", e)
        return Icar_data

    # 카테고리(속도) 기준 차선별 교통량
    def Category_speed_data(self, sync_time=None, cnum=[], lane=6, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        Cspeed_data = []
        # Cspeed_data = [[1차선 카테고리별 데이터],[2차선 카테고리별 데이터],...., [n-1차선 카테고리별 데이터],[n차선 카테고리별 데이터]]

        try:
            if (sync_time is None) or (cnum == []) or (len(cnum) != 12):
                print('nack')
            else:
                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sync_time))
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()

                sql1 = "SELECT * FROM sw_parameter WHERE param = 'last_time_Cspeed';"  # 이전 동기화 시간 호출
                cur.execute(sql1)
                result = cur.fetchall()
                data_start = result[0][1]
                if data_start is None:
                    data_start = now_time
                sql = "SELECT * FROM traffic_detail WHERE category = 2 and time >='" + data_start + "' order by Zone asc, ID asc, time asc;"
                cur.execute(sql)
                after_time = time.strftime("%Y-%m-%d %H:%M:%S")
                result = cur.fetchall()
                if len(result) == 0:
                    Cspeed_data = []
                else:
                    for i in range(lane):
                        lane_speed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        for res in result:
                            if res[4] == (i + 1):  # 차선 일치 확인
                                for j in reversed(range(len(cnum))):
                                    if res[3] >= cnum[j]:  # 속도 범위 확인
                                        lane_speed[j] += 1
                                        break
                        Cspeed_data.append(lane_speed)

                sql2 = "UPDATE sw_parameter SET value = '"+after_time+"' WHERE param = 'last_time_Cspeed';" # 동기화 시간 저장
                cur.execute(sql2)
                db_connect.commit()
                db_connect.close()
        except Exception as e:
            print("err Cspeed_data : ", e)
        return Cspeed_data

    # 지정체
    def congestion_data(self, data_start=None, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        # 전체 차선 zone별 평균속도 list [[1차선 1구역 평균속도, 1차선 2구역 평균속도 ..] ...[6차선 1구역 평균속도, 6차선 2구역 평균속도 ..]]
        velocity_A_cell_list = []

        try:
            if data_start is None:
                print('nack')
            else:
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()

                sql = "SELECT * FROM traffic_detail WHERE category = 2 and time>='" + data_start + "' ORDER BY Zone ASC"  # 여기서 zone 은 lane category = 3 셀을 지나가는 순간 수정필요 0907
                cur.execute(sql)
                result = cur.fetchall()  # [time, ID, DistLong, Velocity, Zone, class, category]

                lane_data_list = []

                lane_1_data = []
                lane_2_data = []
                lane_3_data = []
                lane_4_data = []
                lane_5_data = []
                lane_6_data = []

                zone = 25
                zone_num = int(200 / zone)  # 나눴을 때 딱 맞게 떨어지지 않으면 날려버리기로 했으니까 굳이 +1 할 필요가 없음

                for data in result:
                    # 차선 비교
                    if data[4] >= 0 and data[4] <= 7:
                        # [data[2], data[3]] = [DistLong, Velocity]
                        lane_1_data.append([data[2], data[3]])
                    elif data[4] >= 8 and data[4] <= 15:
                        lane_2_data.append([data[2], data[3]])
                    elif data[4] >= 16 and data[4] <= 23:
                        lane_3_data.append([data[2], data[3]])
                    elif data[4] >= 24 and data[4] <= 31:
                        lane_4_data.append([data[2], data[3]])
                    elif data[4] >= 32 and data[4] <= 39:
                        lane_5_data.append([data[2], data[3]])
                    elif data[4] >= 40 and data[4] <= 47:
                        lane_6_data.append([data[2], data[3]])

                lane_data = [lane_1_data, lane_2_data, lane_3_data, lane_4_data, lane_5_data, lane_6_data]

                for lane_num, data in enumerate(lane_data):
                    # temp = 차선 zone별 평균속도 list
                    temp = []
                    temp_num = []
                    for i in range(zone_num):
                        temp.append(0)
                        temp_num.append(0)
                    for lane_data in data:
                        for i in range(1, zone_num + 1):
                            # lane_data[0] = 거리 / lane_data[1] = 속도
                            if lane_data[0] > zone * (zone_num - i):
                                temp[zone_num - i] += lane_data[1]  # 구역별 총 속도
                                temp_num[zone_num - i] += 1  # 구역별 총 갯수
                                break
                    for i in range(zone_num):
                        if temp_num[i] > 1:  # 2대 이상
                            temp[i] = int(temp[i] / temp_num[i])

                    lane_data_list.append(temp)
                db_connect.close()
        except Exception as e:
            print("err congestion_data : ", e)
        return lane_data_list

    # 정차
    def outbreak_data(self, data_start=None, now_time=None, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        try:
            if data_start is None:
                print('nack')
            else:
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()
                datett = str(self.last_data_time)
                if self.last_data_time is not None:
                    sql = "SELECT * FROM outbreak WHERE time>'" + datett + "' ORDER BY Zone ASC"
                else:
                    sql = "SELECT * FROM outbreak WHERE time>'" + now_time + "' ORDER BY Zone ASC"
                cur.execute(sql)
                result = cur.fetchall()

                data_list = []

                for data in result:
                    data_list.append(data)
                if result:
                    self.last_data_time = result[-1][0]

                db_connect.close()
        except Exception as e:
            print("err outbreak_data : ", e)
        return data_list