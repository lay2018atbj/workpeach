# -*- coding: utf-8 -*-
from app import application
from flask import request, url_for, redirect
from models import LocalHostConfig, RemoteHostConfig,DeviceInfo
from deviceManager import NewDevice
import json
import devsocket

@application.route('/ma_config/setlocal', methods=['POST'])
def ma_config_setlocal():
    local = LocalHostConfig.load(request)
    local.save()
    return redirect(url_for('ma_index_config'))


@application.route('/ma_config/setremote', methods=['POST'])
def ma_config_setremote():
    remote = RemoteHostConfig.load(request)
    remote.save()
    return redirect(url_for('ma_index_config'))


@application.route('/ma_config/adddevice', methods=['POST'])
def ma_config_adddevice():
    device = NewDevice.load(request)
    device.save()
    devsocket.startCollectedThread(device)
    return redirect(url_for('ma_index_config'))

@application.route('/ma_config/removedevice', methods=['POST'])
def ma_config_removedevice():
    try:
        device_id = int(request.form.get('id'))
        if device_id in application.config['DEVICES']:
            device_info = application.config['DEVICES'].pop(device_id)
            device_info["scoket"].close()
    except Exception as e:
        print('close falied')
        print(e)

    dev = DeviceInfo.query.filter_by(id=int(device_id)).first()
    dev.status = 'delete'
    dev.commit()
    return redirect(url_for('ma_index_config'))



@application.route('/ma_config/connectdevice', methods=['POST'])
def ma_config_connectdevice():
    try:
        device_id = int(request.form.get('id'))
        if device_id in application.config['DEVICES'] and application.config['DEVICES'][device_id]['status'] == 'stop':
            device = NewDevice.load(request)
            device.save()
            devsocket.startCollectedThread(device)
        elif application.config['DEVICES'][device_id]['status'] != 'stop':
            print("not stop")
        else:
            print("not found or not stop")
    except Exception as e:
        print(e)
    return redirect(url_for('ma_index_config'))

