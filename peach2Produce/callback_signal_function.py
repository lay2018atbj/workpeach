import signalsPool
from app import db, application
from models import RobotRunInfo, ProductControlInfo, TechniqueInfo, DeviceInfo
import threading


def signals_robot_start_callback(sender, *args, **kwargs):
    application.config['DEVICES'][sender]['produce_status'] = 'working'
    print(threading.current_thread().name + ':start')


def signals_robot_stop_callback(sender, *args, **kwargs):
    application.config['DEVICES'][sender]['produce_status'] = 'stop'
    print(threading.current_thread().name + ':stop')


def signals_product_begin_callback(product_id, *args, **kwargs):
    product = ProductControlInfo.query.filter_by(productId=product_id).first()
    techId = product.techId
    techniqueInfos = TechniqueInfo.query.filter_by(techniqueId=techId).all()
    for technique in techniqueInfos:
        tech_robot_id = technique.robotId
        print(tech_robot_id)
        tech_device = DeviceInfo.query.filter_by(robotId=tech_robot_id).first()
        tech_device_id = -1
        if tech_device:
            tech_device_id = tech_device.id
        else:
            print(tech_robot_id + ":not found")
        tech_electricity = technique.electricity
        tech_voltage = technique.voltage
        tech_temperature = technique.temperature
        for device_id in application.config['DEVICES']:
            if device_id == int(tech_device_id):
                application.config['DEVICES'][device_id]['productId'] = product.productId
                application.config['DEVICES'][device_id]['techniqueId'] = technique.techniqueId
                application.config['DEVICES'][device_id]['electricity'] = tech_electricity
                application.config['DEVICES'][device_id]['voltage'] = tech_voltage
                application.config['DEVICES'][device_id]['temperature'] = tech_temperature
                application.config['DEVICES'][device_id]['V_THRESHILD_MIN'] = tech_voltage * 0.8
                application.config['DEVICES'][device_id]['V_THRESHILD_MAX'] = tech_voltage * 1.2
                application.config['DEVICES'][device_id]['I_THRESHILD_MIN'] = tech_electricity * 0.8
                application.config['DEVICES'][device_id]['I_THRESHILD_MAX'] = tech_electricity * 1.2


def signals_product_finish_callback(product_id, *args, **kwargs):
    print(product_id + 'finnished')
    for device_id in application.config['DEVICES']:
        application.config['DEVICES'][device_id]['produce_status'] = 'stop'


# 机器人
signalsPool.ROBOT_START.connect(signals_robot_start_callback)
signalsPool.ROBOT_STOP.connect(signals_robot_stop_callback)

# 产品生产
signalsPool.PRODUCT_BEGIN.connect(signals_product_begin_callback)
signalsPool.PRODUCT_FINISHED.connect(signals_product_finish_callback)
