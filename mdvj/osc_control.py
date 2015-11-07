from pythonosc import dispatcher
from pythonosc import osc_server
import threading

class OscControl:
	def __init__(self,gui=None,server_ip="127.0.0.1",server_port=7000):
		self.gui = gui
		self.running = 0
		self.refresh_int = 25
		self.server_ip, self.server_port = server_ip,server_port
		self.dispatcher = dispatcher.Dispatcher()
		#self.dispatcher.map("/midi",self.put_in_queue)

		
		#self.server_thread.start()

	def put_in_queue(self,_,value):
		arr = eval(value)
		tor = (arr[:2],arr[2])
		#print(tor)
		self.queue.put(value)
	
	def start(self):
		self.running = 1
		self.gui.master.protocol("WM_DELETE_WINDOW",self.stop)
		self.server = osc_server.ThreadingOSCUDPServer((self.server_ip, self.server_port), self.dispatcher)
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.start()
		self.run_periodic = self.gui.master.after(self.refresh_int,self.periodicCall)

	def stop(self):
		self.running = 0
		self.server.shutdown()
		self.server_thread.join()

# thread to update gui

	def periodicCall(self):
		self.gui.processIncoming()
		if not self.running:
			if self.run_periodic:
				self.gui.master.after_cancel(self.run_periodic)
				self.gui.quit()
				self.gui.master.destroy()

		self.run_periodic = self.gui.master.after(self.refresh_int,self.periodicCall)


if __name__ == '__main__':
	osc_test = OscControl()
	osc_test.start()