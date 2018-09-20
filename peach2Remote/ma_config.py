# -*- coding: utf-8 -*-
from app import application,configParser,db
from flask import request, url_for, redirect
from models import NewProduceServer

@application.route('/ma_config/addsever',methods={'POST'})
def ma_config_addsever():
    produceServer=NewProduceServer.load(request)
    produceServer.save()
    return redirect(url_for('ma_index_config'))

@application.route('/ma_config/deletesever',methods={'POST'})
def ma_config_deletesever():
    if 'selectedSever' in request.form:
        server=NewProduceServer.query.filter_by(serverID=request.form['selectedSever']).first()
        if server:
            db.session.delete(server)
            db.session.commit()
    return redirect(url_for('ma_index_config'))

@application.template_global()
def getAllSevers():
    return NewProduceServer.query.all()

