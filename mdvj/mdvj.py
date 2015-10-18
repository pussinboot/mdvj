# virtual keycodes
# https://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx
# tk guide
# http://www.python-course.eu/tkinter_dialogs.php
#
#####
# TO DO
# lights bugfix
# preset manager -> save db as csv ? along with better gui
# preset sequence playback/sequencer
# save certain "global" variables over runs
# move selecting midi device to first run?

import pygame
from pygame.locals import *
import configparser
import os.path
from mdvj.screenshot import *
from mdvj.config import Config
from mdvj.db import Database
from mdvj.control import Controller
from mdvj.gui import gui
import sys, getopt

# global vars
path = ""
numpads = 8
numnumpads = 2
binds = ['z', 'c', 'v', 'b', 'iI', '[]', '{}', '<>', 'oO', 'w', 'jJ', 'eE', 'gG', 'qQ', 'F', 'RESET','NEXT','PREV']
descs = ['prev', 'play/pause', 'stop', 'next', 'zoom in / zoom out', 'push motion left/right', 'push motion up/down', 'rotate left/rotate right', 'shrink/grow amplitude of warp', 'cycle waveform', 'scale waveform down/up', 'make the waveform more transparent/solid', 'decrease/increase brightness', 'scale 2nd graphics layer down/up', 'flip 2nd graphics layer (cycle)', 'toggle reset mode','next preset set','previous preset set']
twitch = True
debug = False

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
	an_id = pygame.midi.get_default_input_id()
	print(an_id)
	if an_id == -1:
		print('no midi inputs found')
		pygame.midi.quit()
		pygame.quit()
		exit()
	i = 0
	print("midi devices connected:")
	while True:
		try:
			_, name, inp, outp, _ = pygame.midi.get_device_info(i)
			print (name[2:-1],'in:', inp,'out:',outp)
			i += 1
		except:
			break

	inn = input("select an input #: ")
	outt = input("select an output #: ")

	try:
		inp = int(inn)
		outn = int(outt)
	except ValueError:
		print('using default device')
		_, _, inp, outn, _ = pygame.midi.get_device_info(an_id)

	try:
		inp = pygame.midi.Input(inp)
		out = pygame.midi.Output(outn, latency = 0)
	except:
		print("midi device not found")
		pygame.midi.quit()
		pygame.quit()
		exit()

	if twitch:
		# advanced mode
		out.write([[[183,0,111],pygame.midi.time()]])
		# touchstrip data mode
		out.write([[[183,20,19],pygame.midi.time()]])
		out.write([[[184,20,19],pygame.midi.time()]])

	screen = pygame.display.set_mode((1024, 768), RESIZABLE, 32)
	return screen, inp, out, event_get

def pg_quit(inp,out):
	# exit advanced mode
	if twitch: out.write([[[183,0,0],pygame.midi.time()]])
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
	c = Config(screen,binds,descs,numpads=numpads,numnumpads=numnumpads,debug=debug)
	c.run(inp,event_get)

def db(path):
	d = Database(path)
	d.start()
	return d

hint = """usage: mdvj -c / -d / -h
	use flag -c if you do not have a twitch controller
	use flag -d if you want debug text
	use flag -h to print this text
"""

def main(argv):
	if len(argv) > 0:
		for arg in argv:
			if arg == '-h':
				print(hint)
				sys.exit()
			elif arg == '-c':
				twitch = False
			elif arg == '-d':
				debug = True
	screen,inp,out, event_get = pg_setup()
	first_run(screen,inp,event_get)
	d = db("C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets")
	g = gui(screen)
	c = Controller(inp,out,event_get,binds,descs,d,g,debug=debug,twitch=twitch)
	pg_quit(inp,out)

if __name__=='__main__':
	main()
	
