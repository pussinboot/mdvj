import tkinter as tk

class ConfigMidi:
	"""
	configure midi controls
	"""

	def __init__(self,midi_control):
		self.MC = midi_control
		# first popup with selection of 
		self.MC.collect_device_info()['inputs']
		# maybe outputs as well

		# then presented with list of 
		# midi-key | md function
		# click the midi-key to set it with controller
		# right click to enter params urself

		# when done save to vj_config.ini