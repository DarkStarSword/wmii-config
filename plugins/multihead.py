#!/usr/bin/env python

from pluginmanager import notify_exception, notify

from pygmi import *

@notify_exception
def recover_lost_windows(args=''):
	import wmiirc
	dest = '0'
	for tag in wmiirc.tags.tags.values():
		for area in tag.index:
			if str(area.screen) in [dest, None]: # None is floating layer (ord='~') TODO: may want to check if they are on screen 0 and re-center them if necessary
				continue
			for frame in area.frames:
				#print 'Moving %s:%s %s %s' % (tag.id, area.screen, frame.client, frame.client.props)
				tag.send(frame.client, "%s:1" % (dest)) # I'm not sure how to verify the next step works, this will at least move it to the right screen
				tag.send(frame.client, "%s:%s" % (dest, area.ord))

def client_area(self, c):
	for l in (l.split(' ') for l in client.readlines('%s/index' % self.path) if l):
		if l[0] == '#':
			continue
		if int(l[1], 16) == c.id:
			return l[0]
	return None

def screen_spec(area_spec):
	if area_spec.find(':') != -1:
		return area_spec.split(':')[0]
	else:
		return 0

def col_spec(area_spec):
	# FIXME: This might not be right... I've seen this script move
	# something that should have been in col 2 into col 3.
	return area_spec.split(':')[-1]

def screen_col_spec(area_spec):
	return '%s:%s' % (screen_spec(area_spec), col_spec(area_spec))

def area_aso(area_spec):
	return (area_spec, screen_spec(area_spec), col_spec(area_spec))

@notify_exception
def send_all_tags(args=''):
	import time

	client = Client(Client('sel').id)
	cur_tag = Tag('sel')
	(area, screen, col) = area_aso(client_area(cur_tag, client))

	all_tags = map(str, range(10))

	selected = {}
	for tag in [ Tag(t) for t in all_tags ]:
		try:
			selected[tag.id] = list(tag.selected)
		except:
			selected[tag.id] = '0:1' # Tag does not exist, make sure default screen is selected
		else:
			selected[tag.id][0] = screen_col_spec(selected[tag.id][0]) # Add '0:' if not already present
			if len(selected[tag.id]) == 1:
				selected[tag.id] = selected[tag.id][0]

	client.tags = '+'.join(all_tags)
	time.sleep(0.1) # Race: give wmii some time to create tags

	for tag in [ Tag(t) for t in all_tags ]:
		if tag == cur_tag:
			continue
		tag.send(client, '%s:1' % screen) # Make sure we at least end up on the right screen
		tag.send(client, area)
		(new_area, new_screen, new_col) = area_aso(client_area(tag, client))

		if new_col < col:
			# Don't try too hard to get the area right - wmii is
			# limited in this respect and I'd be better off
			# spending time in the wmii code.
			tag.send(client, 'right')
			(new_area, new_screen, new_col) = area_aso(client_area(tag, client))

			# Make sure it is still on the correct screen - moving
			# right above may have moved it to the wrong screen if
			# it was the only client in the rightmost column
			if new_screen != screen:
				tag.send(client, '%s:1' % screen)
		tag.selcol.mode = 'default' # I think it is reasonable for most cases
		tag.select(selected[tag.id])

def flash_window(window):
	import time
	for i in range(10):
		window.urgent = True
		time.sleep(0.1)
		window.urgent = False
		time.sleep(0.1)

def _find_window(args='', recover=False):
	# Yes, there are five different "clients" here (hey, I only named two of these!):
	# client = wmii plan9 filesystem client
	# /client = directory in the wmii plan9 filesystem listing all the X11 clients
	# c = A directory in the wmii /client plan9 directory, which refers to an X11 client
	# Client = class representing an X11 client in wmii to abstract the plan9 filesystem interface
	# window = An instantiated Client
	# oh_god_no_more_clients = plea for better naming conventions
	# Tags, Tag & tag = more sensible
	from pygmi import client, Client, Tags, Tag
	import threading

	if not args:
		notify('Usage: find_window title', 'find_window')
		return

	found = False
	for c in client.readdir('/client'):
		window = Client(c.name)
		if window.label.find(args) >= 0:
			if not found:
				found = True
				if recover:
					for tag in window.tags:
						Tag(tag).send(window, "0:1")
				if '+' not in window.tags:
					tag = Tag(window.tags)
					Tags().select(tag)
					tag.selclient = window
					continue
			thread = threading.Thread(target=flash_window, args=(window,), name='flash_window %s' % hex(window.id))
			thread.daemon = True
			thread.start()
	if not found:
		notify('No windows found matching "%s"' % args, 'find_window')

def find_window(args=''):
	return _find_window(args, recover=False)

def recover_window(args=''):
	return _find_window(args, recover=True)

def registerActions():
	import wmiirc
	wmiirc.Actions.recover_lost_windows = recover_lost_windows
	wmiirc.Actions.send_all_tags = send_all_tags
	wmiirc.Actions.find_window = find_window
	wmiirc.Actions.recover_window = recover_window

if __name__ == '__main__':
	import sys
	print "Don't call me directly"
	sys.exit(0)
else:
	registerActions()
