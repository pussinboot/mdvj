import tkinter as tk
from tkinter import ttk
import os, configparser

from midi_control import MidiClient, MidiControl

class ConfigMidi:
	"""
	configure midi controls
	"""

	def __init__(self,frame=None):
		if not frame:
			self.master = tk.Tk()
			self.master.wm_state('iconic')
		else:
			self.master = frame
		self.queue = None
		self.midi_started = False
		self.input_storage = None
		#if not MC:
		self.MC = MidiControl()
		#else:
		#	self.MC = MC
		# tk stuff
		self.nb = ttk.Notebook(self.master)
		self.nb.pack()

		self.nb.bind_all('<<NotebookTabChanged>>',lambda event: self.master.update())
		# description of binds and type restrictions # these are only things that have corresponding keybinds that are sent to md
		# 'r' - relative, 'o' - on/off
		desc_type = {'prev' : 'o', 'play/pause' : 'o', 'stop' : 'o', 'next' : 'o', 
					'zoom' : 'r', 'motion left/right' : 'r', 'motion up/down' : 'r', 
					'rotate' : 'r', 'change amplitude' : 'r', 'cycle waveform' : 'o',
					'scale waveform' : 'r', 'waveform opacity' : 'r', 
					'brightness' : 'r', 'scale 2nd layer' : 'r', 'flip 2nd layer' : 'o'}
		# add clip launchers
		padz = ['previous set','next set']
		for n in range(1,9):
			for lr in ['l','r']:
				padz.append("{} pad #{}".format(lr,n)) #= 'o'
		for p in padz:
			desc_type[p] = 'o'
		self.dict = {}
		for key in desc_type:
			# whats gna be the bind, the control type (relative can b scroll wheel or slider), what sort of restriction
			self.dict[key] = [tk.StringVar(),tk.StringVar(),desc_type[key]]
		
		# playback
		pkeys = [ 'play/pause', 'stop', 'prev', 'next'] + padz
		self.p_page = self.nb_page(pkeys,False)
		self.nb.add(self.p_page,text='playback')
		ckeys = ['zoom', 'rotate', 'motion left/right', 'motion up/down', 'change amplitude', 'cycle waveform',	'scale waveform', 'waveform opacity', 'scale 2nd layer', 'flip 2nd layer', 'brightness']
		self.c_page = self.nb_page(ckeys)
		self.nb.add(self.c_page,text='preset control')
		
		self.start()
		# first popup with selection of inputs
		# and outputs as well
		#self.start()
		# then presented with list of 
		# midi-key | md function

		# click the midi-key to set it with controller
		# right click to enter params urself # nah

		# when done save to vj_config.ini
		#self.master.protocol("WM_DELETE_WINDOW",self.quit)
	def nb_page(self,keys,radio=True):
		tor = ttk.Frame(self.nb)
		subframes = [tk.Frame(tor),tk.Frame(tor)]
		subframes[0].pack(side=tk.LEFT,anchor=tk.N)
		subframes[1].pack(side=tk.RIGHT, anchor=tk.N)
		counter = 0
		for k in keys:
			self.config_line(subframes[counter % 2],k,self.dict[k][0],self.dict[k][1],self.dict[k][2],radio)
			counter += 1
		return tor

	def spit_vals(self,event):
		for key in self.dict:
			print(key,self.dict[key][0].get(),self.dict[key][1].get())

	def start(self):
		# if no device
		device_select = DeviceSelect(self)
		#device_select.focus_force()
		self.master.mainloop()
		# now start the midi thread

	def config_line(self,p_frame,desc,bind,ctype,type_restrict,radio=True): #,None] # need to pass in higher level variable fxns otherwise will have weird as behavior
		"""
		little box that has desc & box for midi bind
		"""
		ctype.set('p')
		topframe = tk.Frame(p_frame,bd=1, relief=tk.SUNKEN,padx=2,pady=2)
		line_frame = tk.Frame(topframe)

		label_1 = tk.Label(line_frame,textvariable=bind,bd=2,relief=tk.RAISED,width=10)
		desc_label = tk.Label(line_frame,text=desc,bd=2,relief=tk.GROOVE,width=16)
		# bind each label to midi classifier function that will set bind to proper key or whatever
		if radio:
			radio_but_frame = tk.Frame(topframe)

			b1 = tk.Radiobutton(radio_but_frame,text='O',variable=ctype,value='o')
			b2 = tk.Radiobutton(radio_but_frame,text='-|-',variable=ctype,value='s')
			b3 = tk.Radiobutton(radio_but_frame,text='01',variable=ctype,value='p')
			b3.select()
			b1.pack(side=tk.LEFT)
			b2.pack(side=tk.LEFT)
			b3.pack()

			if type_restrict == 'o':
				b1.config(state='disabled')
				b2.config(state='disabled')
				
			elif type_restrict == 'r':
				b3.config(state='disabled')

			radio_but_frame.pack(side=tk.BOTTOM)
		# make sure if u dont want radio that only piano type is possible

		label_1.pack(side=tk.LEFT,fill=tk.X)
		desc_label.pack()
		line_frame.pack(side=tk.TOP,expand=True,fill=tk.X)

		topframe.pack()
		label_1.bind('<ButtonPress>',lambda event, arg=desc: self.id_midi(arg))
		return line_frame

	def set_queue(self,queue):
		self.queue = queue

		

	def processIncoming(self):
		pass
		# """
		# Handle all the messages currently in the queue (if any).
		# """
		# while self.queue.qsize():
		# 	try:
		# 		msg = self.queue.get(0)
		# 		# Check contents of message and do what it says
		# 		# As a test, we simply print it
		# 		print( msg)
		# 	except queue.Empty:
		# 		pass

	def id_midi(self,key_to_bind):
		# find most common key, look @ ns, figure out wat kind of key it is : )
		msgs = []
		while self.queue.qsize():
			try:
				msg = self.queue.get(0)
				# Check contents of message and do what it says
				# As a test, we simply print it
				msgs.append(msg)
			except queue.Empty:
				pass
		msgs = msgs[-10:]
		#print(key_to_bind,'\n',msgs)
		f=lambda s,d={}:([d.__setitem__(i[0],d.get(i[0],0)+1) for i in s],d)[-1]
		hist = f(msgs)
		#print(f(msgs))
		def keywithmaxval(d):
			v=list(d.values())
			k=list(d.keys())
			return k[v.index(max(v))]
		#print("max",keywithmaxval(f(msgs)))
		if hist:
			maxval = keywithmaxval(hist)
			self.dict[key_to_bind][0].set(maxval)
			if self.dict[key_to_bind][2] == 'o':
				self.dict[key_to_bind][1].set('p') # piano
				return
			ns = [msgs[i][1] for i, x in enumerate(msgs) if x[0] == maxval]
			f=lambda s,d={}:([d.__setitem__(i,d.get(i,0)+1) for i in s],d)[-1]
			hist_ns = f(ns)
			if len(hist_ns) > 2:
				self.dict[key_to_bind][1].set('o')
			else:
				self.dict[key_to_bind][1].set('s')
			return

	def load(self,fname='vj_config.ini'):
		if os.path.exists(fname):
			Config = configparser.RawConfigParser()
			Config.optionxform = str 
			Config.read(fname)
			for o in self.dict:
				try:
					key = Config.get('Keys',o)
	
					control_type = Config.get('Type',o)
					self.dict[o][0].set(key)
					self.dict[o][1].set(control_type)
				except:
					print(o,'failed to load')
			return int(Config.get('IO','Input ID'))

	def save(self):
		if not self.input_storage[0] or self.input_storage[0] == '-':
			return
		fname = self.input_storage[0]+'.ini'

		Config = configparser.RawConfigParser()
		Config.optionxform = str 
		cfgfile = open(fname,'w')
		if not Config.has_section('IO'):
			Config.add_section('IO')
		Config.set('IO','Input Name',self.input_storage[0])
		Config.set('IO','Input ID',self.input_storage[1])
		keyname = "Keys"
		typename = "Type"
		if not Config.has_section(keyname):  
			Config.add_section(keyname)
		if not Config.has_section(typename):  
			Config.add_section(typename)
		for k in self.dict:
			Config.set(keyname,k,self.dict[k][0].get())
			Config.set(typename,k,self.dict[k][1].get())
		Config.write(cfgfile)
		cfgfile.close()

	def quit(self):
		self.save()
		#self.master.destroy()
