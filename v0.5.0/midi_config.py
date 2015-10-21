import tkinter as tk

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

		# then presented with list of 
		# midi-key | md function
		# click the midi-key to set it with controller
		# right click to enter params urself

		# when done save to vj_config.ini
	def set_start_op(self,fun, *args):
		self.start_fun = lambda *args: fun(*args)

	def start(self):
		# if no device
		self.device_selection()
		# now start the midi thread

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
	midi_thread = MidiClient(root,config)
	config.set_MC(midi_thread.MC)
	config.set_start_op(midi_thread.start)
	config.start()
	root.mainloop()
