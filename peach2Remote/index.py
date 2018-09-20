# -*- coding: utf-8 -*-

#此处是index控制器--为公司页面的

from app import application
from flask import render_template

@application.route('/')
@application.route('/index')
def index_index():
    return render_template('company/index.html',titlename='index')

@application.route('/index/login')
def index_login():
    return render_template('manage/login.html',tilename='login')

@application.route('/index/signup')
def index_signup():
    return render_template('manage/sign.html',tilename='signup')


@application.route('/index/noauthority')
def index_noauthority():
    return render_template('company/noauthority.html',titlename='noahthority')
