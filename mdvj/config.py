import pygame
import pygame.midi
from pygame.locals import *
import configparser

# variables
class Config():
    # screen,binds,descs,numpads,numnumpads
    def __init__(self,screen,binds,descs,numpads=8,numnumpads= 2, debug = False):
        self.d1 = {}
        self.d2 = {}
        self.screen = screen
        self.Config = configparser.RawConfigParser()
        self.Config.optionxform = str 
        self.debug = debug
        self.the_binds = binds[::-1]
        self.their_descs = descs[::-1]

    def write_dict(self,d):
        cfgfile = open('vj_config.ini','w')
        if not self.Config.has_section("Control"):  
            self.Config.add_section('Control')
        for k,v in d.items():
            self.Config.set('Control',str(k),str(v))
        self.Config.write(cfgfile)
        cfgfile.close()
    
    def write_rules(self,d):
        cfgfile = open('vj_config.ini','w')
        if not self.Config.has_section("SorC"):  
            self.Config.add_section('SorC')
        for k,v in d.items():
            self.Config.set('SorC',str(k),str(v))
        self.Config.write(cfgfile)
        cfgfile.close()    
    
    def printText(self,txtText, Textfont=None, Textsize=36 , Textx=-1, Texty=-1, Textcolor=(150,150,150)):
        if Textx < 0: Textx=self.screen.get_width() / 2
        if Texty < 0: Texty=self.screen.get_height() / 2
        # pick a font you have and set its size
        #myfont = pygame.font.SysFont(Textfont, Textsize)
        myfont = pygame.font.Font("ProggyTinySZ.ttf", Textsize)
        # apply it to text on a label
        label = myfont.render(txtText, 1, Textcolor)
        # put the label object on the screen at point Textx, Texty
        self.screen.blit(label, (Textx - label.get_width() // 2, Texty  - label.get_height() // 2))
        # show the whole thing
        pygame.display.flip()
    
    def run(self,inp,event_get):
        going = True
        padset = False
        last = []
        while going:
            if len(self.the_binds) == 0: 
                self.write_dict(self.d1)
                self.write_rules(self.d2)
                going = False
            else:
                to_print = 'press the button for ' + str(self.the_binds[-1])
                self.printText(to_print)
                self.printText(self.their_descs[-1],Textsize=18,Texty=self.screen.get_height()//2 + 25)
                events = event_get()
                for e in events:
                    if e.type in [QUIT]:
                        going = False
                    if e.type in [KEYDOWN]: # press a key to save the value
                        set = self.the_binds.pop() 
                        self.their_descs.pop()
                        self.d1[set] = last
                        if set == '00': padset = True
                        if padset:
                            self.d2[set] = 'p'
                        elif set == 'RESET':
                            self.d2[set] = 'r' # reset 
                        elif set == 'NEXT':
                            self.d2[set] = 'a' 
                        elif set == 'PREV':
                            self.d2[set] = 'd'
                        elif set == '{}' or set == '[]':
                            self.d2[set] = 'w'
                        elif n > 120 or n < 9:
                            self.d2[set] = 's' # simple
                        else:
                            self.d2[set] = 'c' # complex
                        #print(set,' set to ',last)
                        self.screen.fill((0, 0, 0))
                   
            if inp.poll():
                midi_events = inp.read(10)
                if self.debug: print(midi_events[0][0])
                last = [midi_events[0][0][0],midi_events[0][0][1]]
                n = midi_events[0][0][2]
