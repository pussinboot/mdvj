import tkinter as tk
import tkinter.messagebox as tkmessagebox

import os, queue, pickle, time, sys
from PIL import ImageTk,Image

from db import Database
from control_md import Controller
from screenshot import Screenshot
import midi_config

class MainGui:
	""" the main gui """

	def __init__(self,root,mainprogram=None,path="C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets",midi_save=None):
		# mdvj stuff
		# load saved directory, if no saved dir then run first setup (screenshot then control)
		# add menu to configure input or reselect db
		self.mainprogram = mainprogram
		self.db = Database(path) # will update later to select your folder first
		self.db.start()
		starting_len = len(self.db)

		# tk stuff
		self.root = root
		self.frame = tk.Frame(root)
		self.padframe = tk.Frame(self.frame)

		self.queue = None
		
		#self.padgroup_l_n = -1
		#self.padgroup_r_n = -1
		#if starting_len > 1:
		self.padgroup_l_n = 0
		self.padgroup_r_n = 1
		self.padgroup_l = SuperPadGroup(self,0)#,self.db[0])
		self.padgroup_r = SuperPadGroup(self,1)#,self.db[1])
		#else:
		#	if starting_len > 0:
		#		self.padgroup_l_n = 0
		#		self.padgroup_l = SuperPadGroup(self,0)#,self.db[0])
		#	else:
		#		self.padgroup_l = SuperPadGroup(self,0)
		#	self.padgroup_r = SuperPadGroup(self,1)
		self.padgroups = [self.padgroup_l,self.padgroup_r]


		self.controlframe = tk.Frame(self.frame)
		self.prev_col_button = tk.Button(self.controlframe,text="<",command=lambda: self.control.go_lr(0),pady=0)
		self.next_col_button = tk.Button(self.controlframe,text=">",command=lambda: self.control.go_lr(1),pady=0)
		self.check_lr()
		self.next_col_button.pack(side=tk.RIGHT,anchor=tk.SE)
		self.prev_col_button.pack(side=tk.RIGHT,anchor=tk.SE)
		self.padframe.pack()
		self.controlframe.pack()
		self.frame.pack()

		if self.mainprogram: self.setup_menubar()

		self.control = Controller(self)
		if midi_save: midi_save = midi_save + '.ini'
		inp = self.control.load(midi_save) 
		self.control.midi_start(inp)

	def set_queue(self,queue):
			self.queue = queue

	def processIncoming(self): # change queue to only handle events that would cause gui changes
		while self.queue.qsize():
			try:
				msg = self.queue.get(0)
				# Check contents of message and do what it says
				# As a test, we simply print it
				# print( msg)
				if msg[0] == 'pad':
					self.control.select_pad_gui(*msg[1])
				elif msg[0] == 'lr':
					if msg[1] == 0:
						self.go_l()
					else:
						self.go_r()
				
			except queue.Empty:
				pass


	def check_lr(self):
		if self.padgroup_l_n > 0:
			# enable l
			self.prev_col_button.config(state='normal')
		else:
			# bad
			self.prev_col_button.config(state='disabled')
		if self.padgroup_r_n < len(self.db) - 1:
			# enable r
			self.next_col_button.config(state='normal')
		else:
			# bad
			self.next_col_button.config(state='disabled')

	def go_l(self):
		self.control.MC.pause()
		self.padgroup_l_n -= 1
		self.padgroup_r_n -= 1
		self.padgroup_l.show_group(self.padgroup_l_n)
		self.padgroup_r.show_group(self.padgroup_r_n)
		self.root.update_idletasks()
		self.check_lr()
		self.control.MC.resume()

	def go_r(self):
		self.control.MC.pause()
		self.padgroup_l_n += 1
		self.padgroup_r_n += 1
		self.padgroup_l.show_group(self.padgroup_l_n)
		self.padgroup_r.show_group(self.padgroup_r_n)
		self.root.update_idletasks()
		self.check_lr()
		self.control.MC.resume()

	def quit(self):
		#self.root.destroy()
		pass

	def setup_menubar(self):
		self.menubar = tk.Menu(self.root)
		self.filemenu = tk.Menu(self.menubar,tearoff=0)
		self.filemenu.add_command(label="retake screenshots",command=self.mainprogram.re_screenshot)
		self.filemenu.add_command(label="reconfig midi",command=self.mainprogram.re_configure)
		self.menubar.add_cascade(label='settings',menu=self.filemenu)

		self.root.config(menu=self.menubar)
		
class SuperPadGroup:
	""" stores stacked PadGroups """

	def __init__(self,parent,lr):
		self.parent = parent
		self.padgroup_cont = []
		self.current_group = lr
		self.frame = tk.Frame(parent.padframe,borderwidth=5,relief=tk.RIDGE)
		self.frame.pack(side=tk.LEFT, fill="both", expand=True) #pack(side=tk.LEFT)
		self.frame.grid_rowconfigure(0, weight=1)
		self.frame.grid_columnconfigure(0, weight=1) 
		for i in range(len(self.parent.db)):
			new_pad_group = PadGroup(self,lr,self.parent.db[i])
			self.padgroup_cont.append(new_pad_group)
		self.show_group(self.current_group)

	def show_group(self,groupno):
		self.current_group = groupno
		cgroup = self.padgroup_cont[groupno]
		cgroup.frame.tkraise()
		cgroup.deselect_all()

	def current_padgroup(self):
		return self.padgroup_cont[self.current_group]

