import tkinter as tk

from midi_control import MidiControl

class ConfigMidi:
	"""
	configure midi controls
	"""

	def __init__(self,midi_control):
		self.MC = midi_control
		# first popup with selection of inputs
		# and outputs as well

		# then presented with list of 
		# midi-key | md function
		# click the midi-key to set it with controller
		# right click to enter params urself

		# when done save to vj_config.ini

	def device_selection(self):
		self.device_dict = self.MC.collect_device_info()


if __name__ == '__main__':
	root = tk.Tk()
	MC = MidiControl()
	root.mainloop()
