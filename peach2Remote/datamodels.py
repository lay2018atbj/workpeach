# -*- coding: utf-8 -*-
from app import db
from sqlalchemy import Table, MetaData, Column, Integer, String,Float
import datetime
# 用于管理采集到的数据的模型
class CollectedDatas(db.Model):
    __tablename__ = 'tempData'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    electricity = db.Column(db.Float, unique=False)
    voltage = db.Column(db.Float, unique=False)
    temperature = db.Column(db.Float,unique=False)
    workpieceid = db.Column(db.Integer, unique=False)
    devid=db.Column(db.String(16), unique=False)
    time = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())

    def __init__(self,devid,workpieceid,electricity, voltage, temperature):
        self.electricity = electricity
        self.voltage = voltage
        self.temperature = temperature
        self.workpieceid=workpieceid
        self.devid=devid

    @staticmethod
    def create(tablename):
        table=Table(tablename, db.metadata,
              Column('id', Integer, primary_key=True, autoincrement=True),
              Column('workpieceid', db.Integer,unique=False),
              Column('electricity', db.Float, unique=False),
              Column('voltage',db.Float, unique=False),
              Column('temperature',db.Float, unique=False))
        db.create_all()

    def save(self):
        db.session.add(self)
        db.session.commit()