import giantwin32 as kp # keypressing stuff
import win32api
import win32con
import win32gui

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
		self.lastpad = None

	def get_pad_container(self,lr,padno):
		if lr in [0,1] and padno in [0,1,2,3,4,5,6,7]:
			return self.gui.padgroups[lr].preset_containers[padno]

	def select_pad(self,lr,padno):
		if self.lastpad and self.lastpad != [lr, padno]: # deselect (in gui) last pad
			lastpc = self.get_pad_container(*self.lastpad)
			if lastpc: lastpc.deselected()
			#self.gui.padgroups[self.lastpad[0]].preset_containers[self.lastpad[1]].deselected()
		pc = self.get_pad_container(lr,padno)
		if pc: 
			pc.selected()
			self.mdc.select_preset(pc.preset)
			self.lastpad = [lr, padno]

	def go_lr(self,lr):
		# left - lr = 0, right - lr = 1
		if lr == 0 and self.gui.padgroup_l_n > 0:
			self.lastpad[0] += 1
			pc = self.get_pad_container(*self.lastpad)
			if pc: pc.selected()

		elif lr == 1 and self.gui.padgroup_r_n < len(self.gui.db) - 1:
			self.lastpad[0] -= 1
			pc = self.get_pad_container(*self.lastpad)
			if pc: pc.selected()		