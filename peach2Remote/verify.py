# -*- coding: utf-8 -*-
from app import application
import user
from flask import redirect,url_for,request

@application.before_request
def before_request():
    #进行默认验证
    controller=(request.path.split('/'))[1]
    if controller in application.config['NEED_AUTH']:
        if user.isGuest():
            return redirect(url_for('index_noauthority'))
        else:
            pass
    else:
        pass

@application.teardown_request
def treardown_request(exception):
    pass

@application.after_request
def after_request(response):
    return response
