#!/bin/echo Don't call me directly

import pygmi

from pluginmanager import notify

def inthread(name, args, action, **kwargs):
	import inspect
	inthread = pygmi.menu.inthread
	if len(inspect.getargspec(inthread).args) == 3:
		return inthread(name, args, action, **kwargs)
	else:
		return inthread(args, action, **kwargs)

import inspect
if 'prompt' in inspect.getargspec(pygmi.Menu.__init__).args:
	notify('pygmi.Menu appears to support a prompt')
	Menu = pygmi.Menu
else:
	class Menu(pygmi.Menu):
		def __init__(self, choices=(), action=None,
				histfile=None, nhist=None, prompt=None):
			self.prompt = prompt
			return super(Menu, self).__init__(choices, action, histfile, nhist)

		def __call__(self, choices=None, prompt=None):
		    if choices is None:
			choices = self.choices
		    if callable(choices):
			choices = choices()
		    args = ['wimenu']
		    if self.histfile:
			args += ['-h', self.histfile]
		    if self.nhist:
			args += ['-n', self.nhist]
		    if self.prompt or prompt:
			args += ['-p', prompt if prompt is not None else self.prompt]
		    return inthread('Menu', map(str, args), self.action, input='\n'.join(choices))

		call = __call__

# UNTESTED, replace functions rather than subclass:
# XXX Perhaps replace pygmi.Menu with above subclass rather than the functions

# def repl_Menu__init__(self, choices=(), action=None,
#                  histfile=None, nhist=None, prompt=None):
#         self.prompt = prompt
# 	return self.__init____bak__(choices, action, histfile, nhist)
#
# def repl_Menu__call__(self, choices=None, prompt=None):
#     if choices is None:
#         choices = self.choices
#     if callable(choices):
#         choices = choices()
#     args = ['wimenu']
#     if self.histfile:
#         args += ['-h', self.histfile]
#     if self.nhist:
#         args += ['-n', self.nhist]
#     if self.prompt or prompt:
# 	args += ['-p', prompt if prompt is not None else self.prompt]
#     return pygmi.menu.inthread('Menu', map(str, args), self.action, input='\n'.join(choices))
#
# def restore_menu_funcs():
# 	if hasattr(pygmi.Menu, '__init____bak__'):
# 		pygmi.Menu.__init__ = pygmi.Menu.__init____bak__
# 		del pygmi.Menu.__init____bak__
# 	if hasattr(pygmi.Menu, '__call____bak__'):
# 		pygmi.Menu.__call__ = pygmi.Menu.__call____bak__
# 		del pygmi.Menu.__call____bak__
# 		pygmi.Menu.call = pygmi.Menu.__call__
#
# def backup_menu_funcs():
# 	restore_menu_funcs()
# 	pygmi.Menu.__init____bak__ = pygmi.Menu.__init__
# 	pygmi.Menu.__call____bak__ = pygmi.Menu.__call__
#
# def fixup_menu_funcs():
# 	backup_menu_funcs()
# 	pygmi.Menu.__init__ = repl_Menu__init__
# 	pygmi.Menu.__call__ = repl_Menu__call__
# 	pygmi.Menu.call = pygmi.Menu.__call__
