# -*- coding: utf-8 -*-
from app import db, application, configParser
from utils import randomStr, encrypt, decrypt
from flask import escape
from flask import session, request
from sqlalchemy import and_, desc, func
import json

import time
import datetime
import json
from datamodels import DevicesRunInfo


# User类 用于登录的模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(320), unique=True)
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


# 用于生产信息查询form的模型
class SearchInfoForm:
    def __init__(self, productId, techId, status, processEval, resultEval):
        self.productId = productId
        self.status = status
        self.processEval = processEval
        self.resultEval = resultEval
        self.techId = techId

    @staticmethod
    def load(request):
        if 'productId' in request.form:
            return SearchInfoForm(request.form['productId'],
                                  request.form['techId'],
                                  request.form['status'],
                                  request.form['processEval'],
                                  request.form['resultEval'])
        else:
            return SearchInfoForm('',
                                  '',
                                  '',
                                  '',
                                  '',
                                  )

    def getSearchResults(self):
        return ProductControlInfo.search(self)


# 用于生产信息查询form的模型
class SearchTechniqueInfoForm:
    def __init__(self, productKind, robotId, techniqueId):
        self.productKind = productKind
        self.robotId = robotId  # config里的临时id
        self.techniqueId = techniqueId

    @staticmethod
    def load(request):
        if 'productKind' in request.form:
            return SearchTechniqueInfoForm(request.form['productKind'] if request.form['productKind'] else '',
                                           request.form['robotId'] if request.form['robotId'] else '',
                                           request.form['techniqueId'] if request.form['techniqueId'] else '',
                                           )
        else:
            return SearchTechniqueInfoForm('',
                                           '',
                                           ''
                                           )

    def getSearchResults(self):
        return TechniqueInfo.search(self)


# 生产产品生产模型
class ProductControlInfo(db.Model):
    __mapper_args__ = {
        "order_by": desc('beginTime')
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productId = db.Column(db.String(32), unique=False, nullable=False)
    techId = db.Column(db.String(32), unique=False, nullable=False)
    status = db.Column(db.String(32), nullable=False)
    processEval = db.Column(db.String(32), nullable=False, unique=False)
    resultEval = db.Column(db.String(32), nullable=False, unique=False)
    desc = db.Column(db.String(100), nullable=True, unique=False)
    beginTime = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())
    endTime = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())

    def __init__(self, productId, techId, status, processEval, resultEval, desc, beginTime, endTime):
        self.productId = productId
        self.techId = techId
        self.status = status
        self.processEval = processEval
        self.resultEval = resultEval
        self.desc = desc
        self.beginTime = beginTime
        self.endTime = endTime

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

    @staticmethod
    def search(infoForm):
        filter = []
        if infoForm.productId:
            filter.append(ProductControlInfo.productId == infoForm.productId)
        if infoForm.techId:
            filter.append(ProductControlInfo.techId == infoForm.techId)
        if infoForm.status:
            filter.append(ProductControlInfo.status == infoForm.status)
        if infoForm.processEval:
            filter.append(ProductControlInfo.processEval == infoForm.processEval)
        if infoForm.resultEval:
            filter.append(ProductControlInfo.resultEval == infoForm.resultEval)

        return ProductControlInfo.query.filter(and_(*filter)).limit(100).all()  # 一次性最多产生100条


