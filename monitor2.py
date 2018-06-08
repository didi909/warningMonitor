#!/usr/bin/python
# -*- coding: UTF-8 -*-
import subprocess
import pymysql
import socket
import logging
import time
import sys,traceback
from apscheduler.schedulers.blocking import  BlockingScheduler

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='monitor.log',
                    filemode='a')
def get_checklist(ip):
    try:
        db = pymysql.connect(host='192.168.2.197', port=3306, user='ywjk', passwd='mysql098', db='ywdb')
        cursor = db.cursor()
        sql = "select server,check_type,check_command from check_server where server='%s'" % ip
        try:
            cursor.execute(sql)
            check_list = cursor.fetchall()
        except:
            logging.error(traceback.print_exception(*sys.exc_info()))
    except:
        logging.error(traceback.print_exception(*sys.exc_info()))
    return check_list
def insert_checkresult(ip,check_type,check_result):
    insert_result=0
    try:
        db = pymysql.connect(host='192.168.2.197', port=3306, user='ywjk', passwd='mysql098', db='ywdb')
        cursor = db.cursor()
        check_time=time.strftime("%Y-%m-%d %X")
        sql = "insert into check_result() values('%s','%s','%s','%s')" % (ip,check_type,check_result,check_time)
        try:
            cursor.execute(sql)
            db.commit()
            insert_result=1
        except:
            db.rollback()
            logging.error(traceback.print_exception(*sys.exc_info()))
            insert_result=2
        if any(str_ in check_result for str_ in('CRITICAL','WARNING','FAILED')):
            sql2="insert into send_message() values('%s','%s','%s','%s','N')" % (ip,check_type,check_result,check_time)
            try:
                cursor.execute(sql2)
                db.commit()
                insert_result=1
            except:
                db.rollback()
                logging.error(traceback.print_exception(*sys.exc_info()))
                insert_result=2
        else:
            pass
    except:
        logging.error(traceback.print_exception(*sys.exc_info()))
    return insert_result
def workprocess():
    ip = socket.gethostbyname(socket.gethostname())
    a=get_checklist(ip)
    logging.info(ip)
    for i in a:
        ip=i[0]
        check_type=i[1]
        command=i[2]
        logging.info(ip)
        logging.info(check_type)
        logging.info(command)
        #check_result=subprocess.getoutput(command)
        #logging.info(check_result)
        (theCheckStatus,check_result) = subprocess.getstatusoutput(command)
        logging.info(check_result)
        if theCheckStatus==0:
            insert_result=insert_checkresult(str(ip),str(check_type),str(check_result))
        else:
            check_result=check_type+" EXECUTE FAILED"
            insert_result=insert_checkresult(str(ip),str(check_type),str(check_result))
        logging.info(check_result)
        logging.info("check data insert database status:"+str(insert_result))
sched = BlockingScheduler()
sched.add_job(workprocess,'cron',minute='00,10,20,30,40,50',hour='8-18',day_of_week='0-4')
sched.add_job(workprocess,'cron',minute='00',hour='1,2,3,4,5,6,7,19,20,21,22,23,24',day_of_week='0-4')
sched.add_job(workprocess,'cron',hour='*',day_of_week='5-6')
sched.start()
