#!/usr/bin/env python

from pluginmanager import notify_exception

import readline # For line editing in raw_input

from pygmi import *
from pygmi import event

input_file = '/tmp/debug_wmii_i'
output_file = '/tmp/debug_wmii_o'

@notify_exception
def interpreter():
	import sys,os
	ostdout = sys.stdout
	ostderr = sys.stderr
	os.mkfifo(input_file, 0600) # This will fail if something is already here
	os.mkfifo(output_file, 0600) # which is what we want.
	try:
		sys.stdout = open(output_file, 'w', 0)
		sys.stderr = sys.stdout
		input = open(input_file, 'r')
		cmd = None
		while cmd != '':
			cmd = input.readline()
			try:
				exec cmd
			except Exception, e:
				print 'Remote %s: %s' % (e.__class__.__name__, e)
		input.close()
		sys.stdout.close()
	finally:
		sys.stdout = ostdout
		sys.stderr = ostderr
		try:	os.remove(input_file)
		except:	pass
		try:	os.remove(output_file)
		except: pass

def proxy_process_output(i):
	from select import select
	while True:
		(rlist, wlist, xlist) = select([i], [], [])
		for f in rlist:
			if f == i:
				tmp = f.read(1)
				if tmp == '': return
				sys.stdout.write(tmp)
			else:
				print 'unknown file', f

def proxy():
	import threading
	readline.parse_and_bind('tab: complete')
	readline.parse_and_bind('set editing-mode vi')

	i = open(output_file, 'r', 0)
	o = open(input_file, 'r+', 0) # Want this to fail if the file does not exist
	try:
		t = threading.Thread(target = proxy_process_output, args=[i])
		t.daemon = True
		t.start()
		while t.isAlive():
			tmp = raw_input()
			o.write(tmp + '\n')
		t.join()
	finally:
		i.close()
		o.close()

def action_interpreter(args=''):
	interpreter()

if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1 and sys.argv[1] == '-t':
		interpreter()
		sys.exit(0)
	proxy()
else:
	#interpreter()
	import wmiirc
	wmiirc.Actions.debug_interpreter = action_interpreter
