# -*- coding: utf-8 -*-
#测试控制器

from app import application
from flask import request
import utils


@application.route('/test/operation',methods=['POST','GET'])
def test_operation():
    if request.method=="POST":
        data=request.get_data()
        flg,content=utils.ParseData(data)
        if flg != 'success':
            return flg+':'+content
        else:
            return utils.encrypt_json({'name':'ok','content':'解析成功,命令生效'})
