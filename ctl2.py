#!/usr/bin/python
# -*- coding: UTF-8 -*-


'''
TODO:
    1.脚本只能在部署目录启动
    update_status 的逻辑以及被调用的地方都粗糙了些：不管发送短信是不是成功，都要全部更新
'''


import socket
import log_fn
import pymysql
import time
import top.api
import logging
import sys,traceback
import configparser
import threading
import cx_Oracle as ora
from apscheduler.schedulers.blocking import  BlockingScheduler


class ctl:

    # 发送短信后更新发送状态
    def update_status(self,id,isSend):
        # Y-已调用大鱼接口,N-未发送,E-调用接口异常
        try:
            db = pymysql.connect(host,user,passwd,dbname)
            cursor = db.cursor()
            sql = "update send_message set is_send='%s' " \
                  "where is_send='N' " \
                  "and id='%s'" % (isSend,id)
            try:
                cursor.execute(sql)
                sendinfo = cursor.fetchall()
                db.commit()
                status=1
            except:
                db.rollback()
                status=2
                logging.error(traceback.print_exception(*sys.exc_info()))
        except:
            logging.error(traceback.print_exception(*sys.exc_info()))
        return status

    # 检查结果入库
    def insert_checkresult(self,ip,check_type,check_result,logging):

        insert_result=0
        try:
            db = pymysql.connect(host,user,passwd,dbname)
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
            # 如果存在异常，则写入短信表
            if any(str_ in check_result for str_ in('CRITICAL','WARNING','FAILED')):
                sql2="insert into send_message(server,check_type,check_result,check_time,is_send) values('%s','%s','%s','%s','N')" % (ip,check_type,check_result,check_time)
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
            db.close()
        except:
            logging.error(traceback.print_exception(*sys.exc_info()))
        return insert_result

    # 根据周期获取需要检查的服务器ip
    def get_checkser(self,cycle):
        try:
            db = pymysql.connect(host,user,passwd,dbname)
            cursor = db.cursor()
            sql = "select distinct server from check_server where check_cycle='%s'" % cycle
            try:
                cursor.execute(sql)
                check_ser = cursor.fetchall()
            except:
                print(traceback.print_exception(*sys.exc_info()))
            db.close()
        except:
            print(traceback.print_exception(*sys.exc_info()))
        return check_ser

    # 获取N和M级别下的未发送数据级短信内容
    def get_sendinfo(self):
        try:
            db = pymysql.connect(host,user,passwd,dbname)
            cursor = db.cursor()
            sql = "select a.id,a.check_time,server,concat(check_type,':',check_result),b.phone_no from send_message a,send_user b where a.is_send='N' and b.TYPE='N' UNION select a.id,a.check_time,a.server,concat(a.check_type,':',check_result),b.phone_no from send_message a,send_user b,check_server c where a.is_send='N' and b.TYPE='M' and a.check_type=c.check_type and a.server=c.server and c.check_level='M'"
            try:
                cursor.execute(sql)
                sendinfo = cursor.fetchall()
                return sendinfo
                logging.info(sendinfo)
            except:
                logging.error(traceback.print_exception(*sys.exc_info()))
        except:
            logging.error(traceback.print_exception(*sys.exc_info()))

    def get_checkcom(self,cycle,server,logging):
        try:
            db = pymysql.connect(host,user,passwd,dbname)
            cursor = db.cursor()
            sql = "select check_type,check_command from check_server where check_cycle='%s' and server='%s'" % (cycle,server)
            try:
                cursor.execute(sql)
                check_com = cursor.fetchall()
            except:
                logging.error(traceback.print_exception(*sys.exc_info()))
            db.close()
        except:
            print(traceback.print_exception(*sys.exc_info()))
            logging.error(traceback.print_exception(*sys.exc_info()))
        return check_com
    def exception_money(self):
        try:
            cn=ora.connect('cnolan/j0MUFPJPXu@192.168.2.188:21521/jfdb')
            cursor=cn.cursor()
            cursor.execute('''select count(1) from (select to_char(a.timestamps,'yyyy-mm-dd hh24:mi:ss')||'，客户:'||a.account_name||'，入金'||a.amount||'元，失败' result
        from cnolan.acc_fund_abnormal a where a.status in ('01','04') and a.timestamps>=sysdate-2/24 and a.timestamps<=sysdate-1/24
        union
        select to_char(b.timestamps,'yyyy-mm-dd hh24:mi:ss')||',客户:'||b.COMPANY_ACCID||'出金'||b.amount||'元，失败'
        from cnolan.acc_trdcenter_accrecord b where b.amount_status = '03' and b.timestamps>=sysdate-2/24 and b.timestamps<=sysdate-1/24
        union
        select to_char(c.withdraw_date,'yyyy-mm-dd hh24:mi:ss')||',客户:'||c.withdraw_user_name||'出金'||c.withdraw_amount||'元，失败'
        from cnolan.acc_virtual_withdraw c where c.status = '05' and c.withdraw_date>=sysdate-2/24 and c.withdraw_date<=sysdate-1/24
        union
        select t.TIMESTAMP||t.inquiryid||'' from cnolan.inquiry_request t where t.state in(80,81,82,100,101,102,103,96,97,98,99))''')
            rows=cursor.fetchall()
            a=rows[0][0]
            ip='fitc'
            check_type='money_error'
            if a==0:
                check_result='平台出入金/流程正常'
                check_time=time.strftime('%Y-%m-%d %X')
                db = pymysql.connect(host='192.168.2.197', port=3306, user='ywjk', passwd='mysql098', db='ywdb',use_unicode=1,charset='utf8')
                cursor = db.cursor()
                sql = "insert into check_result() values('%s','%s','%s','%s')" % (ip,check_type,check_result,check_time)
                cursor.execute(sql)
                db.commit()
            else:
                check_time=time.strftime('%Y-%m-%d %X')
                check_result='平台有:'+str(int(a))+'笔资金/流程异常，请检查。'
                self.insert_checkresult(ip,check_type,check_result)
                try:
                    db = pymysql.connect(host='192.168.2.197', port=3306, user='ywjk', passwd='mysql098', db='ywdb',use_unicode=1,charset='utf8')
                    cursor = db.cursor()
                    sql = "insert into send_message(server,check_type,check_result,check_time,is_send) values('SYSTEM','FITC_MONEY','%s','%s','N')" % (check_result,check_time)
                    sql2 = "insert into check_result() values('%s','%s','%s','%s')" % (ip,check_type,check_result,check_time)
                    print(sql)
                    try:
                        cursor.execute(sql)
                        cursor.execute(sql2)
                        db.commit()
                        insert_result=1
                    except:
                        db.rollback()
                        logging.error(traceback.print_exception(*sys.exc_info()))
                        insert_result=2
                    db.close()
                except:
                    logging.error(traceback.print_exception(*sys.exc_info()))
        except:
            logging.error(traceback.print_exception(*sys.exc_info()))
    def sendmessage(self,check_time,server,message,phoneno):
        req=top.api.AlibabaAliqinFcSmsNumSendRequest()
        req.set_app_info(top.appinfo('23885233','a4cc077827649ad324a6146b74ac2068'))
        req.extend="123456"
        req.sms_type="normal"
       # req.sms_free_sign_name="武汉票据交易中心"
        req.sms_free_sign_name="大鱼测试"
        #req.sms_param="{\"date\":\"check_time\",\"servicename\":\"server\",\"level\":\"message\"}"
        exec('req.sms_param="{\\"date\\":\\"'+check_time+'\\",\\"servicename\\":\\"'+server+'\\",\\"level\\":\\"'+message+'\\"}"')
        req.rec_num=phoneno
        req.sms_template_code="SMS_68035083"
        try:
            resp= req.getResponse()
            result=1
        except Exception as resp:
            resp=resp
            result=0
            logging.exception(resp)
        logging.info(resp)
        return result
    def sock_fn(self,host,command,logging):
        sk=socket.socket()
        port = 9527
        s_command=bytes(command)
        try:
            sk.connect((host,port))
            sk.send(s_command)
            result=str(sk.recv(1024))
            result=result.split('|')
            check_status=result[0]
            check_result=result[1]
            logging.info(check_status)
            logging.info(check_result)
        except:
            logging.close()
            logging.error(traceback.print_exception(*sys.exc_info()))
        sk.close()
        return check_result

    # 定时器调用
    def work_fn(self,cycle):

        ''' 关于python多线程的一些知识

        在python中，主线程结束后，会默认等待子线程结束后，主线程才退出
        python对于thread的管理中有两个函数：join和setDaemon

        join：如在一个线程B中调用threada.join()，则threada结束后，线程B才会接着threada.join()往后运行。
        setDaemon：thread.setDaemon（）设置为True, 则设为true的话 则主线程执行完毕后会将子线程回收掉,避免子线程无限死循环，导致退不出程序，也就是避免楼上说的孤儿进程。
        '''

        # 获取当前周期下需要进行检查的服务器和对应脚本
        a=self.get_checkser(cycle)
        #print(len(a))
        # 定义线程
        threads = []
        for i in a:
            ip=i[0]
            check_time=time.strftime("%Y-%m-%d %X")
            # 定义日志文件名和路径
            logging=log_fn.Logger("log"+ip+check_time+cycle, "./log/t"+ip+".log")
            # 定义记录的内容
            logging.info(ip+' '+cycle)
            # 线程实例化
            t1=threading.Thread(target=self.exec_com,args=(cycle,ip,logging))
            # 加入线程池
            threads.append(t1)
        # 设置守护线程
        for t in threads:
            t.setDaemon(True)
            t.start()
            # 设置主线程阻塞
            t.join()
            send=self.get_sendinfo()
            if len(send)==0:
                logging.error("no waring")
            else:
                for i in send:
                    id=i[0]
                    check_time=i[1]
                    server=i[2]
                    message=i[3]
                    phoneno=i[4]

                    #hwz 20180409因为发短信的时候，内容里面带有CRITICAL关键字无法发送
                    message=message.relpace('CRITICAL','')
                    try:
                        sendResult=self.sendmessage(check_time,server.replace('.','-'),message,phoneno)
                        if sendResult==1:
                            logging.info("message send complete")
                            isSend='Y'
                        else:
                            logging.info("message send failed")
                            isSend='N'
                    except:
                        logging.error("send message failed")
                        isSend='E'
                    # 更新短信表状态,逐条更新
                    self.update_status(id,isSend)
                    logging.info(check_time+','+server+','+message+','+phoneno)

                # b=self.update_status()


    def exec_com(self,cycle,i,logging):
        s_checkcm=self.get_checkcom(cycle,i,logging)
        for n in s_checkcm:
            type=n[0]
            com=n[1]
            logging.info(com)
            ex_result=self.sock_fn(i,com,logging)
            a=self.insert_checkresult(i,type,ex_result,logging)
            logging.info("check data insert database status:"+str(a))
        #print(logging.echo_h)
        logging.close()
cf = configparser.ConfigParser()
cf.read("db.conf")
host = cf.get("db", "db_host")
port = cf.getint("db", "db_port")
user = cf.get("db", "db_user")
passwd = cf.get("db", "db_pass")
dbname = cf.get("db", "db_name")
def cycle_five():
    aa=ctl()
    aa.work_fn('5')
def cycle_ten():
    aa=ctl()
    aa.work_fn('10')
def ex_money():
    aa=ctl()
    aa.exception_money()
sched = BlockingScheduler()
#sched.add_job(cycle_five,'cron',minute='*',hour='8-18',day_of_week='0-4')
sched.add_job(cycle_five,'cron',minute='05,10,15,20,25,30,35,40,45,50,55',hour='8-18',day_of_week='0-4')
sched.add_job(cycle_ten,'cron',minute='00,10,20,30,40,50',hour='8-18',day_of_week='0-4')
sched.add_job(ex_money,'cron',hour='*')
#sched.add_job(ex_money,'cron',minute='05,10,15,20,25,30,35,40,45,50,55',hour='8-18',day_of_week='0-4')
sched.start()



