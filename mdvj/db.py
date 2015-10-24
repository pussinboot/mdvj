###/
#// store presets as Preset objects
#/ store the objects in a big list of lists
#/
import glob
import os
# import configparser

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
				f_img = "scrot" + f[len(self.path):-5] + '.png'
				# get the description :^)
				# Config = configparser.RawConfigParser()
				# Config.optionxform = str 
				# Config.read('vj_config.ini')
				# try:
				# 	f_desc = Config.get('FileDesc',f[len(self.path)+1:-5])
				# except:
				# 	f_desc = ""
				if c % 8 == 0 and c != 0: # change 8 to numpads
					self.db.append(tmp)
					tmp = []
					g += 1
					c = 0
				tmp.append(Preset(f[len(self.path)+1:-5],f_img,g,n)) #mydb[g][c] f_desc
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

	def __init__(self,name,img,group,n):
		placehold = name.find(' - ')
		if placehold > 0:
			self.name = name[placehold+3:]
			self.author = name[:placehold]
		else:
			self.author = 'unknown'
			self.name = name
		self.img = img
		self.group = group
		self.n = n
	def __str__(self):
		tor = self.name + "by " + self.author
		return tor


if __name__=='__main__':
	db = Database("C:/Program Files (x86)/Winamp/plugins/milkdrop2/presets")
	#db = Database("C:/Code/python/mdvj/v0.5.0/scrot")
	db.start()
	print(db[0][-1].name)
	print(len(db))