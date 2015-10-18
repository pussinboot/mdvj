import giantwin32 as kp # keypressing stuff
import win32api
import win32con
import win32gui

class ControlMD():

	def __init__(self):
		print('ok')

	def select_preset(self,preset):
		self.alt_tab('MilkDrop 2')
		name = preset.name
		kp.press('l')
		kp.press('home')
		#print(name)
		kp.fast_press('down_arrow',preset.n)
		kp.press('enter','esc')
		self.alt_tab('mdvj')

	def alt_tab(self,win):
		try:
			hwnd = win32gui.FindWindow(None, win)
			win32gui.SetForegroundWindow(hwnd)
		except:
			print('are you sure milkdrop is running?')
	
