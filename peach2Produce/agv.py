# -*- coding: utf-8 -*-
import socket  # socket模块
import threading
from models import AgvPos, RobotInfo
import config

HOST = config.HOST
PORT = 9001

fixed_location = {
    (44, 0): (0, 0.5)
    , (45, 0): (0.058, 0.5)
    , (46, 0): (0.058 * 2, 0.5)

    , (47, 0): (0.058 * 3, 0.5)
    , (48, 0): (0.058 * 4, 0.5)
    , (49, 0): (0.058 * 5, 0.5)
    , (50, 0): (0.058 * 6, 0.5)
    , (51, 0): (0.058 * 7, 0.5)
    , (52, 0): (0.058 * 8, 0.5)
    , (53, 0): (0.058 * 9, 0.5)
    , (54, 0): (0.058 * 10, 0.5)
    , (55, 0): (0.058 * 11, 0.5)
    , (56, 0): (0.058 * 12, 0.5)
    , (57, 0): (0.058 * 13, 0.5)
    , (58, 0): (0.058 * 14, 0.5)
    , (59, 0): (0.058 * 15, 0.5)
    , (60, 0): (0.058 * 16, 0.5)
    , (61, 0): (1, 0.5)

    , (62, 0): (0.029, 0.2)
    , (66, 0): (0.058, 0.4)
    , (67, 0): (0.058, 0.35)
    , (68, 0): (0.058, 0.3)
    , (69, 0): (0.058, 0.2)

    , (70, 0): (0.058 * 6, 0.4)

    , (77, 0): (0.058 * 7, 0.3)
    , (78, 0): (0.058 * 7, 0.2)
    , (79, 0): (0.058 * 7, 0.2)
    , (80, 0): (0.058 * 7, 0.2)
    , (81, 0): (0.058 * 7, 0.2)
    , (82, 0): (0.058 * 7, 0.2)
    , (83, 0): (0.058 * 7, 0.2)
    , (84, 0): (0.058 * 12, 0.5)
    , (86, 0): (0.058 * 12, 0.5)
    , (92, 0): (0.058 * 12, 0.5)
    , (93, 0): (0.058 * 12, 0.5)
    , (94, 0): (0.058 * 12, 0.5)
    , (95, 0): (0.058 * 12, 0.5)

    , (96, 0): (0.058 * 15, 0.5)

}

# (46,0),(47,0),(48,0),(49,0),(50,0),(51,0),(52,0),(53,0),(54,0),(55,0),(56,0),(57,0),(58,0),(59,0),(60,0),(61,0),(62,0),(66,0),(70,0),(77,0),(84,0),(96,0)}

last_location = (-1, -1)
last_real_location = (-1, -1)
last_update_location = (-1, -1)


def calc(x, y, tag, AgvAngle):
    global last_location, fixed_location
    if (tag, 0) in fixed_location:
        last_location = fixed_location[(tag, 0)]
        return fixed_location[(tag, 0)]
    if last_location == (-1, -1):
        return (-1, -1)
    else:
        x = max(min(100, x), -100)
        y = max(min(100, y), -100)
        return (last_location[0] + x * 0.058 / 100, last_location[1] + y / 100 * 0.3)


def move_obj(data):  # 移动坐标
    x = int.from_bytes(data[16:18], byteorder='big', signed='false')
    y = int.from_bytes(data[18:20], byteorder='big', signed='false')
    tag = int.from_bytes(data[13:16], byteorder='big', signed='false')
    AgvAngle = int.from_bytes(data[20:22], byteorder='big', signed='false')
    # print(x, y, tag)
    newX, newY = calc(x, y, tag, AgvAngle)
    return (newX, newY)


def getAgvPos():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 定义socket类型，网络通信，TCP
        s.bind((HOST, PORT))  # 套接字绑定的IP与端口
        s.listen(5)  # 开始TCP监听,监听1个请求
    except Exception as e:
        print(e)

    while 1:
        try:
            conn, addr = s.accept()  # 接受TCP连接，并返回新的套接字与IP地址
            print('Connected by', addr)  # 输出客户端的IP地址
        except Exception as e:
            print(e)
        while 1:
            data = conn.recv(4096)  # 把接收的数据实例化
            if len(data) == 50:
                x, y = move_obj(data)
                agvPos = AgvPos.query.first()
                if not agvPos:
                    agvPos = AgvPos(x, y, 0)
                    agvPos.add()
                else:
                    agvPos.pos_X = x
                    agvPos.pos_Y = y
                    agvPos.update()
                agvRobot = RobotInfo.query.filter_by(type='agv').first()
                if agvRobot:
                    agvRobot.posX = x
                    agvRobot.posY = y
                    agvRobot.commit()

def getAgvData():
    t = threading.Thread(target=getAgvPos)
    t.start()
