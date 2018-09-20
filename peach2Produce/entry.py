# -*- coding: utf-8 -*-

# 入口运行模块

# 导入各模块（即控制器，配置）
from app import application
import index  # 导入index控制器
import user  # 导入user控制器
import ma_index  # 导入manage后台的index控制器
import ma_config  # 导入配置 控制器
import ma_workshop  # 导入车间 控制器
import ma_produceinfo  # 导入生产信息控制器
import ma_producreport  # 导入生产报表控制器
import ma_workshop_overall  # 全局视图
import ma_manufacture  # 生产产品
import verify  # 导入验证模块 主要是请求的权限验证
import agv
import callback_signal_function
################################基础内容全部加载完毕################################

# 初始化配置
import json
from app import configParser, db
import devsocket
from flask import escape
from models import DeviceInfo

# 创建所有需要的表(存在则不会创建)
db.create_all()

# 读取远程主机url和本机标识符
configParser.read('config.ini')
application.config['REMOTEURL'] = configParser.get('RemoteHost', 'url')
application.config['LOCALID'] = configParser.get('LocalHost', 'id')
application.config['INTERVAL'] = configParser.get('LocalHost', 'interval')

# 从数据库中加载配置信息
devs = DeviceInfo.query.all()
for device in devs:
    if device.status != 'delete':
        device_id = device.id
        info = dict()
        info['id'] = device.id
        info['uniqueid'] = device.uniqueid
        info['ip'] = device.ip
        info['port'] = device.port
        info['type'] = device.type
        info['route'] = device.route
        info['name'] = device.name
        info['robotId'] = device.robotId
        info['status'] = device.status
        info['produce_status'] = 'stop'
        info['V_THRESHILD_MIN'] = 11
        info['V_THRESHILD_MAX'] = 15
        info['I_THRESHILD_MIN'] = 110
        info['I_THRESHILD_MAX'] = 150
        application.config['DEVICES'][device_id] = info
        devsocket.startCollectedThread(device)

# 添加用户
if not user.User.query.first():
    u = user.User('admin', '123456', '123456@qq.com')
    db.session.add(u)
    db.session.commit()

import count_statistics  # 导入定期统计模块

if __name__ == '__main__':
    agv.getAgvData()
    application.run(host=application.config['HOST'], port=application.config['PORT'], use_reloader=False)
