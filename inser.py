#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import socket
import pymysql,sys,traceback
import subprocess
def insertdata(ip,check_type,check_command):
        db=pymysql.connect(host='192.168.2.197',port=3306,user='ywjk',passwd='mysql098',db='ywdb')#杩..mysql
        try:
            cursor=db.cursor()
            sql="insert into check_server() values('%s','%s','%s','')" % (ip,check_type,check_command)
            cursor.execute(sql)
            db.commit()
            result=1
        except:
            result=2
            traceback.print_exception(*sys.exc_info())
        return result
ip=socket.gethostbyname(socket.gethostname())
f=open('/usr/local/nagios/etc/nrpe.cfg')
for line in f:
    b=[]
    #f.readlines():
    match=re.findall('^command\[',line)
    if match != []:
        line=line.replace('command[','').replace(']','').replace('\n','')
        #print(line)
        b=line.split('=')
        (theCheckStatus,theCheckOutPut) = subprocess.getstatusoutput(b[1])
        if theCheckStatus==0:
            #print("command can be exec")
            c=insertdata(ip,b[0],b[1])
            if c==1:
                print(ip+','+b[0]+','+b[1]+' insert database complete')
            else:
                print(ip+','+b[0]+','+b[1]+' insert database failed')
        else:
            print(ip+','+b[0]+','+b[1]+' command can not be exec')
    else:
        pass
