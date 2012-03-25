from pluginmanager import notify, notify_exception

from launch import launch, _launch
import wacom
import os, background

from pygmi import *

import mixer
mixer.mixers = ['Master', 'LFE']

background.set_background(os.path.expanduser('~/water-drop1.jpg'))

keys.bind('main', (
	"Dell specific keys",
	('Mod1-Control-x', "Re-apply X11 settings",
		lambda k: fixX11()),
	))

@notify_exception
def fixX11():
	notify("Applying X11 settings")
	_launch("setxkbmap -option terminate:ctrl_alt_bksp".split())
	_launch("setxkbmap -option keypad:pointerkeys".split())

	wacom.apply_profile('Wacom Intuos3 9x12 pad', 'gimp')

fixX11()

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts
