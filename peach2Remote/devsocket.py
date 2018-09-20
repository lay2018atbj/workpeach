# -*- coding: utf-8 -*-
from app import application,db
import socket
import threading
from datamodels import CollectedDatas
from sqlalchemy.orm import mapper
import time

#用于处理盒子信息的套接字
#定义为一个回调函数 供多线程使用

def devRunSocket(id,host,port):
    sc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #application.config['DEVICES'][id]={}
    for i in range(1,4):
        try:
            if id in application.config['DEVICES']:
                if i != 1:
                    application.config['DEVICES'][id]['status'] = 'reconnecting'
                else:
                    application.config['DEVICES'][id]['status'] = 'connecting'
                sc.connect((host, port))
                application.config['DEVICES'][id]['status'] = 'normal'
                while id in application.config['DEVICES']:
                    data = sc.recv(8)
                    #插入数据库
                    one=CollectedDatas(application.config["DEVICES"][id]['uniqueid'],0,0,0,0)
                    one.save()
            else:
                print("Device{}已删除".format(id))
        except Exception:
            application.config['DEVICES'][id]['status']='stop'
            print('Device{}连接异常 尝试重新连接{}次'.format(id,i))
            
#新建并启动一个采集数据的线程
def startCollectedThread(id,host,port):
    t=threading.Thread(target=devRunSocket,args=(id,host,port))
    t.start()
