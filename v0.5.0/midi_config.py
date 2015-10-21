import tkinter as tk
from tkinter import ttk

from midi_control import MidiClient

class ConfigMidi:
	"""
	configure midi controls
	"""

	def __init__(self,master):
		self.master = master
		self.queue = None
		self.start_fun = lambda : None
		# first popup with selection of inputs
		# and outputs as well
		# self.start()

		# then presented with list of 
		# midi-key | md function

		# click the midi-key to set it with controller
		# right click to enter params urself

		# tk stuff
		self.nb = ttk.Notebook(self.master)
		self.nb.pack()
		# description of binds and type restrictions # these are only things that have corresponding keybinds that are sent to md
		# 'r' - relative, 'o' - on/off
		desc_type = {'prev' : 'o', 'play/pause' : 'o', 'stop' : 'o', 'next' : 'o', 
					'zoom' : 'r', 'motion left/right' : 'r', 'motion up/down' : 'r', 
					'rotate' : 'r', 'change amplitude' : 'r', 'cycle waveform' : 'o',
					'scale waveform' : 'r', 'waveform opacity' : 'r', 
					'brightness' : 'r', 'scale 2nd layer' : 'r', 'flip 2nd layer' : 'o'}
		# add clip launchers
		padz = []
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
		#for i in range(15):
		#	cl = self.config_line(self.master,self.descs[i],self.binds[i],self.control_types[i]) # create StringVar and pass it as the bind
		#	cl.pack()
		# when done save to vj_config.ini
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

	def set_start_op(self,fun, *args):
		self.start_fun = lambda *args: fun(*args)

	def start(self):
		# if no device
		self.device_selection()
		# now start the midi thread

	def config_line(self,p_frame,desc,bind,ctype,type_restrict,radio=True): #,None] # need to pass in higher level variable fxns otherwise will have weird as behavior
		"""
		little box that has desc & box for midi bind
		"""
		ctype.set('p')
		topframe = tk.Frame(p_frame,bd=1, relief=tk.SUNKEN,padx=2,pady=2)
		line_frame = tk.Frame(topframe)

		label_1 = tk.Label(line_frame,textvariable=bind,bd=2,relief=tk.RAISED,width=10)
		desc = tk.Label(line_frame,text=desc,bd=2,relief=tk.GROOVE,width=15)
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
		desc.pack()
		line_frame.pack(side=tk.TOP,expand=True,fill=tk.X)

		topframe.pack()
		label_1.bind('<ButtonPress>',self.spit_vals)
		return line_frame


	def device_selection(self):
		device_dict = self.MC.collect_device_info()
		inputs = [key for key in device_dict[0]]
		outputs = [key for key in device_dict[1]]
		device_select = tk.Toplevel()
		device_select.title('select midi devices')
		#device_select.focus_force()

		device_select_frame = tk.Frame(device_select)
		ok_frame = tk.Frame(device_select)

		input_label = tk.Label(device_select_frame,text='input')
		output_label = tk.Label(device_select_frame,text='output')

		input_choice = tk.StringVar()
		input_choice.set('-')
		output_choice = tk.StringVar()
		output_choice.set('-')

		input_select = tk.OptionMenu(device_select_frame,input_choice,*inputs)
		output_select = tk.OptionMenu(device_select_frame,output_choice,*outputs)

		def return_vals():
			choices = [input_choice.get(),output_choice.get()]
			tor = [None, None]
			if choices[0] in inputs:
				tor[0] = device_dict[0][choices[0]]			
			if choices[1] in outputs:
				tor[1] = device_dict[1][choices[1]]
			device_select.destroy()
			self.master.focus_force()
			#return tor # this wont work..
			print(tor)
			self.MC.set_inp(tor[0])
			self.start_fun()


		device_select.protocol("WM_DELETE_WINDOW",return_vals)

		ok_button = tk.Button(ok_frame,text='OK',command=return_vals)
		ok_button.pack()

		input_label.grid(row=0,column=0)
		output_label.grid(row=0,column=1)
		input_select.grid(row=1,column=0)
		output_select.grid(row=1,column=1)

		device_select_frame.pack()
		ok_frame.pack()

	def set_queue(self,queue):
		self.queue = queue

	def set_MC(self,MC):
		self.MC = MC

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

if __name__ == '__main__':
	root = tk.Tk()
	config = ConfigMidi(root)
	#midi_thread = MidiClient(root,config)
	#config.set_MC(midi_thread.MC)
	#config.set_start_op(midi_thread.start)
	#config.start()
	root.mainloop()
