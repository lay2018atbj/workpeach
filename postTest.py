# -*- coding: utf-8 -*-
import requests



def login(base_url):
    # post需要的表单数据，类型为字典

    login_data = {
        'username': 'admin',
        'password': '123456',
    }

    form_data = {
        'productId': 4,
        'techniqueId': 'SK3',
        'desc': '钛合金'
    }
    # 设置头信息
    headers_base = {
        'content-type': "application/x-www-form-urlencoded"
    }

    login_url = base_url + "/index/login"
    form_url  = base_url + "/ma_product/manufacture_begin"

    # requests 的session登录，以post方式，参数分别为url、headers、data
    my_session = requests.Session()
    content = my_session.post(login_url, headers=headers_base, data=login_data)

    print(content.text)
   
    content = my_session.post(form_url, headers=headers_base, data=form_data)
    print(content.text)
login('http://127.0.0.1')
