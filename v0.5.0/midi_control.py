"""
provides midi interface, and a way to use it as a seperate thread
to use thread
create gui object w/ set_queue and processIncoming fxns
pass it to new ThreadedClient object
then can run .start()
then can do mainloop or whatever else
"""

import pygame.midi

import threading
import queue

class MidiControl:
	def __init__(self):
		pygame.midi.init()
		self.inp = None #pygame.midi.Input(pygame.midi.get_default_input_id())

	def set_inp(self,inp):
		try:
			self.inp = pygame.midi.Input(inp)
		except:
			self.inp = pygame.midi.Input(pygame.midi.get_default_input_id())

	def collect_device_info(self): # using this can construct list of inputs/outputs and have their corresponding channels
		inputs = {}
		outputs = {}
		i = res = 0
		while True:
			res = pygame.midi.get_device_info(i)
			if res is None: break
			to_add = str(res[1])[2:-1]
			if res[2] == 1:
				inputs[to_add] = i
			else:
				outputs[to_add] = i
			i += 1
		return [inputs,outputs]

	def quit(self):
		# self.out.close()
		try:
			self.inp.close()
			pygame.midi.quit()
		except:
			pass

	def test_inp(self):
		#while True:
		if self.inp.poll():
			midi_events = self.inp.read(10)
			the_key = str([midi_events[0][0][0],midi_events[0][0][1]])
			n = int(midi_events[0][0][2])
			#print(the_key,n)
			return (the_key,n)

class MidiClient:
	"""
	Launch the main part of the GUI and the worker thread. periodicCall and
	endApplication could reside in the GUI part, but putting them here
	means that you have all the thread controls in a single place.
	"""
	def __init__(self, gui, mc=None, refresh_int=25):
		"""
		Start the GUI and the asynchronous threads. We are in the main
		(original) thread of the application, which will later be used by
		the GUI. We spawn a new thread for the worker.
		"""
		self.refresh_int = refresh_int
		if not mc:
			self.MC = MidiControl()
		else:
			self.MC = mc
		# Create the queue
		self.queue = queue.Queue()

		# Set up the GUI part
		self.gui = gui # setup elsewhere, needs to have a set_queue fxn and a processIncoming fxn
		self.gui.set_queue(self.queue)
		


	def start(self,action=None):
		if not action:
			action = self.workerThread1
		self.gui.master.protocol("WM_DELETE_WINDOW",self.endApplication)
		# Set up the thread to do asynchronous I/O
		# More can be made if necessary
		self.running = 1
		self.thread = threading.Thread(target=action,args=(self.queue,))
		self.thread.setDaemon(True)
		self.thread.start()
		
		# Start the periodic call in the GUI to check if the queue contains
		# anything
		self.periodicCall()

	def periodicCall(self):
		"""
		Check every 100 ms if there is something new in the queue.
		"""
		self.gui.processIncoming()
		if not self.running:
			# maybe gui.quit
			self.MC.quit()
			self.gui.quit()
			self.gui.master.destroy()
		self.gui.master.after(self.refresh_int, self.periodicCall)

	def workerThread1(self,queue):
		"""
		This is where we handle the asynchronous I/O. For example, it may be
		a 'select()'.
		One important thing to remember is that the thread has to yield
		control.
		"""
		while self.running:
			# To simulate asynchronous I/O, we create a random number at
			# random intervals. Replace the following 2 lines with the real
			# thing.
			
			msg = self.MC.test_inp()
			if msg:
				queue.put(msg)

	def endApplication(self):
		self.running = 0

class GuiEx:

	def __init__(self,master):
		self.master = master
		self.queue = None

	def set_queue(self,queue):
		self.queue = queue

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
	MC = MidiControl()
	test_d = MC.collect_device_info()
	print('inputs',test_d[0])
	print('outputs',test_d[1])
	print((pygame.midi.get_default_input_id()))
	MC.set_inp(1)
	MC.quit()
	#import tkinter as tk
	#root = tk.Tk()
#
	#test_gui = GuiEx(root)
	#test_client = MidiClient(root,test_gui)
	#test_client.start()
	#root.mainloop()