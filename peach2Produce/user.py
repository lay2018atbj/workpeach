# -*- coding: utf-8 -*-
from models import User
from app import application
from flask import session,request,abort,redirect,url_for,escape,flash

#使用session 默认记住(即过期时间长)

#实际登录动作
@application.route('/user/login',methods=['POST','GET'])
def user_login():
    if request.method == 'POST':
        if not isGuest():
            return redirect(url_for('index_index'))
        else:
            username=request.form.get('username')
            password=request.form.get('password')
            if User.login(username,password):
                return redirect(url_for('ma_index_index'))
            else:
                flash(u'你输入的账户或者密码有错误','user_login_error')
                return redirect(url_for('index_login'))
    else:
        abort(404)
        
#新建用户动作
@application.route('/user/signup',methods=['POST','GET'])
def user_signup():
    if request.method == 'POST':
        if not isGuest():
            return redirect(url_for('index_index'))
        else:
            user=User(username=request.form['username'],
                      password=request.form['password'],
                      email=request.form['email'],
                      )
            if user.save():
                return redirect(url_for('index_index'))
            else:
                flash(u'注册失败','user_add_error')
                return redirect(url_for('index_login'))
                
    else:
        abort(404)

#注销动作
@application.route('/user/logout',methods=['POST','GET'])
def user_logout():
    if not isGuest():
        session.pop('username_key')
        session.pop('password')
        
    return redirect(url_for('index_index'))


##################################################################################


#注册到模板可以在模板中直接使用

#判断是否登录
@application.template_global()
def isGuest():
    if 'username_key' in session:
        re=User.query.filter_by(key=session['username_key']).first()
        if re and re.isRight(session['password'],False):
            return False
        else:
            return True
    else:
        return True;

#如果登录返回用户名 没有则返回空
@application.template_global()
def GetUserName():
    if not isGuest():
        re=User.query.filter_by(key=session['username_key']).first()
        return str(escape(re.username))
    else:
        return









    
