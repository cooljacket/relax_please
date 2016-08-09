#!/usr/bin/env python
# coding: utf-8
# reference: http://ju.outofmemory.cn/entry/77321
import os
import sys
import struct
import time
import multiprocessing
import threading
import subprocess


class Listener:
	def __init__(self):
		self._observers = []

	def attach(self, observer):
		if not observer in self._observers:
			self._observers.append(observer)

	def detach(self, observer):
		try:
			self._observers.remove(observer)
		except ValueError, e:
			pass

	def notify(self):
		for observer in self._observers:
			observer.update()

	def listening(self):
		pass


class KeyBoardListener(Listener):
	"""使用观察者模式来实现对键盘敲击的监听！"""
	format = "llHHI"
	size = struct.calcsize(format)
	keyboardDevice = "/dev/input/event3"
	fd = os.open(keyboardDevice, os.O_RDWR)

	# maxWorkTime，最长的工作时间，默认为一个小时
	# leastRelaxTime，最短的休息时间，默认为600秒，即十分钟
	# notifyInterval，发送提醒的间隔时间，因为太频繁发送会导致桌面混乱，所以这个需要控制！默认为1分钟提醒一次
	def __init__(self, maxWorkTime=3600, leastRelaxTime=600, notifyInterval=60):
		Listener.__init__(self)

		self.maxWorkTime = maxWorkTime
		self.leastRelaxTime = leastRelaxTime
		self.notifyInterval = notifyInterval

		self.lastInputTime = time.time()
		self.lastNotifyTime = time.time() - notifyInterval
		self.start_work_time = time.time()


	def listening(self):
		while True:
			op = os.read(self.fd, self.size)
			# timestamp, subsecond, type, code, value = struct.unpack(format, op)
			now, _, _, _, _ = struct.unpack(self.format, op)

			# 如果中间有休息过了，那么更新开始工作的时间
			if now - self.lastInputTime >= self.leastRelaxTime:
				self.start_work_time = now
			elif now - self.start_work_time >= self.maxWorkTime:
				# 如果持续工作超过指定时间段，并且距离上次提醒的时间超过设定区间，就开始发提醒！
				if now - self.lastNotifyTime >= self.notifyInterval:
					self.notify()
					self.lastNotifyTime = now
			self.lastInputTime = now


class SayGoodNightListener(Listener):
	def __init__(self, night=23, morning=5):
		Listener.__init__(self)
		self.morning = morning
		self.night = night

	def listening(self):
		while True:
			now = time.localtime(time.time())
			if now.tm_hour >= self.night or now.tm_hour <= self.morning:
				self.notify()
			time.sleep(10)


class NotificaitonSender:
	"""通过ubuntu上的nofity-send在屏幕右上角发送提醒信息"""

	def __init__(self, title, msg):
		self.title = title
		self.msg = msg

	def update(self):
		self.sendNotification(self.title, self.msg)

	def sendNotification(self, title, msg):
		# os.system('notify-send "TITLE" "MESSAGE"')
		os.system('export DISPLAY=:0.0;notify-send "{0}" "{1}"'.format(title, msg))
		with open('/tmp/lalalalala.txt', 'a') as f:
			f.write(msg + '\n')

def relaxSupervisor():
	print('relax')
	hardWorkSender = NotificaitonSender("请注意休息", "你已超负荷工作！！！必须马上停下来休息！")
	listener = KeyBoardListener(maxWorkTime=10, leastRelaxTime=10, notifyInterval=15)
	listener.attach(hardWorkSender)
	listener.listening()


def goodNightSupervisor():
	print('good night')
	goodNightSender = NotificaitonSender("晚安", "夜深了，早点睡～再不睡就真的会变丑到家了")
	listener = SayGoodNightListener()
	listener.attach(goodNightSender)
	listener.listening()


def main(args):
	print('main', args)
	# 由于在应用层里监听是阻塞操作，所以需要开多个进程
	relax = multiprocessing.Process(target=relaxSupervisor)
	goodNight = multiprocessing.Process(target=goodNightSupervisor)
	relax.start()
	goodNight.start()

	# 以下多线程版本，不过发现在终端按Ctrl+C没法中断程序，是不是没有响应SIGKILL信号呢？
	# relax = threading.Thread(target=relaxSupervisor)
	# goodNight = threading.Thread(target=goodNightSupervisor)
	# relax.start()
	# goodNight.start()
	# relax.join()
	# goodNight.join()


os.environ['DISPLAY'] = ':0.0'
main(sys.argv[1:])
