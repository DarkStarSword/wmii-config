#!/usr/bin/env python

import subprocess
import pluginmanager

from pluginmanager import notify

timeout = 5
margin = 5

xautolock = None

def selfFile():
	import os
	return os.path.realpath(__file__)

import atexit
@atexit.register # NOTE: Does not handle signals or abnormal process termination
def termAutoLock():
	global xautolock

	if xautolock is not None:
		try:	xautolock.terminate()
		except:	pass
		else:	xautolock.wait()
		xautolock = None

import signal
# TODO: Make this a decorator, I have the feeling I might want to reuse this
def signal_exit(signum, stack):
	import os
	termAutoLock()

	# Restore original handler and resend signal:
	signal.signal(signum, orig_actions[signum])
	os.kill(os.getpid(), signum)
orig_actions = {}
for sig in [signal.SIGTERM, signal.SIGHUP]:
	try:
		orig_actions[sig] = signal.signal(sig, signal_exit)
	except Exception, e:
		notify('WARNING: Lock plugin unable to register signal hander: %s' % e)

def spawnAutoLock():
	import threading
	global xautolock

	termAutoLock()
	xautolock = subprocess.Popen(map(str,['xautolock', '-time', timeout, '-locker',
			selfFile(), '-notify', str(margin), '-notifier', selfFile() + ' -n']))
	# Prevent xautolock becoming a zombie if something kills it:
	# I could also use this to set up any cleanup I might want
	threading.Thread(target = lambda: xautolock.wait(), name='XAutoLock-Waiter').start()

def keepScreenOff(process):
	"""
	Forces the screen off while process is alive
	"""
	import time
	# Give xtrlock a chance to fail so we don't blank the screen if it
	# doesn't start (say if it was already running or was started too soon
	# after changing tags). Also means the user can see the lock appear
	# first:
	time.sleep(0.5)
	while process.poll() is None:
		# TODO: Maybe check that the screen has turned on like I do in
		# the shell version...
		subprocess.call('xset dpms force suspend'.split())
		# TODO: Though it would be nicer to start this delay after the
		# screen comes on instead:
		time.sleep(5)
	process.wait()

def _locknow(daemon = True):
	# NOTE: We are not necessarily in the same process that performed the
	# setup - don't import wmiirc!
	import threading, time
	from pygmi import Tags, keys
	tags = Tags()

	try:
		notify('Locking now', daemon = daemon)

		# Disable keyboard:
		keys.mode = 'passthrough'

		cur = tags.sel # NOTE: Only updated in Tags.__init__()
		tags.select('!lock')

		# xtrlock doesn't seem to like starting if a key that wmii has
		# grabbed is being held down. We change the key mode to
		# passthrough above to remove these grabs, but if the lock key
		# itself has not yet been released that won't help. Sleep here
		# to give the user plenty of time to remove their fingers (at
		# this point we have already switched tags so they have some
		# indication that the screen is about to lock):
		time.sleep(0.5)

		xtrlock = subprocess.Popen('xtrlock')
		#xtrlock = subprocess.Popen('strace xtrlock'.split()) # 'tis difficult to debug

		t = threading.Thread(target = keepScreenOff, args=[xtrlock], name='Keep-Screen-Off')
		t.daemon = True # Don't prevent termination
		t.start()
		# Just in case the user switched tags while we were waiting:
		tags.select('!lock')

		xtrlock.wait()

	finally:
		keys.mode = 'main'
		tags.select(cur)

def locknow(daemon = True):
	import threading
	t = threading.Thread(target = _locknow, name='Lock-Now', kwargs={'daemon': daemon})
	t.daemon = daemon
	t.start()

def enableAutoLock():
	notify('Auto lock enabled', key='lock')
	subprocess.Popen('xautolock -enable'.split()).wait()

def disableAutoLock():
	notify('Auto lock disabled!', key='lock')
	subprocess.Popen('xautolock -disable'.split()).wait()

enabled = True
def toggleAutoLock():
	# XXX No way to know whether we are disabling or enabling if we do this:
	#subprocess.Popen('xautolock -toggle'.split()).wait()
	# So do this instead (Note we won't know about any external changes
	# this way, but it should be good enough):
	global enabled
	if enabled:
		disableAutoLock()
		enabled = False
	else:
		enableAutoLock()
		enabled = True

def registerKeyBindings():
	from pygmi import keys
	keys.bind('main', (
		"Screen Locking",
		('Mod4-grave', "Lock Screen Now",
			lambda k: locknow()),
		('Mod4-shift-grave', "Toggle automatic locking",
			lambda k: toggleAutoLock()),
	))

def registerTraditionalKeyBindings():
	from pygmi import keys
	keys.bind('main', (
		"Screen Locking",
		('Mod1-Control-l', "Lock Screen Now",
			lambda k: locknow()),
		('Mod4-grave', "Toggle automatic locking",
			lambda k: toggleAutoLock()),
		('Mod4-shift-grave', "Toggle automatic locking",
			lambda k: toggleAutoLock()),
	))

keepLockEmptyKey = None
def keepLockEmpty():
	global keepLockEmptyKey
	from pygmi import events, Match, Client
	def retag(event, tag, client):
		print 'retagging', client
		if Client(client).tags != '+/./':
			Client(client).tags = '+'.join(map(str, range(10)))
	if keepLockEmptyKey is not None:
		unload()
	keepLockEmptyKey = Match('ViewAttach', '!lock')
	events.bind({
		keepLockEmptyKey: retag,
		})

def unload():
	global keepLockEmptyKey
	termAutoLock()
	# TODO: Unregister atexit and signal handlers
	if keepLockEmptyKey is not None:
		from pygmi import events
		del events.eventmatchers[keepLockEmptyKey]
		keepLockEmptyKey = None

def main():
	import sys
	def usage():
		print 'usage: %s [-s]' % sys.argv[0]
	if len(sys.argv) > 1:
		if sys.argv[1] == '-s':
			spawnAutoLock()
			registerKeyBindings()
			from pygmi import events
			events.loop() # We are called from the command line to do setup, so start the event loop
			xautolock.wait() # Wait on xautolock since we were called directly from the command line
		elif sys.argv[1] == '-n':
			notify('Screen about to lock...', daemon = False)
		else:
			usage()
	else:
		locknow(False)

if __name__ == '__main__':
	pluginmanager.hack_run_manually()
	main()
else:
	keepLockEmpty()
	spawnAutoLock()
	# registerKeyBindings() # Should be done by wmiirc_local.py
	# We have been imported, so don't wait on xautolock or we will halt execution
