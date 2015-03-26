# NEEDS TO BE REWRITTEN SO THAT
# when creating database rite
# first setup press any button to take screenshot and it'll save ^^
import os, time
from PIL import Image
from tkinter import Tk, filedialog, messagebox
import glob
import win32api
import win32con
import win32gui
import configparser
from mdvj.mbox import MessageBox
import win32ui
from ctypes import windll

vjmode = True
class Screenshot():
	def __init__(self):
		self.root = Tk()
		self.root.withdraw()
		self.t = filedialog.askdirectory(initialdir="C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets",mustexist=True)
		self.tl = len(self.t)
		self.file_list = glob.glob(self.t + "/*.milk")
		self.i = 0
		self.data = {}
		#self.mbox("select the first preset in the directory. after you hit ok select the milkdrop window"r)

	def get_dir(self):
		return self.t

	def start(self):
		messagebox.showwarning("get ready", "make sure to select the first preset in the directory.")
		self.alt_tab()
		time.sleep(1)


	def advance(self):
		if self.i == 0: 
			# sequential order (r) 0x52 & scroll lock
			self.control()
			win32api.keybd_event(0x52, 0,0,0)
			win32api.keybd_event(0x52,0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(0x91, 0,0,0)
			win32api.keybd_event(0x91,0 ,win32con.KEYEVENTF_KEYUP ,0)
		if self.i == len(self.file_list): # finish
			self.save_data()
			return False
		self.data[self.file_list[self.i][self.tl+1:-5]] = self.mbox('description?',entry=True)
		#self.alt_tab()
		self.save_screen("scrot" + self.file_list[self.i][self.tl:-5] + '.png')
		#print(self.data[self.file_list[self.i][self.tl:-5]])
		self.i += 1
		# send h
		self.control()
		
		win32api.keybd_event(0x48, 0,0,0)
		win32api.keybd_event(0x48,0 ,win32con.KEYEVENTF_KEYUP ,0)	
		return True

	def alt_tab(self):
		try:
			hwnd = win32gui.FindWindow(None, 'MilkDrop 2')
			win32gui.SetForegroundWindow(hwnd)
		except:
			print('are you sure milkdrop is running?')
			exit()

	def control(self):
		if vjmode:
			try:
				hwnd = win32gui.FindWindow(None, 'MilkDrop Console [VJ Mode]')
				win32gui.SetForegroundWindow(hwnd)
			except:
				vjmode = False
	
	def save_screen(self,filename):
		hwnd = win32gui.FindWindow(None, 'MilkDrop 2')
		wDC = win32gui.GetWindowDC(hwnd)
		left, top, right, bot = win32gui.GetWindowRect(hwnd)
		w = right - left
		h = bot - top
		dcObj=win32ui.CreateDCFromHandle(wDC)
		cDC=dcObj.CreateCompatibleDC()
		dataBitMap = win32ui.CreateBitmap()
		dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
		cDC.SelectObject(dataBitMap)
		cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)
		dataBitMap.SaveBitmapFile(cDC, filename)
		# Free Resources
		dcObj.DeleteDC()
		cDC.DeleteDC()
		win32gui.ReleaseDC(hwnd, wDC)
		win32gui.DeleteObject(dataBitMap.GetHandle())

	def mbox(self,msg, b1='OK', b2='Cancel', frame=True, t=False, entry=False):
		self.msgbox = MessageBox(msg, b1, b2, frame, t, entry)
		self.msgbox.root.mainloop()
		# the function pauses here until the mainloop is quit
		self.msgbox.root.destroy()
		return self.msgbox.returning

	def save_data(self):
		Config = configparser.RawConfigParser()
		Config.optionxform = str 
		cfgfile = open('vj_config.ini','w')
		if not Config.has_section("FileDesc"):  
			Config.add_section('FileDesc')
		for k,v in self.data.items():
		    Config.set('FileDesc',str(k),str(v))
		Config.write(cfgfile)
		cfgfile.close()    

if __name__=='__main__':
	s = Screenshot()
	#s.alt_tab()
	s.start()
	while s.advance():
		time.sleep(2)