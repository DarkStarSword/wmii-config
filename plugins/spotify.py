#!/usr/bin/env python

import subprocess
import sys
module = sys.modules[__name__]

from pluginmanager import notify_exception
import music
import wmiidbus
import dbus

vol_delta = 0.05

if __name__ == '__main__':
	print "Don't call me directly"
	sys.exit(0)

def unload():
	music.unregister_music_backend('spotify')

_spotify = None
def get_spotify_interface():
	global _spotify

	bus = wmiidbus.get_session_bus()

	if _spotify is not None and bus.name_has_owner(_spotify._named_service):
		return _spotify

	# NOTE: Spotify exports two usable interfaces:
	# org.freedesktop.MediaPlayer2 interface under /
	# org.mpris.MediaPlayer2.Player interface under /org/mpris/MediaPlayer2
	# The latter exports PlaybackStatus, which I don't see an equivelant of
	# in the former. The former does export volume controls, but they don't
	# seem to work for me (possibly because I'm using pulseaudio &
	# bluetooth?)
	_spotify = bus.get_object('com.spotify.qt', '/org/mpris/MediaPlayer2')
	return _spotify

def is_running():
	try:
		spotify = get_spotify_interface()
		return True
	except dbus.DBusException:
		return False

def spotify_info():
	spotify = get_spotify_interface()
	#m = spotify.GetMetadata() # org.freedesktop.MediaPlayer2 API
	m = spotify.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
	return { str(x): str(m[x][0]) if isinstance(m[x], dbus.Array) else str(m[x]) for x in m }

def is_playing():
	try:
		spotify = get_spotify_interface()
		return spotify.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus') == 'Playing'
	except dbus.DBusException:
		return False

def status():
	if is_playing():
		metadata = spotify_info()
		tmp = ''
		if 'xesam:artist' in metadata and metadata['xesam:artist']:
			tmp += '%s ' % metadata['xesam:artist']
			if 'xesam:title' in metadata and metadata['xesam:title']:
				tmp += '- '
		if 'xesam:title' in metadata and metadata['xesam:title']:
			tmp += '%s ' % metadata['xesam:title']
		else:
			tmp += '%s ' % status['url']
		return tmp
		#return '%s[%s/%s]' % (tmp, status['position'], status['duration'])
	return None

def spotify_command(command):
	spotify = get_spotify_interface()
	getattr(spotify, command)()

def spotify_pulse_vol(delta):
	# TODO: If spotify is not connected, redirect command back to mixer
	import pulse
	pulse.PulseAppVolume('Spotify', vol_delta=delta)

def spotify_pulse_mute():
	# TODO: If spotify is not connected, redirect command back to mixer
	import pulse
	pulse.PulseAppVolume('Spotify', toggle_mute=True)

commands = {
	'Play': lambda: spotify_command('Play'),
	'Play/Pause': lambda: spotify_command('PlayPause'),
	'Stop': lambda: spotify_command('Stop'),
	'Previous Track': lambda: spotify_command('Previous'),
	'Next Track': lambda: spotify_command('Next'),
	'Volume Up': lambda: spotify_pulse_vol(vol_delta),
	'Volume Down': lambda: spotify_pulse_vol(-vol_delta),
	'Mute': lambda: spotify_pulse_mute(),
}

music.register_music_backend('spotify', module)
