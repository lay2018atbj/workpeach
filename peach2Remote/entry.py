# -*- coding: utf-8 -*-

# 入口运行模块


# 导入各模块（即控制器，配置）
from app import application
import index  # 导入index控制器
import user  # 导入user控制器
import ma_index  # 导入manage后台的index控制器
import ma_config  # 导入配置 控制器

import verify  # 导入验证模块 主要是请求的权限验证

################################基础内容全部加载完毕################################

# 初始化配置
import json
from app import configParser,db
import devsocket
from flask import escape

db.create_all()

configParser.read('config.ini')

#加载本机标识符
application.config['LOCALHOSTID'] = configParser.get('LocalHost','id')

#添加用户
if not user.User.query.first():
    u=user.User('admin','123456','123456@qq.com')
    db.session.add(u)
    db.session.commit()

if __name__ == '__main__':
    application.run(host=application.config['HOST'], port=application.config['PORT'],use_reloader=False)

