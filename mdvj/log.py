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
		self.last_ind = 0
		self.start_time = time.time()

	def start(self):
		self.start_time = time.time()
		self.add_event()

	def add_event(self,fxn=None,args=[],name=None):
		last = None
		if self.log:
			last = self.log[self.last_ind-1]
		self.log.append(LogLine(time.time() - self.start_time,self.last_ind,fxn,args,name,last))
		self.last_ind += 1

	def swap_events(self,e1,e2):
		if e1 != e2:
			# print("swapping {0} w/ {1}".format(e1,e2))
			self.log[e1].swap_funcs(self.log[e2])
		#event1.swap_funcs(event2)

	def delete_event(self,e):
		event = self.log[e]
		if event.next_log:
			event.fxn = lambda: event.next_log.redo()
			event.next_log.time_int += event.time_int
		else:
			event.fxn = lambda: None
		event.time_int = 0

	def play(self):
		if self.log:
			self.log[0].redo()

	def stop(self):
		for log in self.log[::-1]:
			if log.cancel():
				break
		self.start_time = time.time()

	def pause(self):
		self.add_event(lambda *args:print('paused'),'p/r')

	def resume(self):
		self.add_event(args='p/r')


class LogLine:
	"""
	a single line of the log, works like a linked list
	"""

	def __init__(self,timestamp,index,fxn_called=None,args=[],name=None,prev_log=None):
		self.timestamp = timestamp
		self.index = index
		self.next_log = None
		self.time_int = 0
		self.args = args
		if not name:
			self.name = str(args)
		else:
			self.name = name
		if prev_log:
			prev_log.link_line(self)
		self.fxn_called = fxn_called
		if not self.fxn_called: # in case of resume event
			self.time_int = 0
			self.fxn_called = lambda *args: None
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
			return True
		return False

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
		self.recording = 0
		if not master:
			self.master = tk.Tk()
			self.master.wm_state('iconic')

		self.logs = [PresetLog()]
		self.current_log_index = 0
		# gui whatever
		self.win = tk.Toplevel()
		self.win.title("log")
		self.mainframe = tk.Frame(self.win)

		self.buttonframe = tk.Frame(self.mainframe)
		self.playpause = tk.Button(self.buttonframe,text='>',width=5,command=self.play_recording,state='disabled')
		self.record = tk.Button(self.buttonframe,text='O',width=5,command=self.start_recording)
		self.stop = tk.Button(self.buttonframe,text='[ ]',width=5,command=self.stop_recording)
		self.playpause.pack(side=tk.LEFT)
		self.record.pack(side=tk.LEFT)
		self.stop.pack()

		self.treeframe = tk.Frame(self.mainframe)
		self.tree = ttk.Treeview(self.treeframe, columns=("col1","col2"), displaycolumns="col2", selectmode='none')
		self.tree.column("col2",width=150)
		self.tree.heading("col2",text='name')
		self.tree.heading("#0", text="time")
		self.tree.column("#0",width=50,anchor=tk.E)
		self.tree.pack(side=tk.LEFT,anchor=tk.N,fill=tk.BOTH,expand=tk.Y)
		self.ysb = ttk.Scrollbar(self.treeframe, orient='vertical', command=self.tree.yview)
		self.tree.configure(yscrollcommand=self.ysb.set)
		self.ysb.pack(side=tk.RIGHT,anchor=tk.N,fill=tk.Y)
		self.buttonframe.pack()
		self.treeframe.pack()
		self.mainframe.pack()

		self.tree.bind("<ButtonPress-1>",self.bDown)
		self.tree.bind("<ButtonRelease-1>",self.bUp, add='+')
		self.tree.bind("<B1-Motion>",self.bMove, add='+')
		#self.tree.bind("<Shift-ButtonPress-1>",self.bDown_Shift, add='+')
		#self.tree.bind("<Shift-ButtonRelease-1>",self.bUp_Shift, add='+')
		self.tree.bind('<Delete>',self.deleter)
		self.tree.bind('<Double-1>',self.time_change)
		self.tree.bind('<Return>',self.time_change)


	def add_to_log(self,fxn,args=[],name=None):
		self.logs[self.current_log_index].add_event(fxn,args,name)
		self.log_to_tree(self.logs[self.current_log_index].log[-1])

	def log_to_tree(self,logline):
		if logline.args != 'p/r':
			self.tree.insert('', 'end', text="%.2f" % logline.timestamp, values=('',logline.name,logline.index))

	def set_queue(self,queue):
		self.queue = queue

	def start(self):
		if self.queue:
			self.running = 1
			self.periodicCall()
		self.master.mainloop()

	def play_recording(self,event=None):
		self.recording = 0
		self.logs[self.current_log_index].play()

	def start_recording(self,event=None):
		self.recording = 1
		self.logs[self.current_log_index].start()
		# if not self.play_pause: # aka if paused (done playing)
		self.playpause.config(state='disabled')
		self.record.config(text='||',command=self.pause_recording)

	def stop_recording(self,event=None):
		self.recording = 0
		self.logs[self.current_log_index].stop()
		self.playpause.config(state='active')
		self.record.config(text='O',command=self.start_recording,state='active')

	def pause_recording(self,event=None):
		self.recording = 0
		self.logs[self.current_log_index].pause()
		self.playpause.config(state='active')
		self.record.config(text='0',command=self.resume_recording)

	def resume_recording(self,event=None):
		self.recoring = 1
		self.logs[self.current_log_index].resume()
		self.playpause.config(state='disabled')
		self.record.config(text='||',command=self.pause_recording)

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

	def bDown_Shift(self,event):
		tv = event.widget
		select = [tv.index(s) for s in tv.selection()]
		select.append(tv.index(tv.identify_row(event.y)))
		select.sort()
		for i in range(select[0],select[-1]+1,1):
			tv.selection_add(tv.get_children()[i])

	def bDown(self,event):
		tv = event.widget
		if tv.identify_row(event.y) not in tv.selection():
			tv.selection_set(tv.identify_row(event.y))	

	def bUp(self,event):
		tv = event.widget
		if tv.identify_row(event.y) in tv.selection():
			tv.selection_set(tv.identify_row(event.y))	

	def bUp_Shift(self,event):
		pass

	def bMove(self,event):
		tv = event.widget
		moveto = tv.identify_row(event.y) #tv.index(
		for s in tv.selection():
			oldvals = tv.item(s)['values']
			newvals = tv.item(moveto)['values']
			# if newvals and oldvals != newvals: print(oldvals,newvals)
			if newvals:
				self.logs[self.current_log_index].swap_events(oldvals[-1],newvals[-1])
				tv.item(moveto,values=('',oldvals[1],newvals[-1]))
				tv.item(s,values=('',newvals[1],oldvals[-1]))
				tv.selection_set(tv.identify_row(event.y))

	def deleter(self,event):
		tv = event.widget
		item = tv.selection()[0]
		to_delete_ind = tv.item(item)['values'][-1]
		self.logs[self.current_log_index].delete_event(to_delete_ind)
		tv.delete(item)

	def time_change(self,event):
		tv = event.widget
		if not tv.selection():
			return
		item = tv.selection()[0]
		logline = self.logs[self.current_log_index].log[tv.item(item)['values'][-1]]
		change_fun = lambda new_text : tv.item(item,text=new_text)
		start_text = tv.item(item)['text']
		popup = TimeChanger(self,logline,start_text,change_fun)

