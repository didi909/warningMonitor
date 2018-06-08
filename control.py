#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket


# def sock_fn(self,host,log_path,logging):
def sock_fn(host,log_path):
    sk=socket.socket()
    port = 9527
    s_command=bytes(log_path, encoding = "utf8")

    sk.connect((host,port))
    sk.send(s_command)
    result=str(sk.recv(1024))
    result=result.split('|')
    check_status=result[0]
    check_result=result[1]
    sk.close()
    return check_result

sock_fn('192.168.1.62','/root/python_project/hwz/Monitor/access.log')