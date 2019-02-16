### mdvj v0.5.1 - milkdrop vj midi controller :notes:

simple application that makes it easier to control milkdrop. supports any midi device or control with the mouse alone : )

![preview](https://raw.githubusercontent.com/pussinboot/mdvj/master/preview.PNG)

## installation instructions

1. make sure you have the dependencies fulfilled
	- pywin32 from [here](http://sourceforge.net/projects/pywin32/)
	- pygame32 from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame) (only if you plan on using midi)
2. clone this repo
3. `python ./setup.py install`
4. to run execute: `mdvj`

-OR-

download and extract the precompiled zip from [here](https://github.com/pussinboot/mdvj/releases/tag/0.5.1)

## usage instructions

- first time you run `mdvj`, it will guide you through the process of creating screenshots for your presets
- once that's done, select your midi device, if none just press OK and close the next window
- press midi button then click left of the description to set it
- in main app, click on preset to activate or click on arrows to switch preset groups

for use with resolume follow the instructions [here](https://github.com/pussinboot/mdvj/blob/master/resolume.md)

## known bugs

milkdrop uses a funny sorting algorithm for determining order of presets so the name of a preset will not always match up with what you select.
no worries, the screenshot is still correct.. if this bothers you, you can rename your presets so that milkdrop follows the same order as your file explorer.
