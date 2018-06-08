#!/usr/bin/python2
# -*- coding: UTF-8 -*-

'''
客户端启动，从服务端获取配置并执行(日志监控只用获取一次)
    在客户端前面加一层缓存服务？

只能在部署目录启动--由于配置文件的关系
为了不发短信而将ctl2杀掉的话，db将不会再记录期间的告警信息，需要改进：支持屏蔽告警，但仍需收集数据
匹配与排除配置化

未来的设计是，服务端配置管理与短信发送是不同服务，互不影响


1.部署到生产，双轨，并验证新方案的及时性
2.
'''

import subprocess
import socket
import logging
import configparser
import pymysql
import threading
# import sys,traceback
import time
import top.api
import test
import re


# cf = configparser.ConfigParser()
# cf.read("db.conf")
# host = cf.get("db", "db_host")
# port = cf.getint("db", "db_port")
# user = cf.get("db", "db_user")
# passwd = cf.get("db", "db_pass")
# dbname = cf.get("db", "db_name")



class a:
    def __init__(self):
        pass
    def clientListener(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='monitor.log',
                            filemode='a')
        socketlink =socket.socket()
        host = socket.gethostname()
        port = 9527
        socketlink.bind((host,port))
        socketlink.listen(9)
        while True:
            controller,addr = socketlink.accept()
            command = str(controller.recv(1024),encoding='utf-8')
            print(command)
            logging.info(command)
            if command=='5':
                theCheckStatus='check5'
            elif command=='10':
                theCheckStatus='check10'
            (theCheckStatus,check_result) = subprocess.getstatusoutput(command)
            # print(theCheckStatus,check_result)
            # logging.info(theCheckStatus)
            # logging.info(check_result)
            msg=str(theCheckStatus)+'|'+check_result
            s_msg = bytes(str(msg),encoding='utf-8')
            controller.send(s_msg)

    # def logMonitor(self,logfile):
    #     while True:
    #         # controller,addr = socketlink.accept()
    #         # 接收日志文件绝对路径
    #         # command = 'tail -f '+str(controller.recv(1024),encoding='utf-8')
    #
    #         # logfile='access.log'
    #         # command='tail -f '+logfile+'|grep timeout'
    #         command='tail -f '+logfile
    #         print(command)
    #         popen=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    #         while True:
    #             line=str(popen.stdout.readline().strip(), encoding = "utf-8")
    #             # 不区分大小写，统一用小写匹配
    #             lowerLine=line.lower()
    #             print(lowerLine)
    #             # if line.find("timeout") <> -1 :
    #             if "timeout" in lowerLine :
    #                 print('get it')
    #                 check_time=time.strftime("%Y-%m-%d %X")
    #                 server='192.168.2.22'
    #                 message='日志'+logfile+'异常'
    #                 phoneno='15871465381'
    #                 self.sendmessage(check_time,server,message,phoneno)
    #             # print(type(line))

    def parallelWorker(self):

        ''' 关于python多线程的一些知识

        在python中，主线程结束后，会默认等待子线程结束后，主线程才退出
        python对于thread的管理中有两个函数：join和setDaemon

        join：如在一个线程B中调用threada.join()，则threada结束后，线程B才会接着threada.join()往后运行。
        setDaemon：thread.setDaemon（）设置为True, 则设为true的话 则主线程执行完毕后会将子线程回收掉,避免子线程无限死循环，导致退不出程序，也就是避免楼上说的孤儿进程。
        '''

        # 获取当前周期下需要进行检查的服务器和对应脚本
        # a=self.get_checkser(cycle)
        #print(len(a))
        # 定义线程
        threads = []
        a = ['/root/python_project/hwz/Monitor/access.log','/root/python_project/hwz/Monitor/httpd.log',]
        for i in a:
            # 线程实例化
            t1=threading.Thread(target=self.logMonitor,args=(i,))
            # 加入线程池
            threads.append(t1)

        # 设置守护线程
        for t in threads:
            # t.setDaemon(True)
            t.start()
            # 设置主线程阻塞
            # t.join()

    # def getLogKeyWord(self):
    #     # 打开数据库连接
    #     db = pymysql.connect(host,user,passwd,dbname)
    #     # 使用cursor()方法获取操作游标
    #     cursor = db.cursor()
    #     # SQL 插入语句
    #     sql = """select ip,port,alias from rel_servers
    #              where ip='%s'""" % (self.ip)
    #     try:
    #         # 执行sql语句
    #         cursor.execute(sql)
    #         # 获取所有记录列表
    #         results = cursor.fetchall()
    #         for row in results:
    #             id = row[0]
    #             ip = row[1]
    #             port = row[2]
    #             # 打印结果
    #             print ("ip=%s,port=%d,alias=%s" % (id, ip, port))
    #         # 提交到数据库执行
    #         db.commit()
    #     except Exception as e:
    #        # Rollback in case there is any error
    #        #print 'str(e):\t\t', str(e)
    #        print (str(e))
    #        db.rollback()
    #     # 关闭数据库连接
    #     db.close()

    def logMonitor(self,logfile):
        # logfile 需要绝对路径
        while True:
            # controller,addr = socketlink.accept()
            # 接收日志文件绝对路径
            # command = 'tail -f '+str(controller.recv(1024),encoding='utf-8')

            # logfile='access.log'
            # command='tail -f '+logfile+'|grep timeout'
            command='tail -f '+logfile
            print(command)
            popen=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            while True:
                # line=str(popen.stdout.readline().strip(), encoding = "utf-8")
                # 不区分大小写，统一用小写匹配
                line=str(popen.stdout.readline().strip()).encode('utf-8').lower()
                print(line)
                # if line.find("timeout") <> -1 :
                regexStr=re.compile('(.*(?!basename).*)')
                result = regexStr.finditer(line)
                for m in result:
                    print(m.group())

                if "exception" in line :
                    print('get it')
                    check_time=time.strftime("%Y-%m-%d %X")
                    server='192-168-2-85'  # 这里不能用.来间隔
                    # message需要定制一下，日志需要一个别名
                    message='日志'+logfile+'异常'
                    phoneno='15871465381'
                    # self.sendmessage(check_time,server,message,phoneno)
                # print(type(line))

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
            print resp
        except Exception as resp:
            resp=resp
            result=0
            print resp
        # logging.info(resp)
        print result
        return result
