# -*- coding: utf-8 -*-
from app import db, application, configParser
from utils import randomStr, encrypt, decrypt
from flask import escape
from flask import session, request
import json
import devsocket
from datetime import datetime

# User类 用于登录的模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(32), unique=True)
    password = db.Column(db.Binary(32), nullable=False)
    key = db.Column(db.String(32), nullable=False, unique=True)

    def __init__(self, username, password, email):
        self.key = randomStr(32)  # 32位随机字符 唯一标识用户
        self.username = str(username)
        self.email = email
        self.password = encrypt(password)

    # 登录函数 在数据库中验证
    @staticmethod
    def login(username, password):
        # 先查询用户名
        re = User.query.filter_by(username=username).first()
        # 没查到则查email
        if not re:
            re = User.query.filter_by(email=username).first()

        if re and re.isRight(password):
            session['username_key'] = re.key
            session['password'] = re.password
            session.permanent = True
            return True
        else:
            return False

    # 存入数据库
    def save(self):
        if self.validate():
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False

    # 验证用户输入是否正确
    def validate(self):
        return True

    def __repr__(self):
        return "Username: %s" % self.username

    # 参数password 明文或密文
    def isRight(self, password, isplain=True):
        if isplain:
            if decrypt(self.password) == password:
                return True
            else:
                return False
        else:
            if self.password == password:
                return True
            else:
                return False


# 用于处理本地主机配置的模型
class LocalHostConfig:
    def __init__(self, id, interval):
        self.id = id
        self.interval = interval

    @staticmethod
    def load(request):
        # 从表单中加载 失败则使用默认配置
        id = configParser.get("LocalHost", 'id')
        interval = configParser.get('LocalHost', 'interval')
        if 'localHostId' in request.form:
            id = request.form['localHostId']
        if 'localHostInterval' in request.form:
            interval = request.form['localHostInterval']
        return LocalHostConfig(id, interval)

    def save(self):
        configParser.set('LocalHost', 'id', self.id)
        configParser.set('LocalHost', 'interval', self.interval)
        with open('config.ini', 'w') as file:
            configParser.write(file)


# 用于处理远程主机配置的模型
class RemoteHostConfig:
    def __init__(self, url):
        self.url = url

    @staticmethod
    def load(request):
        url = configParser.get('RemoteHost', 'url')
        if 'remoteHostUrl' in request.form:
            url = request.form['remoteHostUrl']
        return RemoteHostConfig(url)

    def save(self):
        configParser.set('RemoteHost', 'url', self.url)
        with open('config.ini', 'w') as file:
            configParser.write(file)


# 用新增设备时提交的表单信息
class NewDevice:
    def __init__(self, desc, ip, port):
        self.desc = desc
        self.ip = ip
        self.port = port
        self.uniqueid = randomStr(16)  # 16位唯一标识符

    @staticmethod
    def load(request):
        desc = request.form['devDesc']
        ip = request.form['devIP']
        port = request.form['devPort']
        return NewDevice(desc, ip, port)

    def saveAndStart(self):
        devIDs = json.loads(configParser.get('Devices', 'devs'))
        if len(devIDs)==0:
            devIDs.append(1)
            cuID=1
        else:
            cuID = devIDs[-1] + 1
            devIDs.append(cuID)
        configParser.set('Devices', 'devs', json.dumps(devIDs))
        devSection = 'Device' + str(cuID)
        configParser.add_section(devSection)
        configParser.set(devSection, 'id', str(cuID))
        configParser.set(devSection, 'ip', self.ip)
        configParser.set(devSection, 'port', self.port)
        configParser.set(devSection, 'desc', self.desc)
        configParser.set(devSection, 'uniqueid', self.uniqueid)
        with open('config.ini', 'w') as file:
            configParser.write(file)
        info = {}
        info['desc'] = escape(self.desc)
        info['uniqueid'] = self.uniqueid
        application.config['DEVICES'][cuID] = info
        devsocket.startCollectedThread(cuID, self.ip, int(self.port))


