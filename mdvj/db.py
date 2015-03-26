###/
#// store presets as Preset objects
#/ store the objects in a big list of lists
#/
import glob
import os
import pygame, sys
from pygame.locals import *
import configparser

class Database():

	def __init__(self,path):
		self.db = []
		self.path = path
		self.filelist = glob.glob(path + "/*.milk")

	def start(self):
		c = 0 # count
		g = 0 # group
		n = 0
		for x in os.walk(self.path):
			n += 1
		tmp = []
		for f in self.filelist:
				# calculate f_img
				f_img = pygame.image.load("scrot" + f[len(self.path):-5] + '.png')
				# get the description :^)
				Config = configparser.RawConfigParser()
				Config.optionxform = str 
				Config.read('vj_config.ini')
				try:
					f_desc = Config.get('FileDesc',f[len(self.path)+1:-5])
				except:
					f_desc = ""
				if c % 8 == 0 and c != 0: # change 8 to numpads
					self.db.append(tmp)
					tmp = []
					g += 1
					c = 0
				tmp.append(Preset(f[len(self.path)+1:-5],f_img,f_desc,g,n)) #mydb[g][c]
				c += 1
				n += 1
		if tmp != []:
			self.db.append(tmp)
	def __getitem__(self,key):
		return self.db[key]

	def __len__(self):
		return len(self.db)

class Preset(object):

	group = 0
	n = 0

	def __init__(self,name,img,desc,group,n):
		placehold = name.find(' - ')
		if placehold > 0:
			self.name = name[placehold+3:]
			self.author = name[:placehold]
		else:
			self.author = 'unknown'
			self.name = name
		self.img = img
		self.origimg = img
		self.desc = desc
		self.group = group
		self.n = n
	def __str__(self):
		tor = self.name + ": " + self.desc
		return tor

	def resize(self,w,h): #resize the image
		self.img = pygame.transform.scale(self.origimg, (w, h))

	def place(self,screen,x,y): # places the image at x,y 
		screen.blit(self.img,(x,y))
		self.nice_text(screen,self.name,x,y,self.img.get_width(),-1)
		#self.nice_text(screen,self.desc,x,y+self.img.get_height(),self.img.get_width())
	def get_name(self):
		return self.name
	def get_desc(self):
		return self.desc
	def get_n(self):
		return self.n
	def nice_text(self,screen,text,x,y,w,ud=0,Textsize=20, Textcolor=(150,150,150)):
		# ud: -1 for up 1 for down
		font = pygame.font.Font("ProggyTinySZ.ttf", Textsize)
		fw,h = font.size(text)
		if fw > w :
			ew = font.size('..')[0]
			text = text[:(len(text)*(w-ew-15)) // fw ] + '..'
		label = font.render(text,1,Textcolor)
		pygame.draw.rect(screen,(0,0,0),(x,y + ud*h,w,h))
		# put the label object on the screen at point Textx, Texty
		screen.blit(label, (x, y + ud*h))
		# show the whole thing
		pygame.display.flip()

def main():
	pygame.init()

	WIDTH = 800
	HEIGHT = 400 
	DISPLAY=pygame.display.set_mode((WIDTH,HEIGHT),0,32)

	WHITE=(255,255,255)
	BLACK=(0,0,0)

	DISPLAY.fill(WHITE)

	def eight(g,topx,topy,w=40,h=30):
		for i in range(4):
			for j in range(2):
				curr = mydb[g][j*4 + i]
				curr.resize(w,h)
				curr.place(DISPLAY,topx+i*(w+5),topy+j*(h+5))
				#pygame.draw.rect(DISPLAY,BLACK,(topx+i*(w+5),topy+j*(h+5),w,h),2)

	#screen.blit(img,(0,0))

	eight(0,5,HEIGHT //2,(WIDTH//2 - 25)//4,(HEIGHT//4 - 6))
	eight(1,WIDTH//2 + 5,HEIGHT //2,(WIDTH//2 - 25)//4,(HEIGHT//4 - 6))
	for p in mydb[0]:
		p.resize(40,30)
	while True:
		for event in pygame.event.get():
			if event.type==QUIT:
				pygame.quit()
				sys.exit()
			pygame.display.update()


if __name__=='__main__':
	db = Database("C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets")
	db.start()
	#print(db[0][-1].get_name())