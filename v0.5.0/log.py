"""
lets you log what presets got activated when
hope is to be able to play back again with or without rearranging
"""
import threading, time

class PresetLog:
	"""
	an entire log
	"""

	def __init__(self):
		self.log = []
		#self.start_time = time.time()

	def start(self):
		self.start_time = time.time()

	def add_event(self,fxn,args=[]):
		last = None
		if self.log:
			last = self.log[-1]
		self.log.append(LogLine(time.time() - self.start_time,fxn,args,last))

	def play(self):
		if self.log:
			self.log[0].redo()

	def stop(self):
		for log in self.log:
			log.cancel()
		self.start_time = time.time()

	def pause(self):
		self.add_event(lambda:print('paused'))

	def resume(self):
		self.add_event()


class LogLine:
	"""
	a single line of the log, works like a linked list
	"""

	def __init__(self,timestamp,fxn_called=None,args=[],prev_log=None):
		self.timestamp = timestamp
		self.next_log = None
		self.time_int = 0
		self.args = args
		if prev_log:
			prev_log.link_line(self)
		if not fxn_called: # in case of resume event
			self.time_int = 0
			fxn_called = lambda: None
		def fxn():
			fxn_called(*self.args)
			if self.next_log:
				self.next_log.redo()

		self.fxn = fxn

		self.timer = None

	def set_int(self,other_log):
		# may have to change this
		self.time_int = self.timestamp - other_log.timestamp 

	def link_line(self,next_log):
		next_log.set_int(self)
		self.next_log = next_log

	def redo(self):
		self.timer = threading.Timer(self.time_int,self.fxn)
		self.timer.start()

	def cancel(self):
		# stop before it's too late
		if self.timer:
			self.timer.cancel()

if __name__ == '__main__':
	# test
	logs = [None]*5
	logs[0] = LogLine(0,print,'start')
	for i in range(1,5):
		logs[i] = LogLine(i*1.0,print,[i],logs[i-1])
#
	logs[0].redo()