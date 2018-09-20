# -*- coding: utf-8 -*-


#flask应用程序实例模块
from flask import Flask
#from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import configparser


application = Flask(__name__) #主程序实例
application.config.from_object('config')#应用配置
#bootstrap = Bootstrap(application)#bootstrap的实例 直接使用bootstrap
db = SQLAlchemy(application)#使用mysql数据库

#读取和解析配置文件
configParser=configparser.ConfigParser()

