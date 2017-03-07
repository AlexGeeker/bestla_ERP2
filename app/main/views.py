# -*- coding: utf-8 -*-

import shutil,os,csv,urllib2,json,time,datetime
from datetime import date,timedelta
from flask import render_template,redirect,url_for,send_from_directory,request,flash
from werkzeug.utils import secure_filename
from ..models import Record,Last_Month_Record
from . import main
from .forms import NameForm,UploadForm
from .. import dbs

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = '../static/upload'
yesterday = date.today() - timedelta(1)
# 本月
currentMonth = time.strftime("%Y%m", time.localtime())
# 上月
today = datetime.date.today()
first = today.replace(day=1)
lastMon = first - datetime.timedelta(days=1)
lastMonth = lastMon.strftime("%Y%m")

@main.route('/', methods=['GET', 'POST'])
def index():
    # 从网页获取单号
    findDanhao = []
    form1 = NameForm()
    if form1.submit1.data and form1.validate_on_submit():
        danhao = form1.name.data
        danhao = danhao.strip()  # strip()的作用是去掉左右空格
        form1.name.data = ''
        # 查询单号（本月及上月）
        findDanhao = dbs.session.query(Record).filter(Record.DANHAO == danhao).all() + dbs.session.query(Last_Month_Record).filter(Last_Month_Record.DANHAO == danhao).all()

    # 本月快递总数
    allCount = dbs.session.query(Record).count()

    # 今天/昨天/本月 各人发件数
    todayCount = {}
    yesterdayCount = {}
    everyoneCount = {} # 本月
    for one in dbs.session.query(Record.NAME).distinct():
        todayCount[one[0]] = dbs.session.query(Record).filter(Record.DATE == today).filter(Record.NAME == one[0]).count()
        yesterdayCount[one[0]] = dbs.session.query(Record).filter(Record.DATE == yesterday).filter(Record.NAME == one[0]).count()
        everyoneCount[one[0]] = dbs.session.query(Record).filter(Record.NAME == one[0]).count()

    # 本月各快递总数
    kuaidicount = {}
    for wuliu in dbs.session.query(Record.WULIU).distinct():
        kuaidicount[wuliu[0]] = dbs.session.query(Record).filter(Record.WULIU == wuliu[0]).count()

    # 上个月各快递公司总数
    lastMonth_kuaidicount = {}
    for wuliu in dbs.session.query(Last_Month_Record.WULIU).distinct():
        lastMonth_kuaidicount[wuliu[0]] = dbs.session.query(Last_Month_Record).filter(Last_Month_Record.WULIU == wuliu[0]).count()

    # 上个月每人发件数
    lastMonth_everyoneCount = {}
    for one in dbs.session.query(Last_Month_Record.NAME).distinct():
        lastMonth_everyoneCount[one[0]] = dbs.session.query(Last_Month_Record).filter(Last_Month_Record.NAME == one[0]).count()

    data = dict()
    data["today"] = todayCount
    data["yestoday"] = yesterdayCount
    data["thismonth"] = kuaidicount
    data["everyone"] = everyoneCount
    data["last"] = lastMonth_kuaidicount
    data["last_everyone"] = lastMonth_everyoneCount

    ### 上传文件部分 ###
    filedata = dict()  # 通过该词典传递多个参数

    form2 = UploadForm()
    fname = None  # 文件安全名
    name = None  # 发件人姓名
    selected_date = None
    existed_record = 0
    recorded = 0

    if form2.submit2.data and form2.validate_on_submit():

        selected_date = form2.date.data
        name = form2.name.data
        fname = secure_filename(form2.file.data.filename)

        # 获取文件名
        file_dir = os.path.join(basedir, UPLOAD_FOLDER)  # 文件路径
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)  # 如果文件夹不存在，则创建文件夹

        # 文件名重复判断
        ii = 0
        print file_dir
        for parent, dirnames, filenames in os.walk(file_dir):  # 遍历目录并调用数据库写入函数
            for filename in filenames:
                if filename == fname:
                    ii = ii + 1
        if ii == 0:
            form2.file.data.save(os.path.join(file_dir, fname))  # 保存文件到upload目录
        else:
            filedata["name"] = name
            filedata["fname"] = fname
            filedata["date"] = selected_date
            return render_template('index.html', form1=form1, form2=form2, data = data, message=u'该文件已存在，请重新上传！', filedata = filedata, existed_record = existed_record, recorded = recorded)

        # 读取文件，并对比数据库
        with open(os.path.join(file_dir, fname)) as csvFile:
            new_record = None
            dictreader = csv.DictReader(csvFile)
            for line in dictreader:
                danhao = line['\xcc\xf5\xc2\xeb'].strip()
                i = dbs.session.query(Record).filter(Record.DANHAO == danhao).count() + dbs.session.query(
                    Last_Month_Record).filter(Last_Month_Record.DANHAO == danhao).count()
                if i > 0:  # 如果单号已经存在于数据中
                    existed_record = existed_record + 1
                elif i == 0:  # 若单号不在数据库中，则写入数据库
                    recorded = recorded + 1
                    if selected_date[0:4] + selected_date[5:7] == lastMonth:
                        new_record = Last_Month_Record(name, danhao, "0", selected_date)
                    elif selected_date[0:4] + selected_date[5:7] == currentMonth:
                        new_record = Record(name, danhao, "0", selected_date)
                        dbs.session.add(new_record)
                elif recorded > 50:
                    try:
                        dbs.session.commit()
                    except:
                        dbs.session.rollback()
        try:
            dbs.session.commit()
        except:
            dbs.session.rollback()

        # 创建当天日期文件夹，并将文件转移至该文件夹
        currentday_file_dir = os.path.join(file_dir, selected_date)
        if not os.path.exists(currentday_file_dir):  # 如果文件夹不存在，则创建文件夹
            os.makedirs(currentday_file_dir)
        shutil.move(os.path.join(file_dir, fname), currentday_file_dir)

    filedata["name"] = name
    filedata["fname"] = fname
    filedata["date"] = selected_date
    return render_template('index.html', form1=form1, findDanhao=findDanhao, total=allCount, data = data,form2=form2, existed_record=existed_record, recorded=recorded,filedata = filedata)


