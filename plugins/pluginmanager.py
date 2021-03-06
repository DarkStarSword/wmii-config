#!/usr/bin/env python

"""
plugin manager
Plugin to manage other plugins, including providing actions to load & reload
plugins, reload wmiirc_local, etc.

Also provides services to plugins, including notice & menus.

Services may be provided by additional plugins if available, or will fall-back
to a simple implementation, so the existence of such services can be relied
upon (provided it is accessed via this plugin).


All plugins are allowed (and expected) to depend on this plugin, but should not
expect other plugins to exist (and should fail gracefully if a plugin they
require does not exist).
"""

import functools

# PLEASE NOTE: The order of functions is important here to get the dependencies
# right & to make sure that any fall backs happen before they are required.

# PLEASE BE CAREFUL IF REFACTORING / REORDERING THIS FILE

def imported_from_wmiirc():
	import sys, os
	return os.path.splitext(os.path.split(sys.modules['__main__'].__file__)[1])[0] == 'wmiirc'

def include_wmiirc_path():
	"""
	This duplicates the functionality in wmiirc to allow wmiirc.py, pygmi
	and pyxp to be imported... Note that it is *NOT* recommended to import
	wmiirc.py (unless imported_from_wmiirc = True), as it lacks the test to
	determine if it is being run directly or imported.
	"""
	if imported_from_wmiirc():
		return
	print 'WARNING: Calling include_wmiirc_path with intent to include wmiirc.py is not recommended'
	import os, sys
	path = []
	for p in os.environ.get("WMII_CONFPATH", "").split(':'):
	    path += [p, p + '/python']
	sys.path = path + sys.path

if not imported_from_wmiirc():
	try:
		import pygmi
		del pygmi
	except ImportError:
		print 'NOTE: pygmi/pyxp not found in PATH - adding WMII_CONFPATH to search path. Be careful if importing wmiirc!'
		include_wmiirc_path()

try:
	from notify import notify
except Exception, e: # Fall back to something sensible
	def notify(msg, *a, **kw):
		from pygmi import client
		client.write('/event', 'Notice %s' % msg) # I'm doing it this way so that things called directly will still work
		class dummy():
			def remove():
				pass
		return dummy
	# If we are being reloaded and notify failed to import, this error
	# would be obscured, so delay it slightly:
	import threading
	t = threading.Timer(0.1, lambda: notify('%s while importing notify: %s' % (e.__class__.__name__, e)))
	t.daemon = True
	t.start()

try: from menu import Menu
except: # Fall back to something sensible. Is there a more concise way of specifying this?
	class Menu(pygmi.Menu):
		def __init__(self, choices=(), action=None, histfile=None, nhist=None, prompt=None):
			return super(Menu, self).__init__(choices, action, histfile, nhist)
		def __call__(self, choices=None, prompt=None):
			return super(Menu, self).__call__(choices)
		call = __call__

def notify_exception(arg):
	"""
	Decorator to catch unhandled exceptions and display some info.
	Exceptions are re-raised to allow normal exception handling to occur.
	"""
	comment = None
	def wrap1(f):
		@functools.wraps(f)
		def wrap2(*args, **kwargs):
			try: return f(*args, **kwargs)
			except Exception, e:
				if hasattr(e, 'notified') and e.notified == True:
					raise # Already notified, just pass back up the stack
				if comment:
					notify('%s %s: %s' % (e.__class__.__name__, comment, e))
				else:
					notify('%s: %s' % (e.__class__.__name__, e))
				e.notified = True # Prevent further notify_exception wrappers from notifying this again
				#raise e # If we have the interpreter up, this will still allow it to print the whole back trace
				raise
		return wrap2
	if isinstance(arg, str):
		comment = arg
		return wrap1
	# No comment was passed in, so we need one less level of indirection
	# (arg is what we are decorating)
	return wrap1(arg)

def async(func):
	@functools.wraps(func)
	def wrap(*args, **kwargs):
		import threading
		return threading.Thread(target=func, args=args, kwargs=kwargs).start()
	return wrap

def hack_run_manually():
	"""
	If a plugin is called directly we will be missing a bunch of config
	that wmiirc.py did. This copies what I need from that config to make
	things work.

	This also creates dummy key bindings for all keys already mapped,
	preventing the script from clearing wmiirc's bindings. Note that this
	is a massive hack - any new bindings will disappear if the real wmiirc
	changes key modes.

	FIXME: This is a hack - we really should use the existing config in
	wmiirc.py, but someone forgot an if __name__ == '__main__'... Then
	again, I suppose it is technically included from wmiirc, not called
	directly, and therefore that check would fail... Better yet, the config
	could have been split from the initialisation out to remove all
	dependencies on wmiirc.py
	"""
	if imported_from_wmiirc():
		return

	from pygmi import wmii, keys, client
	# Keys
	keys.defs = dict(
	    mod='Mod4',
	    left='h',
	    down='j',
	    up='k',
	    right='l')

	wmii['font'] = 'drift,-*-fixed-*-*-*-*-9-*-*-*-*-*-*-*'
	wmii['normcolors'] = '#000000', '#c1c48b', '#81654f'
	wmii['focuscolors'] = '#000000', '#81654f', '#000000'
	wmii['grabmod'] = keys.defs['mod']
	wmii['border'] = 2

	# HACK: Add dummy bindings for existing mappings:
	keys.bind('main', ((b, lambda k: None) for b in client.read('/keys').split()))

def cleanup_plugin(module):
	@notify_exception('while cleaning up plugin')
	def _cleanup_plugin(module):
		if hasattr(module, 'unload') and callable(module.unload):
			module.unload()
	try: _cleanup_plugin(module)
	except: pass

def __load_plugin(plugin):
	import sys
	if plugin in sys.modules:
		module = sys.modules[plugin]
		cleanup_plugin(module)
		reload(module)
		return '%s reloaded' % plugin
	else:
		__import__(plugin)
		return '%s loaded' % plugin

def _load_plugin(args = ''):
	if args.strip() == '':
		notify('usage: load_plugin <plugin>')
		return
	plugin = 'plugins.%s' % args
	return __load_plugin(plugin)

@notify_exception('while loading plugin')
def load_plugin(args = ''):
	notify(_load_plugin(args))

@notify_exception('while reloading wmiirc_local')
def reload_wmiirc_local(args = ''):
	if args.strip() != '':
		notify('WARNING: reload_wmiirc_local unexpected argument: %s, IGNORING' % args)
	notify(__load_plugin('wmiirc_local'))

@notify_exception
def persist():
	'''
	Returns a dictionary suitable for settings that must persist across
	module reloads.

	Currently this creates a fake module named persist that could later be
	imported, but that is an implementation detail - it is recommended to
	always call this function to gain access to the persist object.
	'''
	import sys
	if 'persist' not in sys.modules:
		sys.modules['persist'] = dict()
	return sys.modules['persist']

if __name__ == '__main__':
	import os
	print "To load me without restarting wmii, Hit mod+a and enter: 'eval import plugins.%s'" % \
			os.path.splitext(os.path.split(__file__)[1])[0]
elif imported_from_wmiirc():
	import wmiirc
	wmiirc.Actions.load_plugin = load_plugin
	wmiirc.Actions.reload_wmiirc_local = reload_wmiirc_local
