# virtual keycodes
# https://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx
# tk guide
# http://www.python-course.eu/tkinter_dialogs.php
#
#####
# TO DO
# fix swipers :^) -> object with local state that resets with opposite direction
# lights
# preset manager -> save db as csv
# preset sequence playback

import pygame
import pygame.midi
from pygame.locals import *
import configparser
import os.path
from screenshot import *
from config import Config
from db import Database
from control import Controller
from gui import gui

# global vars
path = ""
numpads = 8
numnumpads = 2
binds = ['z', 'c', 'v', 'b', 'iI', '[]', '{}', '<>', 'oO', 'w', 'jJ', 'eE', 'gG', 'qQ', 'F', 'RESET','NEXT','PREV']
descs = ['prev', 'play/pause', 'stop', 'next', 'zoom in / zoom out', 'push motion left/right', 'push motion up/down', 'rotate left/rotate right', 'shrink/grow amplitude of warp', 'cycle waveform', 'scale waveform down/up', 'make the waveform more transparent/solid', 'decrease/increase brightness', 'scale 2nd graphics layer down/up', 'flip 2nd graphics layer (cycle)', 'toggle reset mode','next preset set','previous preset set']
for nn in range(numnumpads):
    for n in range(numpads):
        binds.append(str(nn)+str(n))
        descs.append("set #{} pad #{}".format(nn,n))

def pg_setup():
	pygame.init()
	pygame.midi.init()
	pygame.fastevent.init()
	event_get = pygame.fastevent.get
	pygame.display.set_caption("veejay")
	screen = pygame.display.set_mode((1024, 768), RESIZABLE, 32)
	try:
		inp = pygame.midi.Input(1)
		out = pygame.midi.Output(3, latency = 0) #?
	except:
		print('midi device not found')
		pygame.midi.quit()
		pygame.quit()
		exit()
	# advanced mode
	out.write([[[183,0,111],pygame.midi.time()]])
	# touchstrip data mode
	out.write([[[183,20,19],pygame.midi.time()]])
	out.write([[[184,20,19],pygame.midi.time()]])
	return screen, inp, out, event_get

def pg_quit(inp,out):
	# exit advanced mode
	out.write([[[183,0,0],pygame.midi.time()]])
	inp.close()
	out.close()
	pygame.midi.quit()
	pygame.quit()
	exit()

def first_run(screen,inp,event_get):
	if(os.path.exists("vj_config.ini")): return
	config(screen,inp,event_get)
	screenshot()

def screenshot():
	s = Screenshot()
	path = s.get_dir()
	s.start()
	going = True
	while going:
		going = s.advance()

def config(screen,inp,event_get):
	c = Config(screen,binds,descs,numpads=numpads,numnumpads=numnumpads)
	c.run(inp,event_get)

def db(path):
	d = Database(path)
	d.start()
	return d

if __name__=='__main__':
	screen,inp,out, event_get = pg_setup()
	first_run(screen,inp,event_get)
	d = db("C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets")
	g = gui(screen)
	c = Controller(inp,out,event_get,binds,descs,d,g)
	pg_quit(inp,out)
	
