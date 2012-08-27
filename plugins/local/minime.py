from pygmi import *

from pluginmanager import notify, notify_exception
from launch import launch, _launch
import wacom
import wmiirc
import lock

import os

keys.bind('main', (
	"Mac Mini specific keys",
	('Mod1-Control-x', "Re-apply X11 settings",
		lambda k: fixX11()),

	('%(mod)s-F6', "Launch MythFrontend",
		lambda k: launch('mythfrontend')),
	('%(mod)s-Shift-F6', "Kill MythFrontend",
		lambda k: launch('killall -9 mythfrontend'.split())),

	('%(mod)s-F7', "Launch XBMC",
		lambda k: launch('xbmc')),
	('%(mod)s-Shift-F7', "Kill XBMC",
		lambda k: launch('killall -9 xbmc.bin'.split())),

	('%(mod)s-F8', "Eject CD",
		lambda k: launch('eject')),
	# TODO: (maybe shift-f8 mount/unmount, or vice versa):
	# pmount cdrom 2>&1 | grep 'already mounted\|wrong fs type' && eject

	))

@notify_exception
def fixX11():
	notify("Applying X11 settings")
	_launch(['xmodmap', os.path.expanduser('~/.xmodmaprc')])
	_launch("setxkbmap -option terminate:ctrl_alt_bksp".split())
	_launch("setxkbmap -option keypad:pointerkeys".split())

	wacom.apply_profile('Wacom Intuos3 9x12 pad', 'gimp')

lock.disableAutoLock()
fixX11()

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts
