#!/bin/echo Don't run me directly

from pluginmanager import notify, notify_exception, async, imported_from_wmiirc

from pygmi import call

class terminal(tuple):
	def __new__(self, command, bw=False, sleep=False):
		if imported_from_wmiirc():
			import wmiirc
			term = wmiirc.terminal
		else:
			term = ['wmiir', 'setsid', 'xterm']
		# sleep = True # wtf is going on? Today just about everything needs this workaround to get the size right initially and doesn't resize properly, partially fixed by unset ROWS and COLUMNS in .zshenv

		if isinstance(command, str):
			command = [command]
		if isinstance(command, list):
			orig_command = command[:]
			if sleep:
				command[0] = 'sleep 0.1;' + command[0]
		else:
			raise TypeError(type(command))

		colours = '-bg Black -fg White'.split() if bw else ''
		orig_command = ' '.join(orig_command)

		tmp = super(self, terminal).__new__(self, list(term) + list(colours) + ['-title', orig_command, '-e'] + list(command))
		tmp.command = orig_command
		return tmp

	def __str__(self):
		return self.command

@async
@notify_exception
def _launch(args, background=True, shell=False):
	import os
	if type(args) == str:
		args = ('wmiir', 'setsid', args)
	if shell:
		args = (' '.join(args),)
	call(*args, background=background, env=os.environ, shell=shell) # Passing os.environ fixes the LINES/COLUMNS bug... wtf?
	# FIXME: Report missing apps - NOTE: xterm would always launch (and
	# pygmi.call doesn't report failure), so I should actually check for
	# existance

@notify_exception
def launch(args, background=True):
	if type(args) == list:
		notify('Launching %s...' % ' '.join(args))
	else:
		notify('Launching %s...' % args.__str__())
	return _launch(args, background)

@notify_exception
def launch_music_player(args, background = True):
	launch(args, background)
	import music
	music.init_status(str(args))

class apps(object):
	eject = 'eject'
