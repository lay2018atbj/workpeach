from app import application, db
import socket
import threading
from datamodels import CollectedDatas
from models import ProductControlInfo
import time
import datetime
import recordworktime  # 导入记录采集设备和机器人工作时间的模块
import deviceManager
import signalsPool
import json
from flask import request, url_for, render_template, request, redirect


@application.route('/ma_product/manufacture_begin', methods=['POST', 'GET'])
def ma_manufacture_begin():
    if request.method == 'POST':
        product_id = request.form.get('productId')
        technique_id = request.form.get('techniqueId')
        desc = request.form.get('desc')
    else:
        product_id = request.args.get('productId')
        technique_id = request.args.get('techniqueId')
        desc = request.args.get('desc')

    status = 'PROCESSING'
    process_eval = 'UNCHECK'
    result_eval = 'UNCHECK'

    begin_time = datetime.datetime.now()
    end_time = datetime.date(2100, 1, 1)

    product = ProductControlInfo.query.filter_by(productId=product_id).first()
    if not product:
        new_product = ProductControlInfo(product_id, technique_id, status, process_eval, result_eval, desc, begin_time,
                                  end_time)
        new_product.save()
    else:
        product.status = status
        product.technique_id = technique_id
        product.desc = desc
        product.processEval = process_eval
        product.resultEval = result_eval
        product.beginTime = begin_time
        product.endTime = end_time
        product.commit()

    signalsPool.PRODUCT_BEGIN.send(product_id, time=time.time())
    return redirect(url_for('ma_index_product'))


@application.route('/ma_product/manufacture_end', methods=['POST', 'GET'])
def ma_manufacture_end():
    if request.method == 'POST':
        product_id = request.form.get('productId')
        processEval = request.form.get('processEval')
        resultEval = request.form.get('resultEval')
    else:
        product_id = request.args.get('productId')
        processEval = request.args.get('processEval')
        resultEval = request.args.get('resultEval')

    status = 'FINISHED'
    end_time = datetime.datetime.now()

    product = ProductControlInfo.query.filter_by(productId=product_id).first()
    if not product:
        pass
    else:
        product.status = status
        product.processEval = processEval
        product.resultEval = resultEval
        product.endTime = end_time
        product.commit()

    signalsPool.PRODUCT_FINISHED.send(product_id, time=time.time())
    return redirect(url_for('ma_index_product'))
