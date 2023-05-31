import sys
import os

from PyQt5.uic          import loadUi
from PyQt5.QtGui        import QIcon, QPainter, QColor, QFont, QPen, QBrush, QPainterPath
from PyQt5.QtWidgets    import *
from PyQt5.QtCore       import Qt

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class Status_function(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = loadUi(resource_path('status_w.ui'), self)
        self.setWindowIcon(QIcon(resource_path("hbrain.png")))
        self.lane = 6
        self.congestion_criterion = 50
        self.zone_criterion = 60
        self.zone_num = None
        self.max_distance = 200
        self.node_interval = 25
        self.cell_num = None
        self.congestion_data = None

    def get_data(self, max_distance=None, lane=None, congestion_criterion=None, node_interval=None, congestion_data=None):
        # 차선
        if lane:
            self.lane = lane

        # 지정체 기준값
        if congestion_criterion:
            self.congestion_criterion = congestion_criterion

        # 최대 검지 거리
        if max_distance:
            self.max_distance = max_distance
            self.cell_num = int(self.max_distance / self.node_interval)

        # 간격
        if node_interval:
            self.node_interval = node_interval
            self.cell_num = int(self.max_distance / node_interval)

        # 셀별 데이터
        if congestion_data:
            self.congestion_data = congestion_data

    def paintEvent(self, QPaintEvent):
        qp = QPainter()
        qp.begin(self)
        self.draw_other(qp, self.lane, self.node_interval, self.max_distance)
        self.draw_congestion(qp, self.node_interval, self.congestion_data, self.congestion_criterion, self.max_distance)
        qp.end()
        self.update()

    def draw_other(self, qp, lane, node_interval, max_distance):
        qp.setFont(QFont('Consolas', 12))
        # (35, 25)      (335, 25)
        # (35, 825)     (335, 825)
        # 비율
        ratio = 800 / max_distance
        # 차선
        if lane:
            for i in range(lane + 1):
                if i == (lane / 2):  # 중앙선
                    qp.setPen(QPen(Qt.yellow, 3, Qt.SolidLine))
                    qp.drawLine(35 + 50 * i, 25, 35 + 50 * i, 825)
                else:  # 일반 차선
                    qp.setPen(QPen(Qt.white, 2, Qt.SolidLine))
                    qp.drawLine(35 + 50 * i, 25, 35 + 50 * i, 825)

        # 구역
        qp.setPen(QPen(Qt.white, 2, Qt.SolidLine))
        if node_interval:
            for i in range(self.cell_num + 1):
                qp.drawText(0, 825 - node_interval * i * ratio, str(node_interval * i) + 'm')
                qp.drawLine(35, 825 - node_interval * i * ratio, 335, 825 - node_interval * i * ratio)
            qp.drawText(0, 25, str(max_distance) + 'm')
            qp.drawLine(35, 25, 335, 25)

    def draw_congestion(self, qp, node_interval, congestion_data, congestion_criterion, max_distance):
        # 비율
        ratio = 800 / max_distance
        lane_cell_num = int(max_distance / node_interval)
        try:
            cell_data = [congestion_data[i:i + lane_cell_num] for i in range(0, len(congestion_data), lane_cell_num)]
            for i, lane_data in enumerate(cell_data):
                for j in range(len(lane_data)):
                    qp.drawText(40 + 50 * i, 825 - node_interval * j * ratio, str(lane_data[j]))
                    if j == len(lane_data) - 1:
                        if lane_data[j] == 0:
                            qp.fillRect(35 + 50 * i, 25, 50, 800 - (node_interval * ratio) * j,
                                        QBrush(QColor(Qt.green), Qt.BDiagPattern))
                        elif 0 < lane_data[j] < (congestion_criterion - 10):
                            qp.fillRect(35 + 50 * i, 25, 50, 800 - (node_interval * ratio) * j,
                                        QBrush(QColor(Qt.red), Qt.BDiagPattern))
                        elif (congestion_criterion - 10) <= lane_data[j] < congestion_criterion:
                            qp.fillRect(35 + 50 * i, 25, 50, 800 - (node_interval * ratio) * j,
                                        QBrush(QColor(Qt.yellow), Qt.BDiagPattern))
                        elif congestion_criterion <= lane_data[j]:
                            qp.fillRect(35 + 50 * i, 25, 50, 800 - (node_interval * ratio) * j,
                                        QBrush(QColor(Qt.green), Qt.BDiagPattern))
                    else:
                        if lane_data[j] == 0:
                            qp.fillRect(35 + 50 * i, 825 - (node_interval * ratio) * (j + 1), 50, node_interval * 4,
                                        QBrush(QColor(Qt.green), Qt.BDiagPattern))
                        elif 0 < lane_data[j] < (congestion_criterion - 10):
                            qp.fillRect(35 + 50 * i, 825 - (node_interval * ratio) * (j + 1), 50, node_interval * 4,
                                        QBrush(QColor(Qt.red), Qt.BDiagPattern))
                        elif (congestion_criterion - 10) <= lane_data[j] < congestion_criterion:
                            qp.fillRect(35 + 50 * i, 825 - (node_interval * ratio) * (j + 1), 50, node_interval * 4,
                                        QBrush(QColor(Qt.yellow), Qt.BDiagPattern))
                        elif congestion_criterion <= lane_data[j]:
                            qp.fillRect(35 + 50 * i, 825 - (node_interval * ratio) * (j + 1), 50, node_interval * 4,
                                        QBrush(QColor(Qt.green), Qt.BDiagPattern))
        except Exception as e:
            pass
            # print("DATA Not ready yet")
            # self.error_show('error', 'DATA Not ready yet!')

    def error_show(self, title, text):
        m_box = QMessageBox()
        m_box.warning(self, title, text)
        m_box.setStyleSheet("background-color:white; color:black;")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Status_function()
    ex.show()
    app.exec_()
