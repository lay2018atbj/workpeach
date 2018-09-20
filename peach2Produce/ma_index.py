# -*- coding: utf-8 -*-
from app import application
from flask import render_template, request, redirect, url_for
from models import LocalHostConfig
from models import RemoteHostConfig


@application.route('/ma_index')
@application.route('/ma_index/index')
def ma_index_index():
    return redirect(url_for('ma_producreport_qulity'))


@application.route('/ma_index/config')
def ma_index_config():
    local = LocalHostConfig.load(request)
    remote = RemoteHostConfig.load(request)
    return render_template('manage/config.html', titlename='Config',
                           localModel=local,
                           remoteModel=remote)

@application.route('/ma_index/product')
def ma_index_product():
    return render_template('manage/productManager.html', titlename='Product')

@application.errorhandler(404)
def page_not_found(error):
    return render_template('manage/404.html', titlename='404'), 404


@application.errorhandler(500)
def page_error(error):
    return render_template('manage/500.html', titlename='500'), 500



