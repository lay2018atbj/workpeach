# -*- coding:utf-8 -*-
from app import application
from flask import url_for, render_template, request
from models import RobotInfo, AgvPos, getTodayEval, getHistoryEval, \
    getHistoryProduce, getTodayRunTime, getHistoryRunTime, getHistoryCost


@application.route('/ma_workshorp/overall', methods=['GET', 'POST'])
def ma_workshop_overall():
    if ("workplace_id" in request.args):
        workplace_id = request.args["workplace_id"]
    else:
        workplace_id = 1
    robotModels = RobotInfo.query.filter_by(factoryId=workplace_id).all()
    todayRuntime = getTodayRunTime()
    historyRuntime = getHistoryRunTime()
    historyCost = getHistoryCost()
    return render_template('manage/overall.html', titlename='总控视图',
                           robotModels=robotModels, todayRuntime=todayRuntime,
                           historyRuntime=historyRuntime, historyCost=historyCost,
                           )