class DeviceSelect:
	def __init__(self,parent):
		self.parent = parent
		self.device_dict = self.parent.MC.collect_device_info()
		self.inputs = [key for key in self.device_dict[0]]
		self.outputs = [key for key in self.device_dict[1]]
		self.device_select = tk.Toplevel(takefocus=True)
		self.device_select.title('select midi devices')
		#device_select.focus_force()

		self.device_select_frame = tk.Frame(self.device_select)
		self.ok_frame = tk.Frame(self.device_select)

		self.input_label = tk.Label(self.device_select_frame,text='input')
		self.output_label = tk.Label(self.device_select_frame,text='output')

		self.input_choice = tk.StringVar()
		self.input_choice.set('-')
		self.output_choice = tk.StringVar()
		self.output_choice.set('-')

		self.input_select = tk.OptionMenu(self.device_select_frame,self.input_choice,*self.inputs)
		self.output_select = tk.OptionMenu(self.device_select_frame,self.output_choice,*self.outputs)

		self.device_select.protocol("WM_DELETE_WINDOW",self.return_vals)

		self.ok_button = tk.Button(self.ok_frame,text='OK',command=self.return_vals)
		self.ok_button.pack()

		self.input_label.grid(row=0,column=0)
		self.output_label.grid(row=0,column=1)
		self.input_select.grid(row=1,column=0)
		self.output_select.grid(row=1,column=1)

		self.device_select_frame.pack()
		self.ok_frame.pack()
		self.device_select.mainloop()
		#return device_select

	def return_vals(self):
		choices = [self.input_choice.get(),self.output_choice.get()]
		tor = [None, None]
		if choices[0] in self.inputs:
			tor[0] = self.device_dict[0][choices[0]]			
		if choices[1] in self.outputs:
			tor[1] = self.device_dict[1][choices[1]]
		self.device_select.destroy()
		self.parent.load(choices[0]+'.ini')
		self.parent.master.wm_state('normal')
		self.parent.input_storage = [choices[0], str(tor[0])]
		self.parent.MC.set_inp(tor[0])
		self.parent.midi_started = True
		self.parent.midi_thread = MidiClient(self.parent,self.parent.MC,250)
		self.parent.queue = self.parent.midi_thread.queue
		self.parent.midi_thread.start()
		#self.parent.master.update()

def main():
	config = ConfigMidi()
	#return config.input_storage


if __name__ == '__main__':
	main()
