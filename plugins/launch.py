#!/bin/echo Don't run me directly

from pluginmanager import notify, notify_exception, async, imported_from_wmiirc
import pygmi

def replace_call(*args, **kwargs):
    """
    Fixes several issues with pygmi's call function:
    - Passes environment through (fixes ncurses resize)
    - Does not open pipes when launching tasks in the bakground (fixes tasks
      hanging once the stdout/stderr buffers fill up)
    """
    import subprocess
    import os

    background = kwargs.pop('background', False)
    input = kwargs.pop('input', None)
    if background:
        p = subprocess.Popen(args, cwd=os.environ['HOME'],
                             close_fds=True, env=os.environ, **kwargs)
    else:
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=os.environ['HOME'],
                             close_fds=True, env=os.environ, **kwargs)
        return p.communicate(input)[0].rstrip('\n')

pygmi.call = replace_call
from pygmi import call

class terminal(tuple):
	def __new__(self, command = None, bw=False, font = [], sleep=False):
		if imported_from_wmiirc():
			import wmiirc
			term = wmiirc.terminal
		else:
			term = ['wmiir', 'setsid', 'xterm']

		if isinstance(command, str):
			command = [command]
		if isinstance(command, list):
			orig_command = ' '.join(command)
			title = ['-title', orig_command]
			if sleep:
				command[0] = 'sleep 0.1;' + command[0]
			command = ['-e'] + command
		elif command is None:
			orig_command = term[-1]
			title = command = []
		else:
			raise TypeError(type(command))

		colours = '-bg Black -fg White'.split() if bw else ''

		tmp = tuple.__new__(self, list(term) + list(colours) + list(font) + list(title) + list(command))
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
	call(*args, background=background, shell=shell)
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