# 生产产品样本
class ProductInfo(db.Model):
    ID = db.Column(db.String(255), primary_key=True, unique=False, nullable=False)
    Product_name = db.Column(db.String(255), unique=False, nullable=False)
    Product_code = db.Column(db.String(255), nullable=False)
    Industry = db.Column(db.String(255), nullable=False, unique=False)
    Drawing_url = db.Column(db.String(255), nullable=False, unique=False)
    Weld_number = db.Column(db.String(255), nullable=True, unique=False)
    Weld_position = db.Column(db.String(255), nullable=True, unique=False)
    Joint_type = db.Column(db.String(255), nullable=True, unique=False)
    Cross_section_type_size = db.Column(db.String(255), nullable=True, unique=False)
    Length_of_weld = db.Column(db.String(255), nullable=True, unique=False)
    Welding_quality_grade = db.Column(db.String(255), nullable=True, unique=False)
    Welding_quality_grade_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_performance_level = db.Column(db.String(255), nullable=True, unique=False)
    Weld_performance_level_remark = db.Column(db.String(255), nullable=True, unique=False)
    Stress_grade = db.Column(db.String(255), nullable=True, unique=False)
    Safety_grade = db.Column(db.String(255), nullable=True, unique=False)
    Imperfection_quality_level = db.Column(db.String(255), nullable=True, unique=False)
    Imperfection_quality_level_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_inspection_level = db.Column(db.String(255), nullable=True, unique=False)
    Weld_inspection_level_remark = db.Column(db.String(255), nullable=True, unique=False)
    Volumetric_tests = db.Column(db.String(255), nullable=True, unique=False)
    Surface_tests = db.Column(db.String(255), nullable=True, unique=False)
    Visual_examination = db.Column(db.String(255), nullable=True, unique=False)
    Weld_length_tolerance = db.Column(db.String(255), nullable=True, unique=False)
    Weld_length_tolerance_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_shape_tolerance = db.Column(db.String(255), nullable=True, unique=False)
    Weld_shape_tolerance_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_tolerance = db.Column(db.String(255), nullable=True, unique=False)
    Weld_tolerance_remark = db.Column(db.String(255), nullable=True, unique=False)
    Weld_method = db.Column(db.String(255), nullable=True, unique=False)

    def __init__(self, ID, Product_name, Product_code, Industry, Drawing_url, Weld_number, Weld_position, Joint_type
                 , Cross_section_type_size, Length_of_weld, Welding_quality_grade, Welding_quality_grade_remark,
                 Weld_performance_level, Weld_performance_level_remark, Stress_grade, Safety_grade,
                 Imperfection_quality_level,
                 Imperfection_quality_level_remark, Weld_inspection_level, Weld_inspection_level_remark,
                 Volumetric_tests, Surface_tests,
                 Visual_examination, Weld_length_tolerance, Weld_length_tolerance_remark, Weld_shape_tolerance,
                 Weld_shape_tolerance_remark, Weld_tolerance, Weld_tolerance_remark, Weld_method):

        self.ID = ID
        self.Product_name = Product_name
        self.Product_code = Product_code
        self.Industry = Industry
        self.Drawing_url = Drawing_url
        self.Weld_number = Weld_number
        self.Weld_position = Weld_position
        self.Joint_type = Joint_type
        self.Cross_section_type_size = Cross_section_type_size
        self.Length_of_weld = Length_of_weld
        self.Welding_quality_grade = Welding_quality_grade
        self.Welding_quality_grade_remark = Welding_quality_grade_remark
        self.Weld_performance_level = Weld_performance_level
        self.Weld_performance_level_remark = Weld_performance_level_remark
        self.Stress_grade = Stress_grade
        self.Safety_grade = Safety_grade
        self.Imperfection_quality_level = Imperfection_quality_level
        self.Imperfection_quality_level_remark = Imperfection_quality_level_remark
        self.Weld_inspection_level = Weld_inspection_level
        self.Weld_inspection_level_remark = Weld_inspection_level_remark
        self.Volumetric_tests = Volumetric_tests
        self.Surface_tests = Surface_tests
        self.Visual_examination = Visual_examination
        self.Weld_length_tolerance = Weld_length_tolerance
        self.Weld_length_tolerance_remark = Weld_length_tolerance_remark
        self.Weld_shape_tolerance = Weld_shape_tolerance
        self.Weld_shape_tolerance_remark = Weld_shape_tolerance_remark
        self.Weld_tolerance = Weld_tolerance
        self.Weld_tolerance_remark = Weld_tolerance_remark
        self.Weld_method = Weld_method

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

    @staticmethod
    def search(infoForm):
        filter = []
        if infoForm.productId:
            filter.append(ProductInfo.productId == infoForm.productId)
        if infoForm.techId:
            filter.append(ProductInfo.techId == infoForm.techId)
        if infoForm.status:
            filter.append(ProductInfo.status == infoForm.status)
        if infoForm.processEval:
            filter.append(ProductInfo.processEval == infoForm.processEval)
        if infoForm.resultEval:
            filter.append(ProductInfo.resultEval == infoForm.resultEval)

        return ProductInfo.query.filter(and_(*filter)).limit(100).all()  # 一次性最多产生100条


