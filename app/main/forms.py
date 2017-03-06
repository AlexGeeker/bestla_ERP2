# -*- coding: utf-8 -*-

from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields import SelectField,RadioField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import time
from datetime import date,timedelta

currentdate = time.strftime("%Y-%m-%d", time.localtime())
today = date.today()
yesterday = date.today() - timedelta(1)
twoday = date.today() - timedelta(2)
threeday = date.today() - timedelta(3)
fourday = date.today() - timedelta(4)

CSVdescrpition = u'选择CSV文件（要求1：文档第一行必须有”条码“，2：文件名规范：姓名简称+日期）：'

class NameForm(FlaskForm):
    name = StringField(u'单号查询，请输入单号：', validators=[Required()])
    submit = SubmitField(u'提交')

# 上传文件表单
class UploadForm(FlaskForm):
    file = FileField( CSVdescrpition,validators=[
        FileAllowed(['csv'], u'只能上传csv文件！'),
        FileRequired(u'文件未选择！')])
    date = SelectField(u'选择发货日期:', choices=[
        (str(today), today),
        (str(yesterday), yesterday),
        (str(twoday), twoday),
        (str(threeday), threeday),
        (str(fourday), fourday)])
    name = RadioField(u'选择姓名:', choices=[
        ('WeiSui', u'韦随'),
        ('HuangShuo', u'黄硕'),
        ('LiJinSheng', u'李金生'),
        ('LiuYun', u'刘云')],
        validators=[DataRequired()])

    submit = SubmitField(u'上传')