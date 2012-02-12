#!/usr/bin/env python

from pluginmanager import notify_exception

from pygmi import *

@notify_exception
def find_lost_windows(args=''):
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

def area_aso(area_spec):
	return (area_spec, screen_spec(area_spec), col_spec(area_spec))

@notify_exception
def send_all_tags(args=''):
	import time

	client = Client(Client('sel').id)
	(area, screen, col) = area_aso(client_area(Tag('sel'), client))

	all_tags = map(str, range(10))
	client.tags = '+'.join(all_tags)

	time.sleep(0.1) # Race: give wmii some time to create tags

	for tag in [ Tag(t) for t in all_tags ]:
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

def registerActions():
	import wmiirc
	wmiirc.Actions.find_lost_windows = find_lost_windows
	wmiirc.Actions.send_all_tags = send_all_tags

if __name__ == '__main__':
	import sys
	print "Don't call me directly"
	sys.exit(0)
else:
	registerActions()
