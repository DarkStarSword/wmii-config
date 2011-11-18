import os

import wmiirc
from pygmi import *

from plugins.launch import launch, launch_music_player, terminal, apps
from plugins import lock, music, unload, resize, display, background

apps.webBrowser		= 'iceweasel'
apps.quickWebBrowser	= terminal('w3m', bw=True)
apps.emailClient	= terminal('sup-mail', bw=True)
apps.RSSReader		= terminal('canto')
apps.python		= terminal('ipython')
apps.musicPlayer	= terminal('cmus')
apps.otherMusicPlayer	= terminal('mocp')
apps.IMClient		= terminal('finch', bw=True)
apps.IRCClient		= terminal('irssi')
apps.calendar		= terminal('wyrd', sleep=True) # Sleep is to avoid race condition triggering bug in wyrd on window resize
apps.networkManager	= terminal('wicd-curses')
apps.calculator		= terminal('calc')
apps.bluetoothManager	= 'blueman-manager'

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

keys.bind('main', (
	"Ian's custom key bindings",
	('%(mod)s-q', "Launch quick web browser",
		lambda k: launch(apps.quickWebBrowser)),
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
	# FIXME: rebind '%(mod)s-a' to mod-shift-a
	# TODO: bind '%(mod)s-a' to finch
	('%(mod)s-Shift-a', "Launch instant messaging client",
		lambda k: launch(apps.IMClient)),
# # Key $MODKEY-a FUNCTIONALITY MOVED TO PYTHON
# 	# launchIMClient
	('%(mod)s-g', "Launch calendar",
		lambda k: launch(apps.calendar)),

	('%(mod)s-z', "Previous Track",
		lambda k: music.command('Previous Track')),
	('%(mod)s-x', "Play",
		lambda k: music.command('Play')),
	('%(mod)s-c', "Play/Pause",
		lambda k: music.command('Play/Pause')),
	('%(mod)s-v', "Stop",
		lambda k: music.command('Stop')),
	('%(mod)s-b', "Next Track",
		lambda k: music.command('Next Track')),
	('%(mod)s-Shift-b', "Launch bluetooth manager",
		lambda k: launch(apps.bluetoothManager)),

	('%(mod)s-n', "Launch network manager",
		lambda k: launch(apps.networkManager)),
	('%(mod)s-slash', "Launch calculator",
		lambda k: launch(apps.calculator)),


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
