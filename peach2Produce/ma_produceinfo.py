# -*- coding: utf-8 -*-
from app import application
from flask import render_template, request
from models import SearchInfoForm, SearchTechniqueInfoForm


@application.route('/ma_produceinfo/searchinfo', methods=['POST', 'GET'])
def ma_produceinfo_searchinfo():
    searchForm = SearchInfoForm.load(request=request)
    return render_template('manage/infotableview.html', titleaname='产品信息', formModel=searchForm)


@application.route('/ma_techniqueinfo/searchinfo', methods=['POST', 'GET'])
def ma_techniqueinfo_searchinfo():
    searchForm = SearchTechniqueInfoForm.load(request=request)
    return render_template('manage/techniqueManager.html', titleaname='工艺信息', formModel=searchForm)