# 生产产品模型
class TechniqueInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    techniqueId = db.Column(db.String(16), unique=False, nullable=False)
    productKind = db.Column(db.String(16), unique=False, nullable=False)
    robotId = db.Column(db.String(16), unique=False, nullable=False)
    electricity = db.Column(db.Float, unique=False, nullable=True)
    voltage = db.Column(db.Float, unique=False, nullable=True)
    temperature = db.Column(db.Float, unique=False, nullable=True)

    def __init__(self, techniqueId, productKind, robotId, electricity, voltage, temperature):
        self.techniqueId = techniqueId
        self.productKind = productKind
        self.robotId = robotId
        self.electricity = electricity
        self.voltage = voltage
        self.temperature = temperature

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

    @staticmethod
    def search(infoForm):
        filter = []
        if infoForm.productKind:
            filter.append(TechniqueInfo.productKind == infoForm.productKind)
        if infoForm.techniqueId:
            filter.append(TechniqueInfo.techniqueId == infoForm.techniqueId)
        if infoForm.robotId:
            filter.append(TechniqueInfo.robotId == infoForm.robotId)

        return TechniqueInfo.query.filter(and_(*filter)).limit(100).all()  # 一次性最多产生100条


# 用于统计历史数据的表 ，每条记录是每一天的，通过对一列求和得到总和
class StatisticalProduceDatas(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    finiwork = db.Column(db.Integer, nullable=False)
    cancelwork = db.Column(db.Integer, nullable=False)
    procqulified = db.Column(db.Integer, nullable=False)
    procunqulified = db.Column(db.Integer, nullable=False)
    requlified = db.Column(db.Integer, nullable=False)
    reunqulified = db.Column(db.Integer, nullable=False)

    def __init__(self, date, finiwork, cancelwork, procqulified, procunqulified, requlified, reunqulified):
        self.date = date
        self.finiwork = finiwork
        self.cancelwork = cancelwork
        self.procqulified = procqulified
        self.procunqulified = procunqulified
        self.requlified = requlified
        self.reunqulified = reunqulified

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()


class StatisticalWorkTimeDatas(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    devId = db.Column(db.String(16), unique=False)
    collectorTotalNormTime = db.Column(db.Float)
    collectorTotalStopTime = db.Column(db.Float)
    robotTotalWorkTime = db.Column(db.Float)
    robotTotalRestTime = db.Column(db.Float)
    robotTotalExceptionTime = db.Column(db.Float)

    def __init__(self, devId, collectorTotalNormTime, collectorTotalStopTime, robotTotalWorkTime, robotTotalRestTime,
                 robotTotalExceptionTime):
        self.collectorTotalNormTime = collectorTotalNormTime
        self.collectorTotalStopTime = collectorTotalStopTime
        self.robotTotalWorkTime = robotTotalWorkTime
        self.robotTotalRestTime = robotTotalRestTime
        self.robotTotalExceptionTime = robotTotalExceptionTime
        self.devId = devId


# 用于管理处理所有的产品质量的从统计数据
@application.template_global()
def getTodayEval():
    re = StatisticalProduceDatas.query.filter(StatisticalProduceDatas.date == datetime.date.today()).first()
    if re:
        return re
    else:
        return StatisticalProduceDatas(datetime.date.today(), 0, 0, 0, 0, 0, 0)


@application.template_global()
def getHistoryEval():
    query = db.session.query
    re = query(func.sum(StatisticalProduceDatas.procqulified), func.sum(StatisticalProduceDatas.procunqulified),
               func.sum(StatisticalProduceDatas.requlified), func.sum(StatisticalProduceDatas.reunqulified)).first()
    if re:
        return list(re)
    else:
        return [0, 0, 0, 0]


@application.template_global()
def getHistoryProduce():
    re = StatisticalProduceDatas.query.all()
    reslut = {}
    dates = []
    finish = []
    cancel = []
    for day in re:
        finish.append(day.finiwork)
        cancel.append(day.cancelwork)
        dates.append(day.date.strftime('%Y-%m-%d'))
    reslut['dates'] = dates
    reslut['finished'] = json.dumps(finish)
    reslut['canceled'] = json.dumps(cancel)
    return reslut


# 用于管理处理所有的生产效能的从统计数据
@application.template_global()
def getTodayRunTime():
    re = DevicesRunInfo.query.filter(DevicesRunInfo.date == datetime.date.today()).all()
    result = {}
    robot = ""
    collector = ""
    for info in re:
        total = info.collectorNormalTime + info.collectorStopTime
        if total == 0:
            total = 1
        collector += info.devId + " " + "normal" + "\t" + str(100 * info.collectorNormalTime / total) + "%" + "\n"
        collector += info.devId + " " + "stop" + "\t" + str(100 * info.collectorStopTime / total) + "%" + "\n"

        total = info.robotWorkTime + info.robotRestTime + info.robotExceptionTime
        if total == 0:
            total = 1
        robot += info.devId + " " + "work" + "\t" + str(100 * info.robotWorkTime / total) + "%" + "\n"
        robot += info.devId + " " + "rest" + "\t" + str(100 * info.robotRestTime / total) + "%" + "\n"
        robot += info.devId + " " + "exception" + "\t" + str(100 * info.robotExceptionTime / total) + "%" + "\n"
    result['robot'] = robot
    result['collector'] = collector
    return result


@application.template_global()
def getHistoryRunTime():
    re = StatisticalWorkTimeDatas.query.all()
    result = {}
    robot = ''
    collector = ''
    for info in re:
        total = info.collectorTotalNormTime + info.collectorTotalStopTime
        if total == 0:
            total = 1
        collector += info.devId + " " + "normal" + "\t" + str(100 * info.collectorTotalNormTime / total) + "%" + "\n"
        collector += info.devId + " " + "stop" + "\t" + str(100 * info.collectorTotalStopTime / total) + "%" + "\n"

        total = info.robotTotalWorkTime + info.robotTotalRestTime + info.robotTotalExceptionTime
        if total == 0:
            total = 1
        robot += info.devId + " " + "work" + "\t" + str(100 * info.robotTotalWorkTime / total) + "%" + "\n"
        robot += info.devId + " " + "rest" + "\t" + str(100 * info.robotTotalRestTime / total) + "%" + "\n"
        robot += info.devId + " " + "exception" + "\t" + str(100 * info.robotTotalExceptionTime / total) + "%" + "\n"

    result['robot'] = robot
    result['collector'] = collector
    return result


# 管理设备配置的表主要是采集设备
class DeviceInfo(db.Model):  # 先放着
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uniqueid = db.Column(db.String(16), unique=True)
    ip = db.Column(db.String(16), unique=False, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    route = db.Column(db.String(64), unique=True, nullable=False)
    type = db.Column(db.String(64), unique=False, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    robotId = db.Column(db.String(16), nullable=True)  # 盒子连接得ROBOT desc
    status = db.Column(db.String(16), nullable=False)  # normal delete表示设备已删除

    def __init__(self, uniqueid, ip, port, type, name, robot_id, status):
        self.uniqueid = uniqueid
        self.ip = ip
        self.port = port
        self.route = str(ip) + ':' + str(port)
        self.type = type
        self.name = name
        self.robotId = robot_id
        self.status = status  # normal delete表示设备已删除

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()


# 机器人信息的表
class RobotInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uniqueid = db.Column(db.String(16), unique=True)
    type = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    factoryId = db.Column(db.String(100), nullable=False)
    imageURL = db.Column(db.String(100), nullable=False)
    posX = db.Column(db.Float, nullable=False)
    posY = db.Column(db.Float, nullable=False)
    posZ = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)

    def __init__(self, type, model, status, factoryId, imageURL, posX, posY, posZ,width,height):
        self.uniqueid = randomStr(16)
        self.type = type
        self.model = model
        self.status = status
        self.factoryId = factoryId
        self.imageURL = imageURL
        self.posX = posX
        self.posY = posY
        self.posZ = posZ
        self.width = width
        self.height = height

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()

# 机器人信息的表
class FactoryInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uniqueid = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(64), unique=True)
    latitude = db.Column(db.Float, unique=True)
    longitude = db.Column(db.Float, unique=True)
    robotIds = db.Column(db.String(128), unique=True)

    def __init__(self, name, latitude, longitude, factoryId, robotIds):
        self.uniqueid = randomStr(16)
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.robotIds = robotIds

    def save(self):
        db.session.add(self)
        db.session.commit()


class RobotRunInfo(db.Model):
    uniqueid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    techniqueId = db.Column(db.String(64), nullable=False)
    time = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())
    run_status = db.Column(db.String(64), nullable=False)

    def __init__(self, time, techniqueId, run_status):
        self.techniqueId = techniqueId
        self.time = time
        self.run_status = run_status

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()


class InteractiveMessageInfo(db.Model):
    messageid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flowid = db.Column(db.String(16), unique=False)
    time = db.Column(db.DateTime, unique=False, default=datetime.datetime.now())
    type = db.Column(db.String(16), unique=False)
    data = db.Column(db.String(1024), unique=False)
    sender = db.Column(db.String(16), unique=False)
    receiver = db.Column(db.String(16), unique=False)

    def __init__(self, flow_id, time, type, data, sender, receiver):
        self.flow_id = flow_id
        self.time = time
        self.type = type
        self.data = data
        self.sender = sender
        self.receiver = receiver

    def save(self):
        db.session.add(self)
        db.session.commit()

    def commit(self):
        db.session.commit()


# 成本消耗
class Cost(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    power_consumption = db.Column(db.Float, unique=False, nullable=True)
    air_consumption = db.Column(db.Float, unique=False, nullable=True)
    welding_wire_consumption = db.Column(db.Float, unique=False, nullable=True)

    def __init__(self, power_consumption, air_consumption, welding_wire_consumption):
        self.date = datetime.date.today()
        self.power_consumption = power_consumption
        self.air_consumption = air_consumption
        self.welding_wire_consumption = welding_wire_consumption

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


# 获取历史的成本消耗数据
def getHistoryCost():
    totalCost = Cost.query.all()
    result = {}
    date = []
    power = []
    air = []
    welding_wrie = []
    for cost in totalCost:
        date.append(cost.date.strftime('%Y-%m-%d'))
        air.append(cost.air_consumption)
        power.append(cost.power_consumption)
        welding_wrie.append(cost.welding_wire_consumption)
    result['air'] = air
    result['date'] = date
    result['power'] = power
    result['weldingwire'] = welding_wrie
    return result


# agv的表
class AgvPos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pos_X = db.Column(db.Float, default=0)
    pos_Y = db.Column(db.Float, default=0)
    pos_Z = db.Column(db.Float, default=0)

    def __init__(self, x, y, z):
        self.pos_Z = z
        self.pos_Y = y
        self.pos_X = x

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
