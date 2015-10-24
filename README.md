### mdvj v0.5.0 - milkdrop vj midi controller :notes:

simple application that makes it easier to control milkdrop. supports any midi device or control with the mouse alone : ) 

![preview](https://raw.githubusercontent.com/pussinboot/mdvj/master/preview.PNG)

## installation instructions

1. make sure you have the dependencies fulfilled
	- pygame32 from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame)
	- pywin32 from [here](http://sourceforge.net/projects/pywin32/)
2. clone this repo
3. `python ./setup.py install`
4. to run execute: `mdvj`

-OR-

download and extract the precompiled zip from [here](https://dl.dropboxusercontent.com/u/9812886/mdvj_v_0_5_0.zip)

## usage instructions

- first time you run `mdvj`, it will guide you through the process of creating screenshots for your presets
- once that's done, select your midi device, if none just press OK and close the next window
- press midi button then click left of the description to set it
- in main app, click on preset to activate or click on arrows to switch preset groups

for use with resolume follow the instructions [here](https://github.com/pussinboot/mdvj/blob/master/resolume.md)

## to-do

- record/playback function >:D
- midi output to light up pads on your controller (if supported)
- midi reset (for knobs that cant be turned all the way around)