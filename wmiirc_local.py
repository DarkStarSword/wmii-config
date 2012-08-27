import os

import plugins.pluginmanager # Should be done before import pygmi to make sure path is set up

import wmiirc
from pygmi import *

from plugins.launch import launch, launch_music_player, terminal, apps
from plugins import lock, music, unload, resize, display, background

apps.webBrowser		= 'iceweasel'
apps.emailClient	= terminal('sup-mail', bw=True)
apps.RSSReader		= terminal('canto')
apps.python		= terminal('ipython', bw=True)
apps.musicPlayer	= terminal('cmus')
apps.otherMusicPlayer	= terminal('mocp')
apps.IMClient		= terminal('finch', bw=True)
apps.IRCClient		= terminal('irssi')
apps.calendar		= terminal('wyrd', sleep=True) # Sleep is to avoid race condition triggering bug in wyrd on window resize
apps.networkManager	= terminal('wicd-curses')
apps.calculator		= terminal('calc')
apps.bluetoothManager	= 'blueman-manager'
apps.mixer		= 'pavucontrol'
apps.voip		= 'mumble'

monitors['load'].active = False

# Clean up showKeys for keys I'm going to override & actions I don't want
keys.unbind('main', '%(mod)s-b')
keys.unbind('main', '%(mod)s-Shift-b')
keys.unbind('main', '%(mod)s-n')
keys.unbind('main', '%(mod)s-Shift-n')
keys.unbind('main', '%(mod)s-i')
keys.unbind('main', '%(mod)s-Shift-i')
keys.unbind('main', '%(mod)s-o')
keys.unbind('main', '%(mod)s-Shift-o')

background.set_background(os.path.expanduser('~/desktop.jpg'))

# Rebind mod+return, as the default wmiirc.py does not pass the environment
# through, leading xterm to manufacture a new environment that includes LINES
# and COLS, which causes issues for curses applications. Our launch.py plygin
# passes os.environ through to avoid the issue.
keys.unbind('main', '%(mod)s-Return')
term_large_font = '-fa Monospace -fs 24'.split()
keys.bind('main', (
	"Running programs",
	('%(mod)s-Return', "Launch a terminal",
		lambda k: launch(terminal())),
	('%(mod)s-Shift-Return', "Launch a terminal (Large)",
		lambda k: launch(terminal(font = term_large_font))),
	('%(mod)s-Control-Return', "Launch a terminal (Black + White)",
		lambda k: launch(terminal(bw = True))),
	('%(mod)s-Control-Shift-Return', "Launch a terminal (Black, White & Large)",
		lambda k: launch(terminal(bw = True, font = term_large_font))),
	))

keys.bind('main', (
	"Ian's custom key bindings",
	# q is unbound
	('%(mod)s-w', "Launch web browser",
		lambda k: launch(apps.webBrowser)),
	('%(mod)s-e', "Launch email client",
		lambda k: launch(apps.emailClient)),
	('%(mod)s-r', "Launch RSS reader",
		lambda k: launch(apps.RSSReader)),
	# t is wmii key
	('%(mod)s-y', "Launch Python interpreter",
		#lambda k: launch(apps.python)),
		lambda k: launch(apps.python)),
	('%(mod)s-u', "Launch music player",
		lambda k: launch_music_player(apps.musicPlayer)),
	('%(mod)s-i', "Launch IRC client",
		lambda k: launch(apps.IRCClient)),
	('%(mod)s-o', "Launch 2nd music player",
		lambda k: launch_music_player(apps.otherMusicPlayer)),
	# p is wmii key
	# [,] are unbound

	# a is wmii key, mod+shift++a:
	('%(mod)s-Shift-a', "Launch instant messaging client",
		lambda k: launch(apps.IMClient)),
	# s,d,f are wmii keys
	('%(mod)s-g', "Launch calendar",
		lambda k: launch(apps.calendar)),
	# h,j,k,l are wmii keys

	('%(mod)s-z', "Previous Track",
		lambda k: music.command('Previous Track')),
	('%(mod)s-x', "Play",
		lambda k: music.command('Play')),
	('%(mod)s-c', "Play/Pause",
		lambda k: music.command('Play/Pause')),
	('%(mod)s-v', "Stop",
		lambda k: music.command('Stop')),
	('%(mod)s-Shift-v', "Launch VoIP client",
		lambda k: launch(apps.voip)),
	('%(mod)s-b', "Next Track",
		lambda k: music.command('Next Track')),
	('%(mod)s-Shift-b', "Launch bluetooth manager",
		lambda k: launch(apps.bluetoothManager)),

	('%(mod)s-n', "Launch network manager",
		lambda k: launch(apps.networkManager)),
	# , & . are unbound
	('%(mod)s-slash', "Launch calculator",
		lambda k: launch(apps.calculator)),


	('%(mod)s-F3', "Blank Screen Now",
		lambda k: display.blank_screen()),
	('%(mod)s-F4', "Toggle Screen Blanking",
		lambda k: display.toggle_screen_blanking()),
	('%(mod)s-F5', "Change Displays",
		lambda k: display.changeDisplays()),
	))
lock.registerKeyBindings()
resize.register_corner_resize_keys()

# Key $MODKEY-escape
# 	displayStatus Escape
# Key $MODKEY-grave
# 	toggleAutoLock
# Key $MODKEY-F1
# 	toggleAutoSuspend
# # Key $MODKEY-F2 unused
# Key $MODKEY-F3
# 	blankScreen
# Key $MODKEY-F4
# 	toggleScreenBlanking
# #Key $MODKEY-F6
# #	presentationMode
# # Key $MODKEY-F7 unused
# Key $MODKEY-F8
# 	# Same as -
# 	musicPlayerCommand "Volume Down"
# Key $MODKEY-F9
# 	# Same as +
# 	musicPlayerCommand "Volume Up"
# # Key $MODKEY-F10 unused
# # Key $MODKEY-F11 unused
# # Key $MODKEY-F12 unused
# # Key $MODKEY-0-9 are default wmii keys, defined below
# Key $MODKEY-minus
# 	# Same as F8
# 	musicPlayerCommand "Volume Down"
# Key $MODKEY-plus
# 	# Same as F9
# 	musicPlayerCommand "Volume Up"


# Key Caps_Lock
# 	updateCapsLockDisplay
# Key Num_Lock
# 	updateNumLockDisplay

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts







###### NOTE: ALMOST EVERYTHING SHOULD GO ABOVE THIS LINE WITHOUT A GOOD REASON ######
# Apply any local settings
try:
	import plugins.local
except ImportError:
	pass

# Run xdg autostart, we do this after applying local settings to allow local to
# override some settings *before* doing the actual autostart:
import plugins.xdg
plugins.xdg.autostart_once()
