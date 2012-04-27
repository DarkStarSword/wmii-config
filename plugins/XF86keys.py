#!/bin/echo Don't call me directly

from pluginmanager import notify, notify_exception
from pygmi import *

if __name__ == '__main__':
	import sys
	print "Don't call me directly"
	sys.exit(0)

for mode in keys.modelist:
	keys.bind(mode, ('Multimedia Keys',
		('XF86ScreenSaver',		lambda k: locknow()),
		('XF86Sleep',			lambda k: locknow()),
		('XF86Suspend',			lambda k: locknow()),
		('XF86AudioLowerVolume',	lambda k: intel_vol('down')),
		('XF86AudioRaiseVolume',	lambda k: intel_vol('up')),
		('XF86AudioMute',		lambda k: intel_vol('mute')),
		('%(mod)s-XF86AudioLowerVolume',lambda k: vol('down')),
		('%(mod)s-XF86AudioRaiseVolume',lambda k: vol('up')),
		('%(mod)s-XF86AudioMute',	lambda k: vol('mute')),
		('%(mod)s-XF86AudioPlay',	lambda k: try_launch('mixer')),
		('%(mod)s-XF86AudioPause',	lambda k: try_launch('mixer')),
		('XF86AudioPlay',		lambda k: music("Play/Pause")),
		('XF86AudioPause',		lambda k: music("Play/Pause")),
		('XF86AudioStop',		lambda k: music("Stop")),
		('XF86AudioPrev',		lambda k: music("Previous Track")),
		('XF86AudioNext',		lambda k: music("Next Track")),
		('XF86Calculator',		lambda k: try_launch('calculator')),
		('XF86HomePage',		lambda k: try_launch('webBrowser')),
		('XF86Mail',			lambda k: try_launch('emailClient')),
		('XF86Eject',			lambda k: try_launch('eject')),
		('XF86TouchpadToggle',		lambda k: toggle_trackpad()),
		),
		)

#try:
import unload
keys.cleanup()
#except:
	#pass
keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts

@notify_exception
def toggle_trackpad():
	import trackpad
	trackpad.toggle_trackpad()

@notify_exception
def locknow():
	import lock
	lock.locknow()

@notify_exception
def vol(command):
	import mixer
	getattr(mixer, 'vol_%s'%command)()

@notify_exception
def intel_vol(command):
	import mixer
	mixer.intel_vol(command)

@notify_exception
def music(command):
	import music
	music.command(command)

@notify_exception
def try_launch(app):
	import launch
	launch.launch(getattr(launch.apps, app))

# 'Shift-XF86AudioLowerVolume':	volumeDown "$VOLUME_MIXER_CONTROL2"
# 'Shift-XF86AudioRaiseVolume':	volumeUp "$VOLUME_MIXER_CONTROL2"
# 'Shift-XF86AudioMute':	volumeMute "$VOLUME_MIXER_CONTROL2"
# '$MODKEY-XF86AudioLowerVolume':	music "Volume Down"
# '$MODKEY-XF86AudioRaiseVolume':	music "Volume Up"
# '$MODKEY-XF86AudioMute':	volumeMute "$VOLUME_MIXER_CONTROL"
# 'XF86Display':	displayStatus `date +"%T"`" XF86Display Pressed" 10

# 'Caps_Lock':	updateCapsLockDisplay
# 'Num_Lock':	updateNumLockDisplay
