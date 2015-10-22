import giantwin32 as kp # keypressing stuff
import os, configparser

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

	def __init__(self,gui,MC=None):
		self.mdc = ControlMD()
		self.gui = gui
		self.MC = MC # midi thread
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
							'zoom in / zoom out':'iI',
							'push motion left/right':'[]',
							'push motion up/down':'{}',
							'rotate left/rotate right':'<>',
							'shrink/grow amplitude of warp':'oO',
							'cycle waveform':'w',
							'scale waveform down/up':'jJ',
							'make the waveform more transparent/solid':'eE',
							'decrease/increase brightness':'gG',
							'scale 2nd graphics layer down/up':'qQ',
							'flip 2nd graphics layer (cycle)':'F'}

	def get_pad_container(self,lr,padno):
		if lr in [0,1] and padno in [0,1,2,3,4,5,6,7]:
			return self.gui.padgroups[lr].preset_containers[padno]

	def select_pad(self,lr,padno):
		if self.last_pad and self.last_pad != [lr, padno]: # deselect (in gui) last pad
			lastpc = self.get_pad_container(*self.last_pad)
			if lastpc: lastpc.deselected()
			#self.gui.padgroups[self.last_pad[0]].preset_containers[self.last_pad[1]].deselected()
		pc = self.get_pad_container(lr,padno)
		if pc: 
			pc.selected()
			self.mdc.select_preset(pc.preset)
			self.last_pad = [lr, padno]

	def go_lr(self,lr):
		# left - lr = 0, right - lr = 1
		if lr == 0 and self.gui.padgroup_l_n > 0:
			self.last_pad[0] += 1
			pc = self.get_pad_container(*self.last_pad)
			if pc: pc.selected()

		elif lr == 1 and self.gui.padgroup_r_n < len(self.gui.db) - 1:
			self.last_pad[0] -= 1
			pc = self.get_pad_container(*self.last_pad)
			if pc: pc.selected()		

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
				kp.typer(key_to_key[key][0])
		else:
			for _ in range(-1*n):
				kp.typer(key_to_key[key][1])
		self.mdc.alt_tab('mdvj')

	def type_s(self,key,n):
		self.mdc.alt_tab('MilkDrop 2')
		if n > 64:
			for _ in range(128-n):
				kp.typer(key_to_key[key][0])
		else:
			for _ in range(n):
				kp.typer(key_to_key[key][1])
		self.mdc.alt_tab('mdvj')

	def type_p(self,key,n):
		if n == 127:
			self.mdc.alt_tab('MilkDrop 2')
			kp.typer(self.key_to_key[key])
			self.mdc.alt_tab('mdvj')

	def type_pad(self,lr,pad,n):
		if n == 127:
			self.select_pad(lr,pad)

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