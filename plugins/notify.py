#!/bin/echo Don't call me directly

# NOTE: We are imported from pluginmanager, so we are not importing pluginmanager

# WARNING: If something else imports us directly, it must ensure it has already
# imported pluginmanager to make sure that pygmi is in the path!

from pygmi import wmii, Colors

# American spelling is only for consistency with other wmii['...colors']:
if 'notifycolors' not in wmii.cache:
	wmii.ctl_types['notifycolors'] = (Colors.from_string, lambda c: str(Colors(*c)))
	wmii['notifycolors'] = '#000000', '#f1f4cb', '#81654f'

if 'errcolors' not in wmii.cache:
	wmii.ctl_types['errcolors'] = (Colors.from_string, lambda c: str(Colors(*c)))
	wmii['errcolors'] = '#ffcc88', '#443322', '#333333'

# Based partly on wmiirc.Notice
from pygmi import Button, wmii
class Notice(Button):
	def __init__(self, key, timeout=5, pos='left', colours='notifycolors'):
		self.key = key
		if isinstance(colours, str):
			colours = wmii.cache[colours]
		self.colours = colours
		self.timeout = timeout
		super(Notice, self).__init__(pos, key, colors=self.colours)
		self.timer = None

	def remove(self):
		with notices_lock:
			# FIXME: There may be a race here - suppose this is
			# waiting on the lock while new_notify is within the
			# critical section - we might prematurely remove the
			# new notice
			if self.key in notices:
				del notices[self.key]
			Button.remove(self)

	def __call__(self, notice, timeout=None, colours=None, **kwargs):
		from threading import Timer
		if self.timer:
			self.timer.cancel()
		colours = colours or self.colours
		if isinstance(colours, str):
			colours = wmii.cache[colours]
		self.create(colours, notice)
		self.timer = Timer(timeout or self.timeout, self.remove)
		self.timer.daemon = True
		self.timer.start()

from threading import Lock
notices = {}
notices_lock = Lock()

def notify(msg, key=None, **kwargs):
	if key is None:
		import time, random
		key = str(time.time()) + str(random.random())
	key = '@notice-%s' % key
	with notices_lock:
		if key in notices:
			notice = notices[key]
		else:
			notice = Notice(key, **kwargs)
			notices[key] = notice
		notice(msg, **kwargs)
	return notice

# This is what I had in __status.py:
# import threading
#
# import wmii
# from util.decorators import singleton
#
# @singleton
# class __clsStatus(object):
#   __runningTimers={}
#   __messages={}
#   __lock = threading.Lock()
#
#   def __init__(self):
#     import wmii.event
#     wmii.event.dispatcher().regExitCallback(self.__exit)
#     #self.display(['test', 'one','two',':)'], timeout=10)
#     #self.display('test', timeout=10)
#     #self.display(['test', 'one','two',':)'], timeout=10, transtime=4)
#
#   def display(self, message, barfile=None, timeout=None,
#       colour=wmii.WMII_NORMCOLOURS, transtime=1):
#     """
#     Display a message for timeout seconds in the wmii bar section barfile.
#
#       message: The message to display
#       barfile: Identify the file in which to place the message as passed to
#                wmiir
#       timeout: Specify time to automatically remove message, or None to
#                indicate the message does not expire
#        colour: Specify a colour string for the message, default WMII
#                colours will be used if none specified
#     """
#     if barfile in self.__runningTimers:
#       self.__runningTimers[barfile].cancel()
#       del self.__runningTimers[barfile]
#
#     with self.__lock:
#       if barfile is None:
#         import time
#         import random
#         barfile = '/lbar/aaa-' + str(time.time()) + str(random.random())
#         if timeout is None:
#           timeout = 5
#
#       if not isinstance(message, list): message = [message]
#       if not isinstance(colour, list): colour = [colour]
#
#       # Concatenate colours and messages
#       messages = [(('' if c is None else c) + ' ' + (message[0] if m is None else m)).strip() \
#           for (c,m) in map(None, colour,message)]
#
#       self.__setMsg(barfile, messages[0])
#
#       if len(message) > 1 or len(colour) > 1:
#         t = threading.Timer(transtime, self.__update, [barfile])
#         self.__messages[barfile] = (0, messages, t, transtime)
#         t.start()
#
#       if timeout is not None:
#         t = threading.Timer(timeout, self.remove, [barfile])
#         t.start()
#         self.__runningTimers[barfile] = t
#
#   def __setMsg(self, barfile, message):
#     wmii.command(barfile, message)
#
#   def __update(self, barfile):
#     with self.__lock:
#       if barfile not in self.__messages: return
#       (n, messages, t, transtime) = self.__messages[barfile]
#       n = (n+1) % len(messages)
#       self.__setMsg(barfile, messages[n])
#       t = threading.Timer(transtime, self.__update, [barfile])
#       self.__messages[barfile] = (n, messages, t, transtime)
#       t.start()
#
#   def __exit(self):
#     timers = self.__runningTimers.keys()
#     for barfile in timers:
#       self.__runningTimers[barfile].cancel()
#       self.remove(barfile)
#       # FIXME: The thread won't go away until it wakes up...
#
#   def remove(self, barfile):
#     with self.__lock:
#       wmii.command(barfile, action='remove')
#       try:
#         del self.__messages[barfile]
#       except: pass #Not flashing, nothing to do
#       del self.__runningTimers[barfile]
