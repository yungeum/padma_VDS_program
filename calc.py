import pymysql
# import pymysql
import time
import math
import datetime


class CALC_function:
    def __init__(self):
        super().__init__()

    #차선 별 교통량 및 평균 속도  catchline[[교통량][속도]]
    def Lane_traffic_data(self, data_start=None, lane=6, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        Lane_traffic_data = []

        try:
            if data_start is None:
                print('nack')
            else:
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()

                # category = 0 중 data_start 이후 값
                # category 0->교통정보수집선. 1-> 점유율 시작선 2-> 점유율 종료선
                sql = "SELECT * FROM traffic_detail WHERE category = 0 and time >='" + data_start + "' order by Zone asc, ID asc, time asc;"

                cur.execute(sql) # 쿼리 실행
                result = cur.fetchall() # cur.fetchall() -> 이전에 실행한 쿼리의 모든 결과 반환
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
                    lane_index = data[3] - 1 # 이거 이해 안됨 zone이 자선이라서 그냥 사용하면 되는거 아닌가
                    velocity = data[2]

                    traffic[lane_index] += 1     # 차량 갯수 +1
                    speed[lane_index] += velocity  # 차량 속도 합산

                # 속도 종합 값을 차량수로 나눈 평균
                for i in range(lane):
                    if traffic[i] != 0:
                        speed[i] = round((speed[i]/traffic[i]))
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
    def Lane_share_data(self, occu=None, data_start=None, cycle = 30, lane=6, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        share_data = []

        try:
            if (occu is None) or (data_start is None):
                print('nack')
            else:
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()
                sql_str = "select *from obj_info where ((Zone= 1 and (DistLong BETWEEN '" + str(occu[0][0]) + "' AND '" + str(occu[1][0]) + "'))"
                for i in range(1, lane):
                    sql_str += "or (Zone=" + str(i + 1) + " and (DistLong BETWEEN '" + str(occu[0][i]) + "' AND '" + str(occu[1][i]) + "'))"
                sql_str += ") and time >= '" + data_start + "' order by Zone asc, ID asc, time asc "
                sql = sql_str

                cur.execute(sql)
                result = cur.fetchall()
                ttime = [0]  # 차량 데이터 시작점 끝점 저장
                timegap = []  # 차선별 차량 점유율 합
                timeoc = []  # 차선별 속도 점유율 %
                coun = []  # 차선별 차량수
                for i in range(lane):
                    timegap.append(0)
                    timeoc.append(0)
                    coun.append(0)

                for i in range(0, len(result) - 1):
                    # result[i][1] = ID / result[i][14] = zone / result[i][3] = DistLong
                    if result[i][1] != result[i + 1][1] or result[i][14] != result[i + 1][14] or abs(
                            result[i][3] - result[i + 1][3]) > 3:  # id변경 , zone 변경, 같은id다른 차량 검지(distlong 기준)
                        ttime.append(i)
                        ttime.append((i + 1))
                ttime.append((len(result)-1))

                # 차선별 차량들 데이터 시작점 끝점 확보
                if len(result) > 1:
                    for i in range(0, len(ttime), 2):  # 차선별 차량 데이터 시작점 기준으로 계산
                        for j in range(lane):
                            if result[ttime[i]][14] % lane == j:
                                timegap[j] += ((result[ttime[i]][0] - result[ttime[i + 1]][0]).microseconds / 1000000) / cycle  # 차량 점유시간 기준 개별 점유율 계산
                                coun[j] += 1

                for j in range(lane):
                    if coun[j] != 0:
                        timeoc[j] = round(timegap[j] * 100 / coun[j]) # 차선별 개별 점유율 총합하여 종합 차선별 속도점유율 % 변환
                    else:
                        timeoc[j] = 0

                timeoc.append(timeoc[0])
                del timeoc[0]

                share_data = timeoc

                db_connect.close()
        except Exception as e:
            print("err share_data : ", e)
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
    def Individual_car_data(self, data_start=None, lane=6, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        Icar_data = []

        try:
            if (data_start is None) :
                print('nack')
            else:
                data_count = datetime.datetime.strptime(data_start, '%Y-%m-%d %H:%M:%S')
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()
                sql = "SELECT * FROM traffic_detail WHERE category = 0 and time >='" + data_start + "' order by Zone asc, ID asc, time asc;"

                cur.execute(sql)
                result = cur.fetchall()

                for res in result:
                    car_data = [0, 0, 0, 0, 0]
                    car_data[0] = res[3]                            # Zone
                    car_data[1] = (res[0] - data_count).seconds     # 경과 시간
                    car_data[2] = res[2]                            # 속도
                    if res[3] <= (lane/2):
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
                # print('now_time type: ', type(now_time))
                sql2 = "UPDATE sw_parameter SET value = '"+now_time+"' WHERE param = 'last_time_Cspeed';" # 동기화 시간 저장
                cur.execute(sql2)
                db_connect.commit()

                # print('data_start type: ', type(data_start))
                sql = "SELECT * FROM traffic_detail WHERE category = 0 and time >='" + data_start + "' order by Zone asc, ID asc, time asc;"
                # print(sql)
                cur.execute(sql)
                result = cur.fetchall()

                for i in range(lane):
                    lane_speed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    for res in result:
                        if res[3] == (i + 1): # 차선 일치 확인
                            for j in reversed(range(len(cnum))):
                                if res[2] >= cnum[j]: # 속도 범위 확인
                                    lane_speed[j] += 1
                                    break

                    Cspeed_data.append(lane_speed)

                db_connect.close()
        except Exception as e:
            print("err Cspeed_data : ", e)
        return Cspeed_data

    # 지정체
    def congestion_data(self, zone=10, data_start=None, host=None, port=None, user=None, password=None, db=None, charset='utf8'):
        # 전체 차선 zone별 평균속도 list [[1차선 1구역 평균속도, 1차선 2구역 평균속도 ..] ...[6차선 1구역 평균속도, 6차선 2구역 평균속도 ..]]
        lane_zone_list = []

        try:
            if (data_start is None) or (zone is None):
                print('nack')
            else:
                # now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data_start))
                db_connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
                cur = db_connect.cursor()

                sql = "SELECT * FROM obj_info WHERE time>'" + data_start + "'"
                cur.execute(sql)
                result = cur.fetchall()
                # result
                # [time, ID, Distlat, Distlong, VrelLat, VrelLong, Velocity, RCS, Prob, ArelLat, ArelLong, Class, Length, Width. zone, lane]

                # region 필요한 변수 선언
                # obj_info 차선별 구분
                lane_1_data = []
                lane_2_data = []
                lane_3_data = []
                lane_4_data = []
                lane_5_data = []
                lane_6_data = []

                # 차선별 zone 개수
                zone_num = 0
                if 200 % zone == 0:
                    zone_num = int(200/zone)
                else:
                    zone_num = int(200/zone) + 1

                # endregion
                for data in result:
                    # 차선 비교
                    if data[15] == 1:
                        # [data[3], data[6]] = [DistLong, Velocity]
                        lane_1_data.append([data[3], data[6]])
                    elif data[15] == 2:
                        lane_2_data.append([data[3], data[6]])
                    elif data[15] == 3:
                        lane_3_data.append([data[3], data[6]])
                    elif data[15] == 4:
                        lane_4_data.append([data[3], data[6]])
                    elif data[15] == 5:
                        lane_5_data.append([data[3], data[6]])
                    elif data[15] == 6:
                        lane_6_data.append([data[3], data[6]])

                lane_data = [lane_1_data, lane_2_data, lane_3_data, lane_4_data, lane_5_data, lane_6_data]
                for lane_num, data in enumerate(lane_data):
                    # temp = 차선 zone별 평균속도 list
                    temp = []
                    temp_num = []
                    for i in range(zone_num):
                        temp.append(0)
                        temp_num.append(0)
                    for lane_data in data:
                        for i in range(1, zone_num+1):
                            # lane_data[0] = 거리 / lane_data[1] = 속도
                            if lane_data[0] > zone * (zone_num - i): #10 * 1  , 10 * 2
                                temp[zone_num - i] += lane_data[1] # 구역별 총 속도
                                temp_num[zone_num - i] += 1        # 구역별 총 갯수
                                break
                    for i in range(zone_num):
                        if temp_num[i] > 1: # 2대 이상
                            temp[i] = int(temp[i] / temp_num[i])

                    lane_zone_list.append(temp)

                # print("lane_zone_list", lane_zone_list)

                db_connect.close()
        except Exception as e:
            print("err congestion_data : ", e)
        return lane_zone_list
