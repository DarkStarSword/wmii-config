from pygmi import *

from pluginmanager import notify, notify_exception, imported_from_wmiirc
from launch import launch, _launch, terminal
import wacom
import wmiirc
import lock

import os

xmodmap_delay = 0.7

# Reverse coloured/B+W keys
term_large_font = '-fa Monospace -fs 24'.split()
keys.bind('main', (
	"Running programs",
	('%(mod)s-Return', "Launch a terminal (Black + White)",
		lambda k: launch(terminal(bw = True))),
	('%(mod)s-Shift-Return', "Launch a terminal (Black, White & Large)",
		lambda k: launch(terminal(bw = True, font = term_large_font))),
	('%(mod)s-Control-Return', "Launch a terminal (Normal)",
		lambda k: launch(terminal())),
	('%(mod)s-Control-Shift-Return', "Launch a terminal (Large)",
		lambda k: launch(terminal(font = term_large_font))),

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
def do_xmodmap():
	_launch(['xmodmap', os.path.expanduser('~/.xmodmaprc')])
	# For debugging:
	# import subprocess, sys
	# print 'xmodmap returned: %i' % subprocess.call(['xmodmap', '-verbose', os.path.expanduser('~/.xmodmaprc')], stdout=sys.stdout, stderr=sys.stderr)

@notify_exception
def fixX11():
	import threading

	notify("Applying X11 settings")
	_launch("setxkbmap -option terminate:ctrl_alt_bksp".split())
	_launch("setxkbmap -option keypad:pointerkeys".split())

	wacom.apply_profile('Wacom Intuos3 9x12 pad', 'gimp')

	t = threading.Timer(xmodmap_delay, do_xmodmap)
	t.daemon = True
	t.start()

if imported_from_wmiirc():
  import wmiirc
  # xfontsel to find these types:
  wmiirc.wmii['font'] = '-*-helvetica-bold-r-*-*-34-*-*-*-*-*-*-*'

lock.disableAutoLock()
fixX11()

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts
