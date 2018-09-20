# -*- coding: utf-8 -*-
from app import application
from flask import render_template,request
from models import LocalHostConfig
from models import RemoteHostConfig


@application.route('/ma_index')
@application.route('/ma_index/index')
def ma_index_index():
    return render_template('manage/index.html',titlename="Index")

@application.route('/ma_index/config')
def ma_index_config():
    return render_template('manage/config.html',titlename='Config')


@application.errorhandler(404)
def page_not_found(error):
    return render_template('manage/404.html',titlename='404'), 404

@application.errorhandler(500)
def page_error(error):
    return render_template('manage/500.html',titlename='500'), 500

