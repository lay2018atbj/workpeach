# -*- coding: utf-8 -*-
from app import application, db
import socket
import threading
from datamodels import CollectedDatas
import time
import recordworktime  # 导入记录采集设备和机器人工作时间的模块
import deviceManager
import signalsPool


# 用于处理盒子信息的套接字
# 定义为一个回调函数 供多线程使用

def devRunSocket(NewDevice):
    id = NewDevice.id
    host = NewDevice.ip
    port = int(NewDevice.port)
    application.config['DEVICES'][id]['statusTimePoint'] = time.time()
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    application.config['DEVICES'][id]['scoket'] = sc
    try:
        application.config['DEVICES'][id]['status'] = 'connecting'
        sc.connect((host, port))
        application.config['DEVICES'][id]['status'] = 'normal'
    except:
        pass

    if application.config['DEVICES'][id]['status'] != 'normal':
        for try_times in range(1, 3):
            try:
                if id in application.config['DEVICES']:
                    application.config['DEVICES'][id]['status'] = 'reconnecting'
                    sc.connect((host, port))
                    application.config['DEVICES'][id]['status'] = 'normal'
                else:
                    print("Device{}已删除".format(id))
            except Exception as err:
                print('err:' + str(err))
                application.config['DEVICES'][id]['status'] = 'stop'
                print('Device{}连接异常 尝试重新连接{}次'.format(id, try_times))
                time.sleep(1)

    last_v = 0
    last_e = 0
    collected_num_thershold = 0
    while id in application.config['DEVICES']:
        if application.config['DEVICES'][id]['status'] != 'normal':  # 在运行时另一个同线程开始了 此处线程退出
            return
        try:
            data = sc.recv(8)
            e = (data[2] * 256 + data[3]) / 100  # 文档中电压与电流 与实际相反
            v = (data[0] * 256 + data[1]) / 100
            t = (data[4] * 256 + data[5]) / 100

            if (v != 0 or e != 0) and (last_v == 0 and last_e == 0):
                signalsPool.ROBOT_START.send(id, time=time.time())
            if (v == 0 or e == 0) and (last_v != 0 and last_e != 0):
                signalsPool.ROBOT_STOP.send(id, time=time.time())

            unique_id = application.config["DEVICES"][id]['uniqueid']
            produce_status = application.config['DEVICES'][id]['produce_status']
            robotId = application.config['DEVICES'][id]['robotId']
            productId = 0
            if 'productId' in application.config['DEVICES'][id]:
                productId = application.config['DEVICES'][id]['productId']

            last_v = v
            last_e = e
            collected_num_thershold += 1
            if collected_num_thershold >= 100:
                one = CollectedDatas(unique_id, productId, e, v, t, produce_status, robotId)
                one.save()
                collected_num_thershold = 0

        except socket.error:
            application.config['DEVICES'][id]['status'] = 'stop'
            time.sleep(3)
            print('Device{}连接异常 尝试重新连接'.format(id))
            application.config['DEVICES'][id]['status'] = 'reconnecting'
            try:
                application.config['DEVICES'][id]['scoket'].connect((host, port))
            except:
                print('Device{}连接异常 尝试重新连接'.format(id))
                application.config['DEVICES'][id]['status'] = 'stop'

        except Exception as err:
            print('err:' + str(err))


# 新建并启动一个采集数据的线程
def startCollectedThread(NewDevice):
    t = threading.Thread(target=devRunSocket, args=(NewDevice,))
    t.start()
    # 开启一个记录时间的线程
    t = threading.Thread(target=recordworktime.checkCollectorStatus, args=(NewDevice.id,))
    t.start()


'''
def doConnect(NewDevice):
    id = NewDevice.id
    host = NewDevice.ip
    port = NewDevice.port
    application.config['DEVICES'][id]['statusTimePoint'] = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect_status = 'connecting'
    application.config['DEVICES'][id]['status'] = connect_status
    application.config['DEVICES'][id]['scoket'] = sock

    for i in range(1, 4):  # 尝试连接3次
        try:
            sock.connect((host, port))
            connect_status = 'normal'
            application.config['DEVICES'][id]['status'] = connect_status
            break
        except Exception as e:
            if i == 3:
                connect_status = 'stop'
                application.config['DEVICES'][id]['status'] = connect_status
            else:
                connect_status = 'reconnecting'
                application.config['DEVICES'][id]['status'] = connect_status
                time.sleep(1)
            print('Device{}第{}次连接异常 , 异常原因:{}'.format(id, i, e))
            pass
    return sock, connect_status
'''
