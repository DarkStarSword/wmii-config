#!/usr/bin/env python

from pluginmanager import notify_exception

@notify_exception
def dispatch_action(event, action):
	import wmiirc
	wmiirc.Actions._call(action)

actionMatchKey = None
@notify_exception
def register():
	global actionMatchKey
	from pygmi import events, Match
	if actionMatchKey is not None:
		unload()
	actionMatchKey = Match('Action')
	events.bind({
		actionMatchKey: dispatch_action,
		})

def unload():
	global actionMatchKey
	if actionMatchKey is not None:
		from pygmi import events
		del events.eventmatchers[actionMatchKey]
		actionMatchKey = None

def send(*action):
	from pygmi import client
	action = ' '.join(action)
	client.write('/event', 'Action %s' % (action or ''))

if __name__ == '__main__':
	print "Don't call me directly"
else:
	register()
