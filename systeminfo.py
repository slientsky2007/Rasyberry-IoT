#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    systeminfo
   Description :  获取系统基础信息
   Author :       Slientsky
   date：         2018-04-23
-------------------------------------------------
   Change Activity:
                   2018-04-23
-------------------------------------------------
"""

import fcntl
import struct
import os
import socket
import sys
import time
import datetime

from basicdef import BasicDef
from onenetapi import OneNetApi

try:
	import psutil
except ImportError:
	print("The psutil library was not found. Run 'sudo -H pip install psutil' to install it.")
	sys.exit()

class SystemInfo():
	def __init__(self, iface, post2OneNet):
		self.IFACE_INIT = iface
		#上一次时间间隔时网络发送总流量和接受总流量
		self.SEND_INIT = 0
		self.RECV_INIT = 0
		#当前时间间隔内的发送和接受流量(计算得到的实时网络流量)
		self.Rx = 0
		self.Tx = 0
		
		self.post2OneNet = post2OneNet
		if post2OneNet:
			self.onenet = OneNetApi()
		

	def get_RT_network_traffic(self, timesleep):
		new_recv,new_send = self.get_net_TxRx()
		self.Rx = (new_recv - self.RECV_INIT)/timesleep
		self.Tx = (new_send - self.SEND_INIT)/timesleep
		
		if self.post2OneNet:
			self.onenet.num +=1
			if self.onenet.num >= 10:
				self.onenet.set("NetTx", self.Tx)
				self.onenet.set("NetRx", self.Rx)
				r2 = self.onenet.post_data_flow()	
				self.onenet.num = 0
		
		recv_data = BasicDef.bytes2human(self.Rx)
		send_data = BasicDef.bytes2human(self.Tx)
		self.RECV_INIT = new_recv
		self.SEND_INIT = new_send
		return "Tx %s,  Rx %s" % \
				(send_data, recv_data)

	def get_net_TxRx(self):
		stat = psutil.net_io_counters(pernic=True)[self.IFACE_INIT]
		send = stat.bytes_sent
		recv = stat.bytes_recv
		return (recv, send)
	
	def get_mem_usage(self):
		usage = psutil.virtual_memory()
		return "Mem: %s %.0f%% %s free" \
			% (BasicDef.bytes2human(usage.total), usage.percent, BasicDef.bytes2human(usage.free))
					
	def getDate(self):
		dt = datetime.datetime.now()
		return dt.strftime( '%Y-%m-%d' )

	def getTime(self):
		dt = datetime.datetime.now()
		return dt.strftime( '%H:%M:%S %p' )

	def getDateTime(self):
		dt = datetime.datetime.now()
		return dt.strftime( '%x %H:%M:%S %p' )

	  
	def getIP(self):  
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
		return socket.inet_ntoa(fcntl.ioctl(   
			s.fileno(),   
			0x8915,  # SIOCGIFADDR   
			struct.pack('256s', self.IFACE_INIT[:15].encode('utf-8'))   
		)[20:24])
	


	