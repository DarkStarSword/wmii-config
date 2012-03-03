from pluginmanager import notify, notify_exception

from launch import launch, _launch
import os, background
import subprocess

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

	# NOTE: Different versions of xsetwacom have different mappings, yours
	# may vary! If you don't have a "pad", try "cursor" or upgrade.
	dev_name = 'Wacom Intuos3 9x12 pad'
	#   +-----+-----+ +-------+   \    +-------+ +------+------+
	#   |     |     | |       |    \   |       | |      |      |
	#   |     |  1  | |  ^    |    /   |    ^  | |   9  |      |
	#   |     |     | |  |(4) |   /    | (4)|  | |      |      |
	#   |  3  +-----+ |  |    |   \    |    |  | +------+  11  |
	#   |     |     | |       |    \   |       | |      |      |
	#   |     |  2  | |       |    /   |       | |  10  |      |
	#   |     |     | |  |    |   /    |    |  | |      |      |
	#   +-----+-----+ |  |(5) |   \    | (5)|  | +------+------+
	#   |     8     | |  v    |    \   |    v  | |     12      |
	#   |           | |       |    /   |       | |             |
	#   +-----------+ +-------+   /    +-------+ +-------------+
	mapping = (
			# NOTE: BE SURE TO MAP THE STRIPS BEFORE THE BUTTONS
			# DUE TO A BUG IN THE WACOM STACK WHICH ERRANEOUSELY
			# MAPS BUTTONS 1-4 WHEN THE STRIPS ARE MAPPED
			('StripLeftUp',    'key +ctrl button 4 key -ctrl'),
			('StripLeftDown',  'key +ctrl button 5 key -ctrl'),
			# ('StripRightUp',   'key k'),
			# ('StripRightDown', 'key j'),

			# Defaults set for Windows:
			('Button 1', 'key shift'),
			('Button 2', 'key alt'),
			('Button 3', 'key ctrl'),
			('Button 8', 'key +space'),

			('Button 9',  'key rshift'),
			('Button 10', 'key ralt'),
			('Button 11', 'key rctrl'),
			('Button 12', 'key +space'),
		)

	notify("Applying Wacom Tablet settings")
	# Work around a bug in the wacom stack causing the buttons to override
	# the strips (similar, but opposite to above bug note) by doing
	# everything twice:
	for i in range(2):
		for (prop, action) in mapping:
			# Wait for termination to avoid race:
			subprocess.call(['xsetwacom', 'set', dev_name] + prop.split() + [action])

@notify_exception
def fixX11():
	notify("Applying X11 settings")
	_launch("setxkbmap -option terminate:ctrl_alt_bksp".split())
	_launch("setxkbmap -option keypad:pointerkeys".split())

	apply_wacom()

fixX11()

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts
