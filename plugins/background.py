#!/usr/bin/env python

from pluginmanager import notify, notify_exception

background = None

def restore_wmiirc_setbackground():
	import wmiirc
	if hasattr(wmiirc, 'setbackground__bak__'):
		wmiirc.setbackground = wmiirc.setbackground__bak__
		del wmiirc.setbackground__bak__

def disable_wmiirc_setbackground():
	import wmiirc
	restore_wmiirc_setbackground()
	if hasattr(wmiirc, 'setbackground'):
		wmiirc.setbackground__bak__ = wmiirc.setbackground
	wmiirc.setbackground = lambda *x: None

@notify_exception
def _set_background():
	disable_wmiirc_setbackground()
	try:
		import subprocess
		subprocess.check_call(['feh', '--bg-fill', background])
	except:
		restore_wmiirc_setbackground()
		raise

@notify_exception
def set_background(file = None):
	import os
	global background

	if file is not None and file != '':
		if os.path.isfile(file):
			background = os.path.expanduser(file)
		else:
			notify("set_background: %s not found" % file, 'background')
			return

	if background is None:
		return

	import threading
	t = threading.Thread(target=_set_background, name='Set-X-Background')
	t.daemon = True
	t.start()

def action_set_background(file = ''):
	if file == '':
		if background == None:
			notify('No default background set!', 'background')
			return
		else:
			notify('setting default background...', 'background')
	else:
		notify('setting background to %s...' % file, 'background')
	set_background(file)

if __name__ == '__main__':
	import actions, sys
	actions.send('set_background', *sys.argv[1:])
else:
	import wmiirc
	wmiirc.Actions.set_background = action_set_background
