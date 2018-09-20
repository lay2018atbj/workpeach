# -*- coding: utf-8 -*-
from app import application
from flask import render_template
from models import getTodayEval,getHistoryEval,getHistoryProduce,getTodayRunTime,getHistoryRunTime,getHistoryCost

@application.route('/ma_producreport/qulity')
def ma_producreport_qulity():
    todayEval=getTodayEval()
    historyEval=getHistoryEval()
    historyProduce=getHistoryProduce()
    return render_template('manage/productionqulity.html',titlename='生产质量',todayEval=todayEval,historyEval=historyEval,historyProduce=historyProduce)

@application.route('/ma_producreport/efficiency')
def ma_producreport_efficiency():
    todayRuntime=getTodayRunTime()
    historyRuntime = getHistoryRunTime()
    return render_template('manage/productionefficiency.html', titlename='生产效能',todayRuntime=todayRuntime,historyRuntime=historyRuntime)

@application.route('/ma_producreport/cost')
def ma_producreport_cost():
    re=getHistoryCost()
    return render_template('manage/productioncost.html', titlename='成本消耗',datas=re)

@application.route('/ma_producreport/materialstock')
def ma_producreport_materialstock():
    return render_template('manage/materialstock.html', titlename='材料库存')