class PadGroup:
	""" stores 8 presets """

	def __init__(self,parent,lr,presets=None):
		self.parent = parent
		self.preset_containers = [None]*8
		self.max_len = len(presets)
		self.lr = lr
		self.frame = tk.Frame(parent.frame)#,borderwidth=5,relief=tk.RIDGE)
		self.frame.grid(row=0, column=0, sticky='news')#pack(side=tk.LEFT, fill="both", expand=True) #pack(side=tk.LEFT)
		#self.frame.grid_rowconfigure(0, weight=1)
		#self.frame.grid_columnconfigure(0, weight=1) 
		if presets:
			self.init_containers(presets)

	def init_containers(self,presets):
		for r in range(2):
			for c in range(4):
				i = r * 4 + c
				if i >= self.max_len :
					return
				#print(self.db[r][c])
				self.preset_containers[i] = PresetContainer(self,presets[i],self.lr,i)
				self.preset_containers[i].grid(row=r,column=c)
				#self.parent.root.update_idletasks()

	def deselect_all(self):
		for i in range(self.max_len):
			self.preset_containers[i].deselected()


class PresetContainer:
	""" stores a single preset """

	def __init__(self,padgroup,preset,lr,padno):
		self.padgroup = padgroup
		self.preset = preset
		self.coords = [lr,padno]
		self.img = Image.open(self.preset.img)
		self.img = self.img.resize((150, 150), Image.ANTIALIAS)
		self.img = ImageTk.PhotoImage(self.img)
		self.label = tk.Label(self.padgroup.frame,image=self.img,text="",compound='top',width=150,bd=5) 
		self.change_text(self.preset.name)
		self.grid = self.label.grid
		self.label.bind('<ButtonPress-1>',self.select)
	def change_text(self,new_text):
		new_text = str(new_text)
		if len(new_text) > 18:
			new_text = new_text[:17] + ".."
		self.label.config(text=new_text)

	def select(self,event=None):
		self.padgroup.parent.parent.control.select_pad(*self.coords)
		#self.padgroup.parent.control.select_pad_gui(*self.coords)
		#self.selected()

	def selected(self):
		self.label.config(relief=tk.SUNKEN)

	def deselected(self):
		self.label.config(relief=tk.FLAT)

class MainProgram:

	def __init__(self):
		self.savedata = self.Load()
		self.input_name = None
		self.directory = None

		self.Setup()
			
	def Setup(self):
		""" loads config if exists, otherwise guides you through setup process"""
		
		if not self.savedata:
			s = Screenshot()
			self.directory = s.start()
			input_store = midi_config.main() # needs rewrite to follow the use queue to update gui standard
			if input_store:
				self.input_name = input_store[0]
		else:
			self.directory = self.savedata['directory']
			if not self.input_name: self.input_name = self.savedata['last_device']
			#s = Screenshot()
			#directory = s.start()
			#print(directory)
			#ConfigMidi(tk.Toplevel())
		self.root = tk.Tk()
		self.root.title('mdvj')
		self.root.resizable(0,0)	
		self.gui = MainGui(self.root,self,self.directory,self.input_name)
		self.root.mainloop()

	def Load(self,filename="saved_state"):
			if os.path.exists(filename):
				with open(filename,'rb') as read:
					try:
						pickle_d = pickle.load(read)
						return pickle_d
					except:
						print('error reading',filename)
						read.close()
						os.remove(filename)
			else:
				print("no saved state")

	def Save(self,filename="saved_state"):
		"""
		save a dictionary to pickle
		"""
		to_save = {}
		if self.directory: to_save['directory'] = self.directory
		if self.input_name: to_save['last_device'] = self.input_name
		if to_save != {}:
			with open(filename,'wb') as write:
				pickle.dump(to_save,write)

	def re_screenshot(self):
		self.gui.control.close()
		self.gui = None
		s = Screenshot(first_time=False)
		self.directory = s.start()
		self.gui = MainGui(root,self,self.directory,self.input_name)

	def re_configure(self):
		self.gui.control.close()
		self.gui = None
		input_store = midi_config.main()
		if input_store: self.input_name = input_store[0]
		self.gui = MainGui(root,self,self.directory,self.input_name)

def main():
	root = tk.Tk()
	root.title("mdvj")
	root.resizable(0,0)
	gui = MainGui(root)#,"C:/Code/python/mdvj/v0.5.0/scrot") # fake data
	root.mainloop()

if __name__ == '__main__':
	
	mainp = MainProgram()
	mainp.Save()
	#main()
	# make fake save
	# to_save = {}
	# with open("saved_state",'wb') as write:
	# 	pickle.dump(to_save,write)