class TimeChanger:

	def __init__(self,parent,logline,start_text,change_fun):
		def int_check(S):
			if S == '.': return True # special case
			try:
				valid = int(S)
				return True
			except:
				return False


		self.parent = parent
		self.logline = logline
		self.start_text = start_text
		self.change_fun = change_fun

		self.top = tk.Toplevel(takefocus=True)
		self.top.title("edit time")
		self.frame = tk.Frame(self.top)
		self.frame.pack()

		vcmd = (self.frame.register(int_check),'%S')
		self.time_text = tk.StringVar()
		self.time_text.set(self.start_text)

		self.entry = tk.Entry(self.frame,validate='key',validatecommand=vcmd,width=5,textvariable=self.time_text)
		self.entry.pack()

		self.entry.focus()
		self.top.protocol("WM_DELETE_WINDOW",self.close_popup)
		self.top.protocol("<Escape>",self.close_popup)
		self.top.bind('<Return>',self.double_check)


	def return_check(self):
		try:
			new_time = float(self.time_text.get())
			old_time = float(self.start_text)
			delta = new_time - old_time
		except:
			return False

		if self.logline.next_log:
			if delta >= self.logline.next_log.time_int: # you can't go past next event sry
				return False
		if delta < 0 and -1 * delta >= self.logline.time_int: # you can't go before prev event
			return False

		return delta

	def double_check(self,event=None):
		delta = self.return_check()
		if not delta:
			self.time_text.set(self.start_text)
		else:
			self.close_popup()

	def close_popup(self,event=None):
		delta = self.return_check()
		if delta:
			self.logline.time_int += delta
			self.change_fun(self.time_text.get())
		self.top.destroy()



def main():
	# root = tk.Tk()
	# root.wm_state('iconic')
	loggui = LogGui()
	loggui.start_recording()
	for i in range(1,6):
		time.sleep(.2)
		loggui.add_to_log(print,[i])
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