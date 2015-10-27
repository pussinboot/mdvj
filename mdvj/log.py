"""
lets you log what presets got activated when
hope is to be able to play back again with or without rearranging
"""
import threading, time
import tkinter as tk
from tkinter import ttk
import queue

class PresetLog:
	"""
	an entire log
	"""

	def __init__(self,title='untitled'):
		self.title = title
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
		self.fxn_called = fxn_called
		if not self.fxn_called: # in case of resume event
			self.time_int = 0
			self.fxn_called = lambda: None
		def fxn():
			self.fxn_called(*self.args)
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

	def swap_funcs(self,nother_log):
		curargs, curfun = self.args, self.fxn_called
		self.args = nother_log.args
		self.fxn_called = nother_log.fxn_called
		nother_log.args = curargs
		nother_log.fxn_called = curfun

	def redo(self):
		self.timer = threading.Timer(self.time_int,self.fxn)
		self.timer.start()

	def cancel(self):
		# stop before it's too late
		if self.timer:
			self.timer.cancel()

class LogGui:
	"""
	shows a presetlog and allows 4 manipulation of it
	new log items get added to current log and show up as rows in tree
	can be dragged up and down to switch what preset when
	can be double clicked to change time interval 
	multiple logs 4 multiple recordings, idk
	"""
	def __init__(self,master=None):
		self.master = master
		self.queue = None
		self.running = 0
		if not master:
			self.master = tk.Tk()
			self.master.wm_state('iconic')
		self.logs = [PresetLog()]
		self.current_log_index = 0
		# gui whatever
		self.win = tk.Toplevel()
		self.mainframe = tk.Frame(self.win)

		self.buttonframe = tk.Frame(self.mainframe)
		self.playpause = tk.Button(self.buttonframe,text='> ||',width=5)
		self.record = tk.Button(self.buttonframe,text='O',width=5)
		self.stop = tk.Button(self.buttonframe,text='[ ]',width=5)
		self.playpause.pack(side=tk.LEFT)
		self.record.pack(side=tk.LEFT)
		self.stop.pack()

		self.treeframe = tk.Frame(self.mainframe)
		self.tree = ttk.Treeview(self.treeframe,selectmode='browse')
		self.tree.pack(side=tk.LEFT,anchor=tk.N,fill=tk.BOTH,expand=tk.Y)
		self.ysb = ttk.Scrollbar(self.treeframe, orient='vertical', command=self.tree.yview)
		self.tree.configure(yscrollcommand=self.ysb.set)
		self.ysb.pack(side=tk.RIGHT,anchor=tk.N,fill=tk.Y)
		self.buttonframe.pack()
		self.treeframe.pack()
		self.mainframe.pack()

	def set_queue(self,queue):
		self.queue = queue

	def start(self):
		if self.queue:
			self.running = 1
			self.periodicCall()
		self.master.mainloop()

	def periodicCall(self):
		self.processIncoming()
		if not self.running:
			self.master.after_cancel(self.processIncoming)
		else:
			self.master.after(100,self.periodicCall)

	def processIncoming(self):
		"""
		Handle all the messages currently in the queue (if any).
		"""
		while self.queue.qsize():
			try:
				msg = self.queue.get(0)
				# Check contents of message and do what it says
				# As a test, we simply print it
				print( msg)
			except queue.Empty:
				pass


def main():
	# root = tk.Tk()
	# root.wm_state('iconic')
	loggui = LogGui()
	loggui.start()
	#root.mainloop()

if __name__ == '__main__':
	# test
	# logs = [None]*5
	# logs[0] = LogLine(0,print,'start')
	# for i in range(1,5):
		# logs[i] = LogLine(i*1.0,print,[i],logs[i-1])
	main()
	# logs[0].redo()