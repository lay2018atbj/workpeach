# -*- coding: utf-8 -*-
from app import db,application
import threading
from models import StatisticalProduceDatas,ProductControlInfo,StatisticalWorkTimeDatas,DeviceInfo,Cost
from datamodels import CollectedDatas
from datetime import datetime,timedelta,date
from sqlalchemy import func,and_
import signalsPool

import time

#定期根据原始采集数据原始生产信息数据等 更新统计数据表
def countTheStatistics():
    lastData={}
    for id,info in application.config['DEVICES'].items():
        lastData[id]={}
        lastData[id]['lastcd']= CollectedDatas.query.filter_by(dev_uniqueId=info['uniqueid']).first()
        lastData[id]['timer'] = time.time()

    while True:
        todayCost = Cost.query.filter_by(date=date.today()).first()
        if not todayCost:
            todayCost = Cost(0, 0, 0)
            todayCost.add()
        for id, info in application.config['DEVICES'].items():
            # 统计成本消耗    每个设备都要统计 由于所有设备的采集数据全部放在同一张表里所以要对devid限制
            cd = CollectedDatas.query.filter_by(dev_uniqueId=info['uniqueid']).first()
            if lastData[id]['lastcd'] and lastData[id]['lastcd'].electricity != 0 and lastData[id]['lastcd'].voltage != 0:
                seconds = time.time() - lastData[id]['timer']
                todayCost.power_consumption += ((((cd.electricity + lastData[id]['lastcd'].electricity) / 2) * (
                            (cd.voltage + lastData[id]['lastcd'].voltage) / 2)) / 1000 * (seconds / 3600))
                todayCost.air_consumption += (application.config['AIRCONSUM'] * (seconds / 60))
                todayCost.welding_wire_consumption += (application.config['WELDINGWIRECONSUM'] * (seconds / 60))*1000
                todayCost.update()
            lastData[id]['lastcd'] = CollectedDatas.query.filter_by(dev_uniqueId=info['uniqueid']).first()
            lastData[id]['timer'] = time.time()

        #先统计产品信息
        info = ProductControlInfo.query.first()
        #devIds=list(set(db.session.query(DevicesInfo.devId).all()))
        devIds=DeviceInfo.query.filter(DeviceInfo.status=='normal').all()
        if info:
            startTime = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')  # 去除具体的小时分秒
            delta = timedelta(days=1)
            query = ProductControlInfo.query.filter(ProductControlInfo.beginTime.between(startTime, startTime + delta))
            finiworks = len(query.filter(ProductControlInfo.status == 'FINISHED').all())
            cancelworks = len(query.filter(ProductControlInfo.status == 'CANCELED').all())
            procqulified = len(query.filter(ProductControlInfo.processEval == 'QUALIFIED').all())
            procunqulified = len(query.filter(ProductControlInfo.processEval == 'UNQUALIFIED').all())
            requlified = len(query.filter(ProductControlInfo.resultEval == 'QUALIFIED').all())
            reunqulified = len(query.filter(ProductControlInfo.resultEval == 'UNQUALIFIED').all())
            re=StatisticalProduceDatas.query.filter(StatisticalProduceDatas.date==startTime).first()
            if not re:
                db.session.add(StatisticalProduceDatas(startTime, finiworks, cancelworks,procqulified, procunqulified, requlified, reunqulified))
            else:
                re.date=startTime
                re.finiwork = finiworks
                re.cancelwork = cancelworks
                re.procqulified = procqulified
                re.procunqulified = procunqulified
                re.requlified = requlified
                re.reunqulified = reunqulified
            db.session.commit()

        for dev in devIds:  # 获取存在的devId
            devId = dev.uniqueid
            query = db.session.query
            collectorTotalNormTime, = query(func.sum(DevicesRunInfo.collectorNormalTime)).filter(
                DevicesRunInfo.devId == devId).first()
            collectorTotalStopTime, = query(func.sum(DevicesRunInfo.collectorStopTime)).filter(
                DevicesRunInfo.devId == devId).first()
            robotTotalWorkTime, = query(func.sum(DevicesRunInfo.robotWorkTime)).filter(DevicesRunInfo.devId == devId).first()
            robotTotalRestTime, = query(func.sum(DevicesRunInfo.robotRestTime)).filter(DevicesRunInfo.devId == devId).first()
            robotTotalExceptionTime, = query(func.sum(DevicesRunInfo.robotExceptionTime)).filter(
                DevicesRunInfo.devId == devId).first()
            re = StatisticalWorkTimeDatas.query.filter(StatisticalWorkTimeDatas.devId == devId).first()
            if not re:
                db.session.add(
                    StatisticalWorkTimeDatas(devId, collectorTotalNormTime, collectorTotalStopTime, robotTotalWorkTime,
                                             robotTotalRestTime, robotTotalExceptionTime))
            else:
                re.collectorTotalNormTime = collectorTotalNormTime
                re.collectorTotalStopTime = collectorTotalStopTime
                re.robotTotalWorkTime = robotTotalWorkTime
                re.robotTotalRestTime = robotTotalRestTime
                re.robotTotalExceptionTime = robotTotalExceptionTime
            db.session.commit()

        time.sleep(60)#1min统计一次


t=threading.Thread(target=countTheStatistics)
t.start()