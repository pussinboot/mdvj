import tkinter as tk
import tkinter.messagebox as tkmessagebox

import os
from PIL import ImageTk,Image

from db import Database
from control_md import Controller
from screenshot import Screenshot
import midi_config

class MainGui:
	""" the main gui """

	def __init__(self,root,path="C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets"):
		# mdvj stuff
		# load saved directory, if no saved dir then run first setup (screenshot then control)
		# add menu to configure input or reselect db
		self.db = Database(path) # will update later to select your folder first
		self.db.start()
		starting_len = len(self.db)

		# tk stuff
		self.root = root
		self.frame = tk.Frame(root)
		self.padframe = tk.Frame(self.frame)

		self.control = Controller(self)
		inp = self.control.load('Twitch.ini') # for testing purposes
		self.control.midi_start(inp)

		self.padgroup_l_n = -1
		self.padgroup_r_n = -1
		if starting_len > 1:
			self.padgroup_l_n = 0
			self.padgroup_r_n = 1
			self.padgroup_l = PadGroup(self,0,self.db[0])
			self.padgroup_r = PadGroup(self,1,self.db[1])
		else:
			if starting_len > 0:
				self.padgroup_l_n = 0
				self.padgroup_l = PadGroup(self,0,self.db[0])
			else:
				self.padgroup_l = PadGroup(self,0)
			self.padgroup_r = PadGroup(self,1)
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
		self.padgroup_l.init_containers(self.db[self.padgroup_l_n])
		self.padgroup_r.init_containers(self.db[self.padgroup_r_n])
		self.root.update_idletasks()
		self.check_lr()
		self.control.MC.resume()

	def go_r(self):
		self.control.MC.pause()
		self.padgroup_l_n += 1
		self.padgroup_r_n += 1
		self.padgroup_l.init_containers(self.db[self.padgroup_l_n])
		self.padgroup_r.init_containers(self.db[self.padgroup_r_n])
		self.root.update_idletasks()
		self.check_lr()
		self.control.MC.resume()

	def quit(self):
		#self.root.destroy()
		pass


class PadGroup:
	""" stores 8 presets """

	def __init__(self,parent,lr,presets=None):
		self.parent = parent
		self.preset_containers = [None]*8
		self.lr = lr
		self.frame = tk.Frame(parent.padframe,borderwidth=5,relief=tk.RIDGE)
		self.frame.pack(side=tk.LEFT)
		if presets:
			self.init_containers(presets)

	def init_containers(self,presets):
		max_len = len(presets)
		for r in range(2):
			for c in range(4):
				i = r * 4 + c
				if i >= max_len :
					return
				#print(self.db[r][c])
				self.preset_containers[i] = PresetContainer(self,presets[i],self.lr,i)
				self.preset_containers[i].grid(row=r,column=c)


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
		self.padgroup.parent.control.select_pad(*self.coords)
		#self.padgroup.parent.control.select_pad_gui(*self.coords)
		#self.selected()

	def selected(self):
		self.label.config(relief=tk.SUNKEN)

	def deselected(self):
		self.label.config(relief=tk.FLAT)
		
def Setup():
	""" loads config if exists, otherwise guides you through setup process"""
	
	if os.path.exists('vj_config.ini'):
		# load config
		print('config exists')
	else:
		#Screenshot()
		#ConfigMidi(tk.Toplevel())
		#midi_config.main()
		main()
		# and then configure midi controller : )
		# and then finna run the fun

def main():
	root = tk.Tk()
	root.title("mdvj")
	root.resizable(0,0)
	gui = MainGui(root,"C:/Code/python/mdvj/v0.5.0/scrot") # fake data
	root.mainloop()

if __name__ == '__main__':
	
	Setup()
	#
	#