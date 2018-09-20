# -*- coding: utf-8 -*-
from app import db
from sqlalchemy import Table, MetaData, Column, Integer, String, Float, desc, func
import datetime
import time


# 用于管理采集到的数据的模型
class CollectedDatas(db.Model):
    __mapper_args__ = {
        "order_by": desc('time')
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    electricity = db.Column(db.Float, unique=False)
    voltage = db.Column(db.Float, unique=False)
    temperature = db.Column(db.Float, unique=False)
    productId = db.Column(db.Integer, unique=False)
    dev_uniqueId = db.Column(db.String(16), unique=False)
    time = db.Column(db.DateTime, unique=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    produce_status = db.Column(db.String(16), unique=False)
    robotId = db.Column(db.String(16), unique=False)

    def __init__(self, dev_uniqueId, productId, electricity, voltage, temperature, produce_status, robotId):
        self.electricity = electricity
        self.voltage = voltage
        self.temperature = temperature
        self.productId = productId
        self.dev_uniqueId = dev_uniqueId
        self.time = datetime.datetime.now()
        self.produce_status = produce_status
        self.robotId = robotId

    def save(self):
        db.session.add(self)
        db.session.commit()


# 序列化函数将数据对象可json导出
def CollectedDataSeria(obj):
    return {
        'time': obj.time.strftime('%Y/%m/%d %H:%M:%S'),
        'e': obj.electricity,
        'v': obj.voltage,
        't': obj.temperature,
        'productId': obj.productId,
        'produce_status': obj.produce_status,
        'robotId': obj.robotId
    }


# 设备表 用于储存累计时间 开关机时间  秒为单位
class DevicesRunInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    devId = db.Column(db.String(16), unique=False)
    collectorNormalTime = db.Column(db.Float)
    collectorStopTime = db.Column(db.Float)
    robotWorkTime = db.Column(db.Float)
    robotRestTime = db.Column(db.Float)
    robotExceptionTime = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False)
    endTime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, devId, collectorNormalTime, collectorStopTime, robotWorkTime, robotRestTime, robotExceptionTime):
        self.devId = devId
        self.collectorNormalTime = collectorNormalTime
        self.collectorStopTime = collectorStopTime
        self.robotWorkTime = robotWorkTime
        self.robotRestTime = robotRestTime
        self.robotExceptionTime = robotExceptionTime
        self.date = time.strftime('%Y-%m-%d')


class CollectedAgvDatas(db.Model):
    __mapper_args__ = {
        "order_by": desc('id')
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    x = db.Column(db.Float, unique=False)
    y = db.Column(db.Float, unique=False)
    z = db.Column(db.Float, unique=False)

    def __init__(self, id, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def save(self):
        db.session.add(self)
        db.session.commit()