# # 检查结果入库
#     def insert_checkresult(self,ip,check_type,check_result,logging):
#
#         insert_result=0
#         try:
#             db = pymysql.connect(host,user,passwd,dbname)
#             cursor = db.cursor()
#             check_time=time.strftime("%Y-%m-%d %X")
#             sql = "insert into check_result() values('%s','%s','%s','%s')" % (ip,check_type,check_result,check_time)
#             try:
#                 cursor.execute(sql)
#                 db.commit()
#                 insert_result=1
#             except:
#                 db.rollback()
#                 logging.error(traceback.print_exception(*sys.exc_info()))
#                 insert_result=2
#             # 如果存在异常，则写入短信表
#             if any(str_ in check_result for str_ in('CRITICAL','WARNING','FAILED')):
#                 sql2="insert into send_message() values('%s','%s','%s','%s','N')" % (ip,check_type,check_result,check_time)
#                 try:
#                     cursor.execute(sql2)
#                     db.commit()
#                     insert_result=1
#                 except:
#                     db.rollback()
#                     logging.error(traceback.print_exception(*sys.exc_info()))
#                     insert_result=2
#             else:
#                 pass
#             db.close()
#         except:
#             logging.error(traceback.print_exception(*sys.exc_info()))
#         return insert_result

    # def getMonitorConf(self):
    #     #第一版从数据库获取配置信息，计划第二版使用缓存
    #
    #     db = pymysql.connect(host,user,passwd,dbname)
    #     cursor = db.cursor()
    #     sql = """select * from check_server
    #              where server='%s'
    #              and check_type='%s'
    #              and check_command='%s' """ % (server,
    #                                            check_type,
    #                                            check_conmmad)
    #     try:
    #         cursor.execute(sql)
    #         results = cursor.fetchall()
    #         for row in results:
    #             name = row[0]
    #             phone = row[1]
    #             type = row[2]
    #             print ("姓名=%s,电话=%s,类型=%s" % (name, phone, type))
    #         db.commit()
    #     except:
    #         db.rollback()
    #         # logging.error(traceback.print_exception(*sys.exc_info()))
    #     db.close()
    #     print results
    #     return results

#实例化
t=a()
#启动监听进程
# t.clientListener()
#启动日志监控
# t.logMonitor()
t.parallelWorker()
# t.sendmessage('','','',15871465381)
# t.getSrvConf()