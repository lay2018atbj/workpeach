# -*- coding: utf-8 -*-
from app import application
from models import MessageLog
from flask import request
import postdata
import models
import  utils

#请求数据格式
#flow_id:id
#message_id:id
#identifier:id
#type:#[command/data]

#type=command
#command-type:[search_tech]
#command-data:{workpiece_id,factory_id,machine_id}

#type=data
#data:{.....}

#context:'' 保留字段
#time:now()

def dealName(name):
    return name.capitalize()

def GetWeldingMethodQuery(Remark):
    """通过remark获取相应工艺明细的模型的query实例"""
    #将表名处理为实际对应的模型名
    try:
        tableName=application.config['WELDINGTABLE'][Remark]
        clsName=''.join(list(map(dealName, tableName.split('_'))))
        return eval('models.'+clsName+'.query')
    except Exception as e:
        print(e)
        return None

#处理命令的操作 即type=command
def dealCommand(data):
    try:
        if data['command-type']=='search_tech':
            info = models.WorkpieceInformation.query.filter_by(Workpiece_ID=data['command-data']['workpiece_id']).first()
            if info :
                query = GetWeldingMethodQuery(info.Remark)
                methods = query.filter_by(Workpiece_ID_A=info.Workpiece_ID).all()
                if methods:
                    responseData={'type':'data','data':{}}
                    for method in methods:
                        responseData['data'][method.Weld_method]=dict(method)
                    return postdata.MakePostResponseNoCrypto(responseData)
                else:
                    return postdata.MakePostResponseNoCrypto({'type': 'data', 'data': '没有找到处理相应工件的工艺'},flow_id=data['flow_id'])
            else:
                return postdata.MakePostResponseNoCrypto({'type':'data','data':'没有找到工件id'},flow_id=data['flow_id'])
    except Exception as e:
        return postdata.MakePostResponseNoCrypto({'type':'data','data':str(e)},flow_id=data['flow_id'])

#处理数据的操作 即type=data
def dealData(data):
    pass

@application.route('/local_response/operate',methods=['POST'])
def local_response_operate():
    """先统一消息进入日志 然后传入相应的函数进行处理"""
    try:
        data = postdata.ParseData(request.data)
        msg = MessageLog(data['flow_id'],data['message_id'],request.data)
        msg.add()
        if data['type'] == 'command':
            return dealCommand(data)
        elif data['type'] == 'data':
            return dealData(data)
        else:
            return postdata.MakePostResponseNoCrypto({'type': 'data', 'data': '解析不了'},flow_id=0)
    except Exception as e:
        return postdata.MakePostResponseNoCrypto({'type': 'data', 'data': str(e)},flow_id=0)
