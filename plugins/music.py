#!/usr/bin/env python

import pluginmanager
from pluginmanager import notify, notify_exception, async

from pygmi import defmonitor, wmii

autoloadMusicBackends = ['moc', 'cmus']
registeredMusicBackends = {}

if __name__ == '__main__':
	import sys
	print "Don't call me directly"
	sys.exit(0)

def unload():
	global registeredMusicBackends
	for module in registeredMusicBackends.values():
		pluginmanager.cleanup_plugin(module)
	try:
		assert(registeredMusicBackends == {})
	finally:
		registeredMusicBackends = {}
		music_status.active = False

@notify_exception
def register_music_backend(name, module):
	assert(name not in registeredMusicBackends)
	registeredMusicBackends[name] = module

@notify_exception
def unregister_music_backend(name):
	if name in registeredMusicBackends:
		del registeredMusicBackends[name]

def music_player_running():
	for (name, module) in registeredMusicBackends.items():
		if module.is_running():
			return (name, module)
	return (None, None)

@async
@notify_exception
def command(command):
	(name, player) = music_player_running()
	if player is None:
		notify('No supported music player running')
		music_status.active = False
		return

	notify('%s: %s' % (name, command), key='music')
	player.commands[command]()

	init_status(player)

@defmonitor
@notify_exception
def music_status(self):
	if not hasattr(self, 'status') or not hasattr(self, 'status_failures'):
		return None # Not initialised yet
	try:
		status = self.status()
	except:
		self.status_failures += 1
		if self.status_failures > 60:
			notify('Too many failures getting music player status')
			self.status_failures = 0
			self.active = False
		return None
	self.status_failures = 0
	if status:
		return wmii['normcolors'], status
	return None
music_status.active = False
music_status.status_failures = 0

@notify_exception
def init_status(player = None):
	if player is None:
		(name, player) = music_player_running()
		if player is None:
			return
	if isinstance(player, str): # launch passes the player name, which may not have finished init yet
		player = registeredMusicBackends[player]

	if hasattr(player, 'status'):
		music_status.status = player.status
		music_status.active = True

def init():
	for plugin in autoloadMusicBackends:
		try: pluginmanager._load_plugin(plugin)
		except: pass

init()
try: init_status()
except: pass
