import giantwin32 as kp # keypressing stuff
import os, configparser, win32gui
from midi_control import MidiClient

class ControlMD():
	"""
	controls milkdrop
	"""

	def __init__(self):
		print('ok')

	def select_preset(self,preset):
		self.alt_tab('MilkDrop 2')
		name = preset.name
		kp.press('l')
		kp.press('home')
		print(name)
		kp.fast_press('down_arrow',preset.n)
		kp.press('enter','esc')
		self.alt_tab('mdvj')

	def alt_tab(self,win):
		try:
			hwnd = win32gui.FindWindow(None, win)
			win32gui.SetForegroundWindow(hwnd)
		except:
			print('are you sure milkdrop is running?')
	
class Controller():
	"""
	interface through which can control md
	"""

	def __init__(self,gui):
		self.mdc = ControlMD()
		self.gui = gui

		self.master = self.gui.root
		self.quit = self.gui.quit
		self.set_queue = self.gui.set_queue
		self.processIncoming = self.gui.processIncoming

		# midi control
		self.MC = MidiClient(self,refresh_int=25) # midi thread


		self.last_pad = None # store last pad
		self.last_n = {} # store last key

		self.key_to_key = {} # midi key to keypress
		self.key_to_fun = {} # midi key to fxn call
		self.desc_to_key = {#playback
							'prev':'z',
							'play/pause':'c',
							'stop':'v',
							'next':'b',
							#preset control
							'zoom':'iI',
							'motion left/right':'[]',
							'motion up/down':'{}',
							'rotate':'<>',
							'change amplitude':'oO',
							'cycle waveform':'w',
							'scale waveform':'jJ',
							'waveform opacity':'eE',
							'brightness':'gG',
							'scale 2nd layer':'qQ',
							'flip 2nd layer':'F'}

	def midi_start(self,inp=None):
		self.MC.MC.set_inp(inp)
		def process_midi(queue):
			while self.MC.running:
				msg = self.MC.MC.test_inp()
				if msg:
					#queue.put(mg)
					if msg[0] in self.key_to_fun:
						resp = self.key_to_fun[msg[0]](msg[1])
						if resp: queue.put(resp)

		self.MC.start(process_midi)

	###
	# update gui to correspond with action

	def get_pad_container(self,lr,padno):
		if lr in [0,1] and padno in [0,1,2,3,4,5,6,7]:
			return self.gui.padgroups[lr].current_padgroup().preset_containers[padno]

	def select_pad(self,lr,padno):
		pc = self.get_pad_container(lr,padno)
		self.mdc.select_preset(pc.preset)
		self.gui.queue.put(['pad',[lr, padno]])

	def select_pad_gui(self,lr,padno):
		if self.last_pad and self.last_pad != [lr, padno]: # deselect (in gui) last pad
			lastpc = self.get_pad_container(*self.last_pad)
			if lastpc: lastpc.deselected()
			#self.gui.padgroups[self.last_pad[0]].preset_containers[self.last_pad[1]].deselected()
		pc = self.get_pad_container(lr,padno)
		if pc: 
			pc.selected()
			self.master.update_idletasks()
			self.last_pad = [lr, padno]

	def go_lr(self,lr):
		#print(lr)
		# left - lr = 0, right - lr = 1

		if lr == 0 and self.gui.padgroup_l_n > 0:
			self.gui.queue.put(['lr',lr])
			if self.last_pad: 
				self.last_pad[0] += 1
				pc = self.get_pad_container(*self.last_pad)
				if pc: self.gui.queue.put(['pad',self.last_pad])#pc.selected()

		elif lr == 1 and self.gui.padgroup_r_n < len(self.gui.db) - 1:
			self.gui.queue.put(['lr',lr])
			if self.last_pad:
				self.last_pad[0] -= 1
				pc = self.get_pad_container(*self.last_pad)
				if pc: self.gui.queue.put(['pad',self.last_pad])#pc.selected()

	### midi 
	# 3 types:
	# o - for dials where n is relative
	# s - for sliders where n is absolute but needs to be relative
	# p - for buttons where n is 1

	# other functions added in here as needed

	def setup_key(self,desc,key,type):
		set_change= ['previous set','next set']
		if type == 'o':
			self.key_to_fun[key] = lambda n: self.type_o(key,n)
		elif type == 's':
			self.key_to_fun[key] = lambda n: self.type_s(key,n)
		else:
			if desc[2:5] == 'pad':
				lr = 0
				if desc[0] == 'r': lr = 1
				padno = int(desc[-1]) - 1
				self.key_to_fun[key] = lambda n: self.type_pad(lr,padno,n)
			elif desc in set_change:
				lr = 0
				if desc == set_change[1]: lr = 1
				self.key_to_fun[key] = lambda n: self.go_lr(lr) if (n == 127) else None
			else:
				self.key_to_fun[key] = lambda n: self.type_p(key,n)

	def type_o(self,key,n):
		# can also add a stored difference in order to reset things if they get 2 crazy
		if key not in self.last_n:
			self.last_n[key] = n
		old_n = self.last_n[key]
		self.last_n[key] = n
		n = n - old_n
		self.mdc.alt_tab('MilkDrop 2')
		if n > 0:
			for _ in range(n):
				kp.typer(self.key_to_key[key][0])
		else:
			for _ in range(-1*n):
				kp.typer(self.key_to_key[key][1])
		#self.mdc.alt_tab('mdvj')

	def type_s(self,key,n):
		self.mdc.alt_tab('MilkDrop 2')
		if n > 64:
			for _ in range(128-n):
				kp.typer(self.key_to_key[key][0])
		else:
			for _ in range(n):
				kp.typer(self.key_to_key[key][1])
		#self.mdc.alt_tab('mdvj')

	def type_p(self,key,n):
		if n == 127:
			self.mdc.alt_tab('MilkDrop 2')
			kp.typer(self.key_to_key[key])
			self.mdc.alt_tab('mdvj')

	def type_pad(self,lr,pad,n):
		if n == 127:
			self.select_pad(lr,pad)
			# return ['pad',[lr, pad]]

	def load(self,fname):
		if os.path.exists(fname):
			Config = configparser.RawConfigParser()
			Config.optionxform = str 
			Config.read(fname)
			for o in Config.options('Keys'):
				try:
					key = Config.get('Keys',o)
					control_type = Config.get('Type',o)
					if key:
						if o in self.desc_to_key:
							self.key_to_key[key] = self.desc_to_key[o]
						self.setup_key(o,key,control_type)	
				except:
					print(o,'failed to load')
			# print(self.key_to_key)
			# print(self.key_to_fun)
			return int(Config.get('IO','Input ID'))


#if __name__ == '__main__':
#	Config = configparser.RawConfigParser()
#	Config.optionxform = str 
#	Config.read('Twitch.ini')
#	print(Config.options('Keys'))