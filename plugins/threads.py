#!/bin/echo Don't call me directly

import threading
import traceback
import sys

def print_tracebacks():
	frames = sys._current_frames()
	for thread in threading.enumerate():
		if True: #thread.is_alive():
			print '\nTraceback for thread [%s] "%s"' % (thread.ident, thread.name)
			traceback.print_stack(frames[thread.ident])
		else:
			print '\nThread [%s] "%s" is not alive' % (thread.ident, thread.name)

class KillThread(object): pass # Does not inherit from Exception to reduce likelihood of being caught

def kill_by_name(name):
	# There is no official way to do this, and forcing the issue can be
	# dangerous is a thread holds the GIL. I would like to be able to do
	# this while debugging though (timers that aren't firing should be
	# safe...). Need to figure out how.
	for thread in threading.enumerate():
		if thread.name == name:
			print 'Killing thread %s' % thread.ident
			#thread._Thread__stop()
			#thread._Thread__delete()

			thread.cancel()
			thread.join()

			# # http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
			# import ctypes
			# res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, ctypes.py_object(KillThread))
			# if res == 0:
			# 	raise ValueError("invalid thread id")
			# elif res != 1:
			# 	# "if it returns a number greater than one, you're in trouble,
			# 	# and you should call it again with exc=NULL to revert the effect"
			# 	ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
			# 	raise SystemError("PyThreadState_SetAsyncExc failed")
