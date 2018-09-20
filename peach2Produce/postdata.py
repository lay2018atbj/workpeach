# -*- coding: utf-8 -*-
import requests
import utils
import json


host='www.baidu.com'
timeout=1

#post寄送数据
#data为实际的pyhton对象
#controller为发送的控制器 action为该控制器下的动作
def PostData(data,controller,action,params=None):
    #底层post的为json数据
    headers = {
        "Host": host,
        "Content-Type": "application/json",
        "Referer": "http://"+host,  # 必须带这个参数，不然会报错
             }
    real_url='http://'+host+'/'+controller+'/'+action
    try:
        response=requests.post(url=real_url,headers=headers,data=utils.encrypt_json(data=data),timeout=timeout,params=params)
        if response.status_code == 200:
            return ('success',utils.decrypt_json(response.text))
        else:
            return ('code:'+str(response.status_code),'未知错误')
    except requests.Timeout:
        return ('failed','响应超时')
    except json.decoder.JSONDecodeError:
        return ('failed','json格式错误')

#用于应答对方使用的PostData
def MakePostResponse(data):
    return utils.encrypt_json(data=data)

#post寄送数据
#data为实际的pyhton对象
#controller为发送的控制器 action为该控制器下的动作
def PostDataNoCrypt(data,controller,action,params=None):
    #底层post的为json数据
    headers = {
        "Host": host,
        "Content-Type": "application/json",
        "Referer": "http://"+host,  # 必须带这个参数，不然会报错
             }
    real_url='http://'+host+'/'+controller+'/'+action
    try:
        response=requests.post(url=real_url,headers=headers,data=json.dumps(data),timeout=timeout,params=params)
        if response.status_code == 200:
            return ('success',json.load(response.text))
        else:
            return ('code:'+str(response.status_code),'未知错误')
    except requests.Timeout:
        return ('failed','响应超时')
    except json.decoder.JSONDecodeError:
        return ('failed','json格式错误')

#用于应答对方使用的PostData
def MakePostResponseNoCrypt(data):
    return json.dumps(data)
