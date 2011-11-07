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
	global background
	background = file if file is not None else background
	if background is None:
		return

	import threading
	t = threading.Thread(target=_set_background)
	t.daemon = True
	t.start()
