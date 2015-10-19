# NEEDS TO BE REWRITTEN SO THAT
# when creating database rite
# first setup press any button to take screenshot and it'll save ^^
import os, time
import shutil
from PIL import ImageTk,Image
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
#from tkinter import Tk, filedialog, messagebox
import glob
import win32api
import win32con
import win32gui
import configparser
import win32ui
from ctypes import windll

class Screenshot():
	def __init__(self,debug=False):
		self.root = tk.Tk()
		self.root.withdraw()
		if not debug:
			tkmessagebox.showinfo("welcome","looks like this is your first time running mdvj.\nto begin you must construct the database of presets\n\nmake sure to open winamp and start milkdrop before clicking OK")
			while not self.check_win('MilkDrop 2'):
				tkmessagebox.showwarning(":(","milkdrop isnt running")
			self.t = tkfiledialog.askdirectory(title='select your milkdrop presets folder',initialdir="C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets",mustexist=True)
			if not self.t:
				tkmessagebox.showwarning(">:(","select a directory please")
				self.__init__()
		else:
			self.t = "C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets"
		self.tl = len(self.t)
		self.file_list = glob.glob(self.t + "/*.milk")
		self.i = 0
		#self.data = {}
		self.start()

	def start(self):
		tkmessagebox.showinfo("get ready", "we're going to take screenshots of each preset now\n\nbefore you start make sure\n\t1. milkdrop is still open\n\t2. you've selected the 1st preset\n\t3. milkdrop is in sequential mode [r]\n\t4. the current preset is locked [ScrLock]\n\t5. you're playing a cool song")
		hwnd = win32gui.FindWindow(None, 'MilkDrop 2')
		# ""borderless window""
		style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
		style -= win32con.WS_CAPTION 
		win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
		win32gui.MoveWindow(hwnd,25,25,500,500,True)
		#self.alt_tab()

		#ScrotPicker(self,"scrot" + self.file_list[self.i][self.tl:-5] + '.png')
		self.advance()
		self.root.mainloop()

	def advance(self):

		if self.i >= len(self.file_list): # finish
			self.root.destroy()
			return False
		
		time.sleep(0.5)

		for i in range(5):
			self.save_screen("scrot/temp{0}.png".format(i))
			time.sleep(0.2)

		ScrotPicker(self,"scrot" + self.file_list[self.i][self.tl:-5] + '.png')

		return True

	def next_preset(self):
		self.alt_tab('MilkDrop 2')
		# send h
		win32api.keybd_event(0x48, 0,0,0)
		win32api.keybd_event(0x48,0 ,win32con.KEYEVENTF_KEYUP ,0)	

	def check_win(self,win):
		hwnd = win32gui.FindWindow(None, win)
		return hwnd != 0

	def alt_tab(self,win):
		try:
			hwnd = win32gui.FindWindow(None, win)
			win32gui.SetForegroundWindow(hwnd)
		except:
			print('are you sure milkdrop is running?')

	def save_screen(self,filename):
		try:
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
		except:
			self.save_screen(filename) # shouldn't break unless u do something rly dumb

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

class ScrotPicker:
	""" choose 1 of 5 pix """

	def __init__(self,parent,target_dest):
		self.target_dest = target_dest
		self.parent = parent
		self.root = tk.Toplevel(takefocus=True)
		self.root.title("pick the best screenshot")
		self.frame = tk.Frame(self.root)
		self.frame.pack()
		for i in range(5):
			ScrotDisp(self,i)
		self.root.focus_force()
		self.root.protocol("WM_DELETE_WINDOW", self.pick_new)
		
	def select(self,n):
		shutil.copy2("scrot/temp{0}.png".format(n),self.target_dest)
		self.root.destroy()
		self.parent.i += 1
		self.parent.next_preset()
		self.parent.advance()

	def pick_new(self):
		self.parent.next_preset()
		self.parent.advance()

class ScrotDisp:
	""" show a pic """

	def __init__(self,parent,n):
		self.parent = parent
		self.n = n
		self.img = Image.open("scrot/temp{0}.png".format(n))
		self.img = self.img.resize((250, 250), Image.ANTIALIAS)
		self.img = ImageTk.PhotoImage(self.img)
		self.label = tk.Label(self.parent.frame,image=self.img) 
		self.label.bind('<ButtonPress-1>',self.select)
		self.label.pack(side=tk.LEFT)

	def select(self,event):
		self.parent.select(self.n)

if __name__=='__main__':
	s = Screenshot(True)
	#pick_test = ScrotPicker("scrot/test.png")
	#s.alt_tab()
	#s.start()
	#while s.advance():
	#	time.sleep(2)