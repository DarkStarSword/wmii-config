from pluginmanager import notify, notify_exception

from launch import launch, _launch
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
def apply_wacom():

	dev_name = 'Wacom Intuos3 9x12 cursor' # Used to come up as pad, not cursor
	# (Default mouse button mappings in brackets)
	#   +-----+-----+ +-------+   \    +-------+ +-----+-----+
	#   |     |     | |       |    \   |       | |  5  |     |
	#   |     |  1  | |  ^    |    /   |    ^  | |     |     |
	#   |     |     | |  |(4) |   /    | (4)|  | |  (9)|     |
	#   |  3  +-----+ |  |    |   \    |    |  | +-----+  7  |
	#   |     |     | |       |    \   |       | |  6  |     |
	#   |     |  2  | |       |    /   |       | |     | (11)|
	#   |     |     | |  |    |   /    |    |  | | (10)|     |
	#   +-----+-----+ |  |(5) |   \    | (5)|  | +-----+-----+
	#   |     4     | |  v    |    \   |    v  | |     8     |
	#   |        (8)| |       |    /   |       | |       (12)|
	#   +-----------+ +-------+   /    +-------+ +-----------+
	mapping = {
			# Defaults set for Windows:
			'Button1': 'key shift',
			'Button2': 'key alt',
			'Button3': 'key ctrl',
			'Button4': 'key space',

			'Button5': 'key rshift',
			'Button6': 'key ralt',
			'Button7': 'key rctrl',
			'Button8': 'key space',

			# remapping StripLUp, etc. doesn't seem to be working for me...
		}

	notify("Applying Wacom Tablet settings")
	for (prop, action) in mapping.items():
		_launch(['xsetwacom', 'set', dev_name, prop, action])

@notify_exception
def fixX11():
	notify("Applying X11 settings")
	_launch("setxkbmap -option terminate:ctrl_alt_bksp".split())
	_launch("setxkbmap -option keypad:pointerkeys".split())

	apply_wacom()

fixX11()

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts
