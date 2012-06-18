#!/bin/echo Don't call me directly

from pluginmanager import notify, notify_exception
from pygmi import *

audio_keys_grabbed = True
volume_keys_grabbed = True

if __name__ == '__main__':
	import sys
	print "Don't call me directly"
	sys.exit(0)

for mode in keys.modelist:
	keys.bind(mode, ('Multimedia Keys',
		('XF86ScreenSaver',		lambda k: locknow()),
		('XF86Sleep',			lambda k: locknow()),
		('XF86Suspend',			lambda k: locknow()),
		('%(mod)s-XF86AudioLowerVolume',lambda k: vol('down')),
		('%(mod)s-XF86AudioRaiseVolume',lambda k: vol('up')),
		('%(mod)s-XF86AudioMute',	lambda k: vol('mute')),
		('%(mod)s-XF86AudioPlay',	lambda k: try_launch('mixer')),
		('%(mod)s-XF86AudioPause',	lambda k: try_launch('mixer')),
		('%(mod)s-Control-XF86AudioPlay',	lambda k: toggle_audio_grab()),
		('%(mod)s-Control-XF86AudioPause',	lambda k: toggle_audio_grab()),
		('%(mod)s-Control-XF86AudioMute',	lambda k: toggle_volume_grab()),
		('XF86Calculator',		lambda k: try_launch('calculator')),
		('XF86HomePage',		lambda k: try_launch('webBrowser')),
		('XF86Mail',			lambda k: try_launch('emailClient')),
		('XF86Eject',			lambda k: try_launch('eject')),
		('XF86TouchpadToggle',		lambda k: toggle_input_device('trackpad')),
		('Shift-XF86TouchpadToggle',	lambda k: toggle_input_device('trackpoint')),
	),)

#try:
import unload
keys.cleanup()
#except:
	#pass

def grab_audio_keys():
	for mode in keys.modelist:
		keys.bind(mode, ('Multimedia Keys',
			('XF86AudioPlay',		lambda k: music("Play/Pause")),
			('XF86AudioPause',		lambda k: music("Play/Pause")),
			('XF86AudioStop',		lambda k: music("Stop")),
			('XF86AudioPrev',		lambda k: music("Previous Track")),
			('XF86AudioNext',		lambda k: music("Next Track")),
		),)
def grab_volume_keys():
	for mode in keys.modelist:
		keys.bind(mode, ('Multimedia Keys',
			('XF86AudioLowerVolume',	lambda k: intel_vol('down')),
			('XF86AudioRaiseVolume',	lambda k: intel_vol('up')),
			('XF86AudioMute',		lambda k: intel_vol('mute')),
		),)
def release_audio_keys():
	for mode in keys.modelist:
		keys.unbind(mode, 'XF86AudioPlay')
		keys.unbind(mode, 'XF86AudioPause')
		keys.unbind(mode, 'XF86AudioStop')
		keys.unbind(mode, 'XF86AudioPrev')
		keys.unbind(mode, 'XF86AudioNext')
def release_volume_keys():
	for mode in keys.modelist:
		keys.unbind(mode, 'XF86AudioLowerVolume')
		keys.unbind(mode, 'XF86AudioRaiseVolume')
		keys.unbind(mode, 'XF86AudioMute')

if audio_keys_grabbed:
	grab_audio_keys()
if volume_keys_grabbed:
	grab_volume_keys()
keys.mode = keys.mode

def toggle_audio_grab():
	global audio_keys_grabbed
	if audio_keys_grabbed:
		notify("Releasing grab on XF86Audio keys")
		release_audio_keys()
	else:
		notify("Grabbing XF86Audio keys")
		grab_audio_keys()
	audio_keys_grabbed = not audio_keys_grabbed
	keys.mode = keys.mode
def toggle_volume_grab():
	global volume_keys_grabbed
	if volume_keys_grabbed:
		notify("Releasing grab on XF86Audio volume keys")
		release_volume_keys()
	else:
		notify("Grabbing XF86Audio volume keys")
		grab_volume_keys()
	volume_keys_grabbed = not volume_keys_grabbed
	keys.mode = keys.mode

@notify_exception
def toggle_input_device(device):
	import trackpad
	getattr(trackpad, 'toggle_%s'%device)()

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
