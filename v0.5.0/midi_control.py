import pygame.midi

class MidiControl:
	def __init__(self):
		pygame.midi.init()
		self.inp = pygame.midi.Input(pygame.midi.get_default_input_id())

	def collect_device_info(self): # using this can construct list of inputs/outputs and have their corresponding channels
		inputs = []
		outputs = []
		i = res = 0
		while True:
			res = pygame.midi.get_device_info(i)
			if res is None: break
			to_add = str(res[1])[2:-1]
			if res[2] == 1:
				inputs.append((to_add,i))
			else:
				outputs.append((to_add,i))
			i += 1
		return {'inputs':inputs,'outputs':outputs}	

	def quit(self):
		# self.out.close()
		self.inp.close()
		pygame.midi.quit()

	def test_inp(self):
		#while True:
		if self.inp.poll():
			midi_events = self.inp.read(10)
			the_key = str([midi_events[0][0][0],midi_events[0][0][1]])
			n = int(midi_events[0][0][2])
			#print(the_key,n)
			return (the_key,n)

if __name__ == '__main__':
	MC = MidiControl()
	test_d = MC.collect_device_info()
	print('inputs',test_d['inputs'])
	print('outputs',test_d['outputs'])
	MC.quit()