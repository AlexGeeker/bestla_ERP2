# -*- coding: utf-8 -*-

import time,datetime
from . import dbs

tableName = 'KDTJ'+time.strftime("%Y%m", time.localtime())
# 上个月的tablename
today = datetime.date.today()
first = today.replace(day=1)
lastMonth = first - datetime.timedelta(days=1)
lastMonthTable = 'KDTJ'+lastMonth.strftime("%Y%m")

class Record(dbs.Model):
    __tablename__ = tableName
    ID = dbs.Column(dbs.Integer, primary_key=True, autoincrement=True)
    NAME = dbs.Column(dbs.TEXT, nullable=False)
    DANHAO = dbs.Column(dbs.TEXT, nullable=False)
    WULIU = dbs.Column(dbs.TEXT, nullable=False)
    DATE = dbs.Column(dbs.TEXT)

    def __init__(self,name,danhao,wuliu,date):
        self.NAME = name
        self.DANHAO = danhao
        self.WULIU = wuliu
        self.DATE = date

class Last_Month_Record(dbs.Model):
    __tablename__ = lastMonthTable
    ID = dbs.Column(dbs.Integer, primary_key=True, autoincrement=True)
    NAME = dbs.Column(dbs.TEXT, nullable=False)
    DANHAO = dbs.Column(dbs.TEXT, nullable=False)
    WULIU = dbs.Column(dbs.TEXT, nullable=False)
    DATE = dbs.Column(dbs.TEXT)

    def __init__(self,name,danhao,wuliu,date):
        self.NAME = name
        self.DANHAO = danhao
        self.WULIU = wuliu
        self.DATE = date