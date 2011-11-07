#!/bin/echo Don't call me directly

from pygmi import *
from pluginmanager import notify, notify_exception

mixer_delta = 2

if __name__ == '__main__':
	import sys
	print "Don't call me directly"
	sys.exit(0)

for mode in keys.modelist:
	keys.bind(mode, ('Multimedia Keys',
		('XF86ScreenSaver',	lambda k: locknow()),
		('XF86Sleep',		lambda k: locknow()),
		('XF86Suspend',		lambda k: locknow()),
		('XF86AudioLowerVolume',lambda k: vol_down()),
		('XF86AudioRaiseVolume',lambda k: vol_up()),
		('XF86AudioMute',	lambda k: vol_mute()),
		('XF86AudioPlay',	lambda k: music("Play/Pause")),
		('XF86AudioPause',	lambda k: music("Play/Pause")),
		('XF86AudioStop',	lambda k: music("Stop")),
		('XF86AudioPrev',	lambda k: music("Previous Track")),
		('XF86AudioNext',	lambda k: music("Next Track")),
		('XF86Calculator',	lambda k: try_launch('calculator')),
		('XF86HomePage',	lambda k: try_launch('webBrowser')),
		('XF86Mail',		lambda k: try_launch('emailClient')),
		('XF86Eject',		lambda k: try_launch('eject')),
		),
		)

#try:
import unload
keys.cleanup()
#except:
	#pass
keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts

def locknow():
	import lock
	lock.locknow()

@notify_exception
def vol(adjust):
	# FIXME: Allow mixer control to be configured
	# FIXME: This is not the same scale as used by alsamixer
	import alsaaudio
	m = alsaaudio.Mixer()
	nv = ov = m.getvolume()[0]
	small_adjust = adjust / abs(adjust)

	v = ov + adjust
	if v > 100: v = 100
	elif v < 0: v = 0

	while nv == ov:
		m.setvolume(v)
		nv = m.getvolume()[0]
		v = v + small_adjust
		if v > 100 or v < 0:
			break
	notify("%s: %d%%" % (m.mixer(), nv), key='mixer')

def vol_up(): return vol(mixer_delta)
def vol_down(): return vol(-mixer_delta)

@notify_exception
def vol_mute():
	# FIXME: Allow mixer control to be configured
	import alsaaudio
	m = alsaaudio.Mixer()
	v = m.getmute()[0]
	v = 0 if v else 1
	m.setmute(v)
	notify("%s: %s" % (m.mixer(), 'off' if m.getmute()[0] else 'on'), key='mixer')

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
# 'XF86TouchpadToggle':	displayStatus 'FIXME: Toggle touchpad'

# 'Caps_Lock':	updateCapsLockDisplay
# 'Num_Lock':	updateNumLockDisplay