#用于管理生产服务器的模型
class NewProduceServer(db.Model):
    __tablename__="produceservers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serverID = db.Column(db.String(80), unique=True,nullable=False)
    url = db.Column(db.String(320), unique=True)
    desc= db.Column(db.String(320), unique=False)

    def __init__(self,serverID,url,desc):
        self.url=url
        self.serverID=serverID
        self.desc=desc

    @staticmethod
    def getUrl(id):
        return NewProduceServer.query.filter_by(serverID=id).first().url

    @staticmethod
    def load(request):
        return NewProduceServer(serverID=request.form['serverID'],url=request.form['serverUrl'],desc=request.form['serverDesc'])

    def save(self):
        db.session.add(self)
        db.session.commit()

#消息日志 主要是服务器之间的通信
class MessageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flow_id = db.Column(db.String(16), unique=False)
    message_id = db.Column(db.String(16), unique=False)
    data = db.Column(db.String(100), unique=False)
    time = db.Column(db.DateTime, unique=False)


    def __init__(self,flow_id,message_id,data):
        self.flow_id = flow_id
        self.message_id = message_id
        self.time = datetime.now()
        self.data = data

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

#焊接工艺数据库

#工件id对应的工艺数据库 找到对应的方法后 到相应的方法表中查询具体的工艺参数
class WorkpieceInformation(db.Model):
	__tablename__ = 'workpiece_information'
	Workpiece_ID = db.Column(db.String(255), primary_key = True, nullable = False)
	Material = db.Column(db.String(255), primary_key = False, nullable = False)
	Material_brand = db.Column(db.String(255), primary_key = False, nullable = False)
	Shape = db.Column(db.String(255), primary_key = False, nullable = False)
	Thickness = db.Column(db.Float, primary_key = False, nullable = True)
	Diameter = db.Column(db.Float, primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	Image = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Workpiece_ID', 'Material', 'Material_brand', 'Shape', 'Thickness', 'Diameter', 'Remark', 'Image')
	def __getitem__(self,item):
		return getattr(self,item)


#相应的焊接方法表
class BrazeWeld(db.Model):
	__tablename__ = 'braze_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = True)
	Brazing_filler_model = db.Column(db.String(255), primary_key = False, nullable = False)
	Brazing_flux_model = db.Column(db.String(255), primary_key = False, nullable = True)
	Temperature = db.Column(db.Float, primary_key = False, nullable = False)
	Shield_gas_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Shield_gas_flow = db.Column(db.Float, primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Brazing_filler_model', 'Brazing_flux_model', 'Temperature', 'Shield_gas_type', 'Shield_gas_flow', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class DMeltingPolarArcWeld(db.Model):
	__tablename__ = 'd_melting_polar_arc_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_clearance = db.Column(db.Float, primary_key = False, nullable = True)
	Groove_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Groove_deep = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_position = db.Column(db.String(255), primary_key = False, nullable = False)
	Double_wire_position = db.Column(db.String(255), primary_key = False, nullable = True)
	Power_polarity = db.Column(db.String(255), primary_key = False, nullable = True)
	Current_F = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_speed_F = db.Column(db.Float, primary_key = False, nullable = True)
	Current_B = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_speed_B = db.Column(db.Float, primary_key = False, nullable = True)
	Voltage_F = db.Column(db.Float, primary_key = False, nullable = True)
	Voltage_B = db.Column(db.Float, primary_key = False, nullable = True)
	Arc_length = db.Column(db.Float, primary_key = False, nullable = True)
	Arc_length_correction = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Wire_material = db.Column(db.String(255), primary_key = False, nullable = False)
	Wire_model = db.Column(db.String(255), primary_key = False, nullable = False)
	Wire_diameter = db.Column(db.Float, primary_key = False, nullable = False)
	Wire_apical_extension_length = db.Column(db.Float, primary_key = False, nullable = False)
	Torch_angle = db.Column(db.String(255), primary_key = False, nullable = True)
	Weave_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Weave_range = db.Column(db.Float, primary_key = False, nullable = True)
	Weave_length = db.Column(db.Float, primary_key = False, nullable = True)
	Weave_frequency = db.Column(db.Float, primary_key = False, nullable = True)
	Shield_gas_type = db.Column(db.String(255), primary_key = False, nullable = False)
	Shield_gas_flow = db.Column(db.Float, primary_key = False, nullable = False)
	Gas_purity = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_peak_current = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_base_current = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_frequency = db.Column(db.Float, primary_key = False, nullable = True)
	Duty_cycle = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_machine = db.Column(db.String(255), primary_key = False, nullable = True)
	Robot = db.Column(db.String(255), primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Joint_clearance', 'Groove_type', 'Groove_deep', 'Weld_position', 'Double_wire_position', 'Power_polarity', 'Current_F', 'Wire_feed_speed_F', 'Current_B', 'Wire_feed_speed_B', 'Voltage_F', 'Voltage_B', 'Arc_length', 'Arc_length_correction', 'Weld_speed', 'Wire_material', 'Wire_model', 'Wire_diameter', 'Wire_apical_extension_length', 'Torch_angle', 'Weave_type', 'Weave_range', 'Weave_length', 'Weave_frequency', 'Shield_gas_type', 'Shield_gas_flow', 'Gas_purity', 'Pulse_peak_current', 'Pulse_base_current', 'Pulse_frequency', 'Duty_cycle', 'Weld_machine', 'Robot', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class ElectricResistanceWeld(db.Model):
	__tablename__ = 'electric_resistance_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = True)
	Current = db.Column(db.Float, primary_key = False, nullable = False)
	Weld_time = db.Column(db.Float, primary_key = False, nullable = False)
	Pressure = db.Column(db.Float, primary_key = False, nullable = False)
	Resistance_tip_diameter = db.Column(db.Float, primary_key = False, nullable = False)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Current', 'Weld_time', 'Pressure', 'Resistance_tip_diameter', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class FrictionStirWeld(db.Model):
	__tablename__ = 'friction_stir_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = False)
	Weld_position = db.Column(db.String(255), primary_key = False, nullable = False)
	Weld_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Spin_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Down_pressure_distance = db.Column(db.Float, primary_key = False, nullable = True)
	Down_pressure_num = db.Column(db.Float, primary_key = False, nullable = True)
	Back_tilt_angle = db.Column(db.String(255), primary_key = False, nullable = True)
	Stir_head_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Stir_needle_shape = db.Column(db.String(255), primary_key = False, nullable = True)
	Stir_needle_length = db.Column(db.Float, primary_key = False, nullable = True)
	Stir_needle_diameter = db.Column(db.Float, primary_key = False, nullable = True)
	Shaft_shoulder_shape = db.Column(db.String(255), primary_key = False, nullable = True)
	Shaft_shoulder_diameter = db.Column(db.Float, primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Weld_position', 'Weld_speed', 'Spin_speed', 'Down_pressure_distance', 'Down_pressure_num', 'Back_tilt_angle', 'Stir_head_type', 'Stir_needle_shape', 'Stir_needle_length', 'Stir_needle_diameter', 'Shaft_shoulder_shape', 'Shaft_shoulder_diameter', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class FrictionStudWeld(db.Model):
	__tablename__ = 'friction_stud_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Weld_type = db.Column(db.String(255), primary_key = False, nullable = False)
	Spin_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Friction_pressure = db.Column(db.Float, primary_key = False, nullable = False)
	Friction_time = db.Column(db.Float, primary_key = False, nullable = False)
	Upsetting_force = db.Column(db.Float, primary_key = False, nullable = False)
	Upsetting_time = db.Column(db.Float, primary_key = False, nullable = False)
	Axial_feed_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Weld_type', 'Spin_speed', 'Friction_pressure', 'Friction_time', 'Upsetting_force', 'Upsetting_time', 'Axial_feed_speed', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class LaserBeamWeld(db.Model):
	__tablename__ = 'laser_beam_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_clearance = db.Column(db.Float, primary_key = False, nullable = True)
	Groove_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Groove_deep = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_position = db.Column(db.String(255), primary_key = False, nullable = False)
	Laser_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Defocusing_amount = db.Column(db.Float, primary_key = False, nullable = False)
	Weld_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Laser_power = db.Column(db.Float, primary_key = False, nullable = False)
	Laser_frequency = db.Column(db.Float, primary_key = False, nullable = True)
	Laser_tilt_type = db.Column(db.String(255), primary_key = False, nullable = False)
	Laser_tilt_angle = db.Column(db.String(255), primary_key = False, nullable = False)
	Laser_beam_position = db.Column(db.String(255), primary_key = False, nullable = True)
	Laser_wire_distance = db.Column(db.Float, primary_key = False, nullable = True)
	Arc_current = db.Column(db.Float, primary_key = False, nullable = True)
	Arc_voltage = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_speed = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_material = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_model = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_diameter = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_feed_angle = db.Column(db.String(255), primary_key = False, nullable = True)
	Shield_gas_type = db.Column(db.String(255), primary_key = False, nullable = False)
	Shield_gas_flow = db.Column(db.Float, primary_key = False, nullable = False)
	Robot = db.Column(db.String(255), primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Joint_clearance', 'Groove_type', 'Groove_deep', 'Weld_position', 'Laser_type', 'Defocusing_amount', 'Weld_speed', 'Laser_power', 'Laser_frequency', 'Laser_tilt_type', 'Laser_tilt_angle', 'Laser_beam_position', 'Laser_wire_distance', 'Arc_current', 'Arc_voltage', 'Wire_feed_speed', 'Wire_material', 'Wire_model', 'Wire_diameter', 'Wire_feed_type', 'Wire_feed_angle', 'Shield_gas_type', 'Shield_gas_flow', 'Robot', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class ManualWeldingRodWeld(db.Model):
	__tablename__ = 'manual_welding_rod_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_clearance = db.Column(db.Float, primary_key = False, nullable = True)
	Groove_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Groove_deep = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_position = db.Column(db.String(255), primary_key = False, nullable = False)
	Welding_rod_type = db.Column(db.String(255), primary_key = False, nullable = False)
	Welding_rod_material = db.Column(db.String(255), primary_key = False, nullable = True)
	Welding_rod_model = db.Column(db.String(255), primary_key = False, nullable = True)
	Welding_rod_diameter = db.Column(db.Float, primary_key = False, nullable = False)
	Power_polarity = db.Column(db.String(255), primary_key = False, nullable = True)
	Current = db.Column(db.Float, primary_key = False, nullable = False)
	Voltage = db.Column(db.Float, primary_key = False, nullable = False)
	Arc_length = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Torch_angle = db.Column(db.String(255), primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Joint_clearance', 'Groove_type', 'Groove_deep', 'Weld_position', 'Welding_rod_type', 'Welding_rod_material', 'Welding_rod_model', 'Welding_rod_diameter', 'Power_polarity', 'Current', 'Voltage', 'Arc_length', 'Weld_speed', 'Torch_angle', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class MeltingPolarArcWeld(db.Model):
	__tablename__ = 'melting_polar_arc_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_clearance = db.Column(db.Float, primary_key = False, nullable = True)
	Groove_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Groove_deep = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_position = db.Column(db.String(255), primary_key = False, nullable = False)
	Power_polarity = db.Column(db.String(255), primary_key = False, nullable = True)
	Current = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Voltage = db.Column(db.Float, primary_key = False, nullable = False)
	Arc_length = db.Column(db.Float, primary_key = False, nullable = True)
	Arc_length_correction = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Wire_material = db.Column(db.String(255), primary_key = False, nullable = False)
	Wire_model = db.Column(db.String(255), primary_key = False, nullable = False)
	Wire_diameter = db.Column(db.Float, primary_key = False, nullable = False)
	Wire_apical_extension_length = db.Column(db.Float, primary_key = False, nullable = False)
	Torch_angle = db.Column(db.String(255), primary_key = False, nullable = True)
	Weave_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Weave_range = db.Column(db.Float, primary_key = False, nullable = True)
	Weave_length = db.Column(db.Float, primary_key = False, nullable = True)
	Weave_frequency = db.Column(db.Float, primary_key = False, nullable = True)
	Shield_gas_type = db.Column(db.String(255), primary_key = False, nullable = False)
	Shield_gas_flow = db.Column(db.Float, primary_key = False, nullable = False)
	Gas_purity = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_peak_current = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_base_current = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_frequency = db.Column(db.Float, primary_key = False, nullable = True)
	Duty_cycle = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_machine = db.Column(db.String(255), primary_key = False, nullable = True)
	Robot = db.Column(db.String(255), primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Joint_clearance', 'Groove_type', 'Groove_deep', 'Weld_position', 'Power_polarity', 'Current', 'Wire_feed_speed', 'Voltage', 'Arc_length', 'Arc_length_correction', 'Weld_speed', 'Wire_material', 'Wire_model', 'Wire_diameter', 'Wire_apical_extension_length', 'Torch_angle', 'Weave_type', 'Weave_range', 'Weave_length', 'Weave_frequency', 'Shield_gas_type', 'Shield_gas_flow', 'Gas_purity', 'Pulse_peak_current', 'Pulse_base_current', 'Pulse_frequency', 'Duty_cycle', 'Weld_machine', 'Robot', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class NonMeltingPolarArcWeld(db.Model):
	__tablename__ = 'non_melting_polar_arc_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_clearance = db.Column(db.Float, primary_key = False, nullable = True)
	Groove_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Groove_deep = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_position = db.Column(db.String(255), primary_key = False, nullable = False)
	Power_polarity = db.Column(db.String(255), primary_key = False, nullable = True)
	Current = db.Column(db.Float, primary_key = False, nullable = False)
	Weld_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Voltage = db.Column(db.Float, primary_key = False, nullable = False)
	Arc_length = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_speed = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_material = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_model = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_diameter = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_angle = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_feed_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Weave_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Weave_range = db.Column(db.Float, primary_key = False, nullable = True)
	Weave_length = db.Column(db.Float, primary_key = False, nullable = True)
	Weave_frequency = db.Column(db.Float, primary_key = False, nullable = True)
	Shield_gas_type = db.Column(db.String(255), primary_key = False, nullable = False)
	Shield_gas_flow = db.Column(db.Float, primary_key = False, nullable = False)
	Plasma_gas_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Plasma_gas_flow = db.Column(db.Float, primary_key = False, nullable = True)
	Gas_purity = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_peak_current = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_base_current = db.Column(db.Float, primary_key = False, nullable = True)
	Pulse_frequency = db.Column(db.Float, primary_key = False, nullable = True)
	Duty_cycle = db.Column(db.Float, primary_key = False, nullable = True)
	Tungsten_electrode_diameter = db.Column(db.Float, primary_key = False, nullable = False)
	Tungsten_electrode_top_angle = db.Column(db.String(255), primary_key = False, nullable = True)
	Tungsten_electrode_neck_in = db.Column(db.Float, primary_key = False, nullable = True)
	Plasma_nozzle_diameter = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_machine = db.Column(db.String(255), primary_key = False, nullable = True)
	Robot = db.Column(db.String(255), primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Joint_clearance', 'Groove_type', 'Groove_deep', 'Weld_position', 'Power_polarity', 'Current', 'Weld_speed', 'Voltage', 'Arc_length', 'Wire_feed_speed', 'Wire_material', 'Wire_model', 'Wire_diameter', 'Wire_feed_angle', 'Wire_feed_type', 'Weave_type', 'Weave_range', 'Weave_length', 'Weave_frequency', 'Shield_gas_type', 'Shield_gas_flow', 'Plasma_gas_type', 'Plasma_gas_flow', 'Gas_purity', 'Pulse_peak_current', 'Pulse_base_current', 'Pulse_frequency', 'Duty_cycle', 'Tungsten_electrode_diameter', 'Tungsten_electrode_top_angle', 'Tungsten_electrode_neck_in', 'Plasma_nozzle_diameter', 'Weld_machine', 'Robot', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class RobotAttitude(db.Model):
	__tablename__ = 'robot_attitude'
	Work_ID = db.Column(db.String(255), primary_key = True, nullable = False)
	h = db.Column(db.Float, primary_key = False, nullable = False)
	X = db.Column(db.Float, primary_key = False, nullable = False)
	Y = db.Column(db.Float, primary_key = False, nullable = False)
	Z = db.Column(db.Float, primary_key = False, nullable = False)
	X1 = db.Column(db.Float, primary_key = False, nullable = False)
	Y1 = db.Column(db.Float, primary_key = False, nullable = False)
	Z1 = db.Column(db.Float, primary_key = False, nullable = False)
	xx = db.Column(db.Float, primary_key = False, nullable = False)
	yy = db.Column(db.Float, primary_key = False, nullable = False)
	zz = db.Column(db.Float, primary_key = False, nullable = False)
	xx1 = db.Column(db.Float, primary_key = False, nullable = False)
	yy1 = db.Column(db.Float, primary_key = False, nullable = False)
	zz1 = db.Column(db.Float, primary_key = False, nullable = False)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Work_ID', 'h', 'X', 'Y', 'Z', 'X1', 'Y1', 'Z1', 'xx', 'yy', 'zz', 'xx1', 'yy1', 'zz1', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class SubmergeArcWeld(db.Model):
	__tablename__ = 'submerge_arc_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_clearance = db.Column(db.Float, primary_key = False, nullable = True)
	Groove_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Groove_deep = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_position = db.Column(db.String(255), primary_key = False, nullable = False)
	Weld_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Power_polarity = db.Column(db.String(255), primary_key = False, nullable = True)
	Current = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_speed = db.Column(db.Float, primary_key = False, nullable = True)
	Voltage = db.Column(db.Float, primary_key = False, nullable = False)
	Flux_material = db.Column(db.String(255), primary_key = False, nullable = False)
	Flux_model = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_material = db.Column(db.String(255), primary_key = False, nullable = False)
	Wire_model = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_diameter = db.Column(db.Float, primary_key = False, nullable = False)
	Wire_feed_angle = db.Column(db.String(0), primary_key = False, nullable = True)
	Remark = db.Column(db.String(255), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Joint_clearance', 'Groove_type', 'Groove_deep', 'Weld_position', 'Weld_speed', 'Power_polarity', 'Current', 'Wire_feed_speed', 'Voltage', 'Flux_material', 'Flux_model', 'Wire_material', 'Wire_model', 'Wire_diameter', 'Wire_feed_angle', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)

class VacuumElectronBeamWeld(db.Model):
	__tablename__ = 'vacuum_electron_beam_weld'
	Weld_method = db.Column(db.String(255), primary_key = True, nullable = False)
	Workpiece_ID_A = db.Column(db.String(255), primary_key = False, nullable = False)
	Workpiece_ID_B = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_form = db.Column(db.String(255), primary_key = False, nullable = False)
	Joint_clearance = db.Column(db.Float, primary_key = False, nullable = True)
	Groove_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Groove_deep = db.Column(db.Float, primary_key = False, nullable = True)
	Weld_position = db.Column(db.String(255), primary_key = False, nullable = False)
	Weld_speed = db.Column(db.Float, primary_key = False, nullable = False)
	Acceleration_voltage = db.Column(db.Float, primary_key = False, nullable = False)
	Electron_beam_flow = db.Column(db.Float, primary_key = False, nullable = False)
	Focusing_curren = db.Column(db.Float, primary_key = False, nullable = False)
	Work_distance = db.Column(db.Float, primary_key = False, nullable = False)
	Vacuum_degree = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_speed = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_material = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_model = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_diameter = db.Column(db.Float, primary_key = False, nullable = True)
	Wire_feed_type = db.Column(db.String(255), primary_key = False, nullable = True)
	Wire_feed_angle = db.Column(db.Float, primary_key = False, nullable = True)
	Remark = db.Column(db.String(0), primary_key = False, nullable = True)
	def keys(self):
		return ('Weld_method', 'Workpiece_ID_A', 'Workpiece_ID_B', 'Joint_form', 'Joint_clearance', 'Groove_type', 'Groove_deep', 'Weld_position', 'Weld_speed', 'Acceleration_voltage', 'Electron_beam_flow', 'Focusing_curren', 'Work_distance', 'Vacuum_degree', 'Wire_feed_speed', 'Wire_material', 'Wire_model', 'Wire_diameter', 'Wire_feed_type', 'Wire_feed_angle', 'Remark')
	def __getitem__(self,item):
		return getattr(self,item)
