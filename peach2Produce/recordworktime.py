# -*- coding: utf-8 -*-
from app import application, db
from datamodels import DevicesRunInfo, CollectedDatas
import time
from sqlalchemy import and_
import datetime


def checkCollectorStatus(id):
    re = DevicesRunInfo.query.filter(and_(DevicesRunInfo.date == time.strftime('%Y-%m-%d'),
                                          DevicesRunInfo.devId == application.config['DEVICES'][id][
                                              'uniqueid'])).first()
    if not re:
        re = DevicesRunInfo(application.config['DEVICES'][id]['uniqueid'], 0, 0, 0, 0, 0)
        db.session.add(re)
        db.session.commit()
    lasttime = time.time()
    work_status = 'stop'
    application.config['DEVICES'][id]['produce_status'] = work_status
    max_v = 10000
    min_v = 0
    max_i = 10000
    min_i = 0
    if id in application.config['DEVICES'] and 'V_THRESHILD_MAX' in application.config['DEVICES'][id]:
        max_v = application.config['DEVICES'][id]['V_THRESHILD_MAX']
        min_v = application.config['DEVICES'][id]['V_THRESHILD_MAX']
        max_i = application.config['DEVICES'][id]['I_THRESHILD_MAX']
        min_i = application.config['DEVICES'][id]['I_THRESHILD_MAX']
    while True:
        if id in application.config['DEVICES']:  # 设备没有被删除
            # re = DevicesInfo.query.filter(and_(DevicesInfo.date == time.strftime('%Y-%m-%d'),DevicesInfo.devId == application.config['DEVICES'][id]['uniqueid'])).first()
            if application.config['DEVICES'][id]['status'] == 'normal':
                re.collectorNormalTime += (time.time() - lasttime)
                data = CollectedDatas.query.filter_by(dev_uniqueId=application.config['DEVICES'][id]['uniqueid']).first()
                # if (datetime.datetime.now()-data.time).seconds >2: #两秒的容差
                if application.config['DEVICES'][id]['produce_status'] == 'working' and data:
                    if data.voltage == 0:
                        re.robotRestTime += (time.time() - lasttime)
                    elif data.voltage >= min_v and data.voltage <= max_v and data.electricity >= min_i and data.electricity <= max_i:
                        work_status = 'normal'
                        application.config['DEVICES'][id]['produce_status'] = work_status
                        re.robotWorkTime += (time.time() - lasttime)
                    else:
                        re.robotExceptionTime += (time.time() - lasttime)
                        work_status = 'abnormal'
                        application.config['DEVICES'][id]['produce_status'] = work_status
                else:
                    re.robotRestTime += (time.time() - lasttime)
            elif application.config['DEVICES'][id]['status'] == 'stop' \
                    or application.config['DEVICES'][id]['status'] == 'reconnecting' \
                    or application.config['DEVICES'][id]['status'] == 'connecting':
                re.collectorStopTime += (time.time() - lasttime)

            # db.session.update(re)
            db.session.commit()
            lasttime = time.time()
            time.sleep(0.5)
        else:
            return
