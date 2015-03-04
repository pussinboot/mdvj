import pygame
from pygame.locals import *

class gui():

	def __init__(self,screen,numpads = 8,numnumpads = 2):
		self.screen = screen
		self.WIDTH = screen.get_width()
		self.HEIGHT = screen.get_height() 
		self.numpads = numpads
		self.numnumpads = numnumpads
		self.traceback = []
		self.font = pygame.font.Font("ProggyTinySZ.ttf", 36)
		self.textw = 0
		self.texth = self.font.size('Tg')[1]

	def resize(self,w,h):
		self.WIDTH = w
		self.HEIGHT = h
		self.screen=pygame.display.set_mode((w,h),HWSURFACE|DOUBLEBUF|RESIZABLE)
		# redraw everything as is

		self.traceback[0](*self.traceback[1])
	def start(self):

		for n in range(self.numnumpads):
			for i in range(self.numpads//2):
				for j in range(2):
					self.square(n,i,j,(255,255,255),2)
		pygame.display.update()
		self.traceback = [self.start, []]
		#eight(5,HEIGHT //2,(WIDTH//2 - 25)//4,(HEIGHT//4 - 6))
		#eight(WIDTH//2 + 5,HEIGHT //2,(WIDTH//2 - 25)//4,(HEIGHT//4 - 6))
	
	
	def square(self,n,i,j,color,f=0,d=15):
		topx = n*self.WIDTH//2
		topy = self.HEIGHT //2
		w = self.WIDTH//self.numpads - d // 2
		h = self.HEIGHT*2//self.numpads - d - 1
		if f != 0:
			pygame.draw.rect(self.screen,color,(topx+i*(w+d),topy+j*(h+d),w,h),f)
		else:
			pygame.draw.rect(self.screen,color,(topx+i*(w+d),topy+j*(h+d),w,h))
	
	def place_presets(self,db,n1,n2,d=32):
		topx = 0
		topy = self.HEIGHT//2 + d
		w = self.WIDTH//self.numpads - d // 2 - 1
		h = self.HEIGHT*2//self.numpads - d - 1
		self.eight(db[n1],topx,topy,w,h,d)
		self.eight(db[n2],topx+self.WIDTH//2+d // 2,topy,w,h,d)
		pygame.display.update()
		self.traceback = [self.place_presets,[db,n1,n2,d]]

	def eight(self,db_list,topx,topy,w,h,d=15):
		for i in range(4):
			for j in range(2):
				if j*4 + i < len(db_list):
					curr = db_list[j*4 + i]
					curr.resize(w,h)
					curr.place(self.screen,topx+i*(w+d//2),topy+j*h)


	def write_text(self,text,x=-1,y=-1,c=0,color=(150,150,150)):
		if x < 0: x=self.screen.get_width() / 2
		if y < 0: y=self.screen.get_height() / 2
		label = self.font.render(text, 1, color)
		w = self.font.size(text)[0]
		if w > self.textw: self.textw = w
		pygame.draw.rect(self.screen,(0,0,0),(x,y,self.textw,self.texth))
		if c != 0:
			self.screen.blit(label, (x - label.get_width() // 2, y  - label.get_height() // 2))
		else:
			self.screen.blit(label,(x,y))
		pygame.display.flip()
		
	#eight(0,5,HEIGHT //2,(WIDTH//2 - 25)//4,(HEIGHT//4 - 6))
	#eight(1,WIDTH//2 + 5,HEIGHT //2,(WIDTH//2 - 25)//4,(HEIGHT//4 - 6))
	#for p in mydb[0]:
	#	p.resize(40,30)
	#while True:
	#	for event in pygame.event.get():
	#		if event.type==QUIT:
	#			pygame.quit()
	#			sys.exit()
	#		pygame.display.update()