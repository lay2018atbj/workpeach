from app import db, application
from utils import randomStr, encrypt, decrypt
from sqlalchemy import and_, desc, func
from models import DeviceInfo


# 用新增设备时提交的表单信息
class NewDevice:
    def __init__(self, name, ip, port, robotId):
        self.name = name
        self.ip = ip
        self.port = port
        self.robotId = robotId
        dev = DeviceInfo.query.filter(
            and_(DeviceInfo.ip == self.ip, DeviceInfo.port == int(self.port))).first()
        if not dev:
            self.uniqueid = randomStr(16)  # 16位唯一标识符  ##会不会重复，需注意
        else:
            self.uniqueid = dev.uniqueid

    @staticmethod
    def load(request):
        name = request.form['devDesc']
        ip = request.form['devIP']
        port = request.form['devPort']
        robotId = request.form['robotId']
        return NewDevice(name, ip, port, robotId)

    def save(self):

        dev = DeviceInfo.query.filter(
            and_(DeviceInfo.ip == self.ip, DeviceInfo.port == int(self.port))).first()

        if not dev:
            dev = DeviceInfo(self.uniqueid, self.ip, int(self.port), 'collect', self.name, self.robotId, 'init')
            dev.save()
        else:
            dev.name = self.name
            dev.status = 'init'
            dev.robotId = self.robotId
            dev.commit()

        info = dict()
        info['id'] = dev.id
        info['uniqueid'] = dev.uniqueid
        info['ip'] = dev.ip
        info['port'] = dev.port
        info['type'] = dev.type
        info['route'] = dev.route
        info['name'] = dev.name
        info['robotId'] = dev.robotId
        info['status'] = dev.status
        info['produce_status'] = 'stop'
        info['V_THRESHILD_MIN'] = 11
        info['V_THRESHILD_MAX'] = 15
        info['I_THRESHILD_MIN'] = 110
        info['I_THRESHILD_MAX'] = 150
        application.config['DEVICES'][dev.id] = info
        self.id = dev.id
        return dev.id