# 显示上个月每天每人发件数
@main.route('/<user_name>', methods=['GET', 'POST'])
def show_last_month_data(user_name):
    count = []
    for odate in dbs.session.query(dbs.distinct(Last_Month_Record.DATE)):
        count.append(([odate[0]],dbs.session.query(Last_Month_Record).filter(Last_Month_Record.NAME == user_name, Last_Month_Record.DATE == odate[0]).count()))

    return render_template('lastmonth.html', count=count)

# 更新快递
@main.route('/kuaidi/update', methods=['GET', 'POST'])
def kuaidi_update():
    # 单号识别
    def getKD(DanHao):
        response = urllib2.urlopen("http://www.kuaidi100.com/autonumber/auto?num="+DanHao).read().decode('utf-8')
        if response == '[]':
            print '尚无记录！'
            return '0'
        else:
            responseJson = json.loads(response)
            return responseJson[0]["comCode"]

    # 更新快递
    x = 0
    for wuliu in dbs.session.query(Record).filter(Record.WULIU == '0').all():
        x = x + 1
        kuaidi = getKD(wuliu.DANHAO)
        record = dbs.session.query(Record).filter(Record.DANHAO == wuliu.DANHAO).first()
        record.WULIU = kuaidi
        if x > 100:
            try:
                dbs.session.commit()
            except:
                dbs.session.rollback()
        print u'%s已更新为%s' % (wuliu.DANHAO, kuaidi)

    # 更新上月
    y = 0
    for wuliu in dbs.session.query(Last_Month_Record).filter(Last_Month_Record.WULIU == '0').all():
        y = y+1
        kuaidi = getKD(wuliu.DANHAO)
        record = dbs.session.query(Last_Month_Record).filter(Last_Month_Record.DANHAO == wuliu.DANHAO).first()
        record.WULIU = kuaidi
        if y >100:
            try:
                dbs.session.commit()
            except:
                dbs.session.rollback()
        print u'%s已更新为%s' % (wuliu.DANHAO, kuaidi)
    try:
        dbs.session.commit()
    except:
        dbs.session.rollback()

    return redirect(url_for(".index"))

# robots.txt
@main.route('/robots.txt')
def static_from_root():
    return send_from_directory(main.static_folder, request.path[1:])