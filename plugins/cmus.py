#!/usr/bin/env python

import subprocess
import sys
module = sys.modules[__name__]

from pluginmanager import notify_exception
import music

vol_delta = 5

if __name__ == '__main__':
	print "Don't call me directly"
	sys.exit(0)

def unload():
	music.unregister_music_backend('cmus')

def is_running():
	try:
		info = cmus_info()
		return True
	except subprocess.CalledProcessError, e:
		return False
	assert(False)

def cmus_info():
	output = subprocess.check_output('cmus-remote -Q'.split()).split('\n')
	tags = {}
	status = {}
	settings = {}
	for item in map(str.split, output):
		if len(item) > 2 and item[0] == 'tag':
			tags[item[1]] = ' '.join(item[2:])
		elif len(item) > 2 and item[0] == 'set':
			settings[item[1]] = ' '.join(item[2:])
		elif len(item) > 1 and item[0] in 'status file duration position'.split():
			status[item[0]] = ' '.join(item[1:])
	return (status, tags, settings)

def status():
	(status, tags, _) = cmus_info()
	#print (status, tags)
	if status['status'] == 'playing':
		tmp = ''
		if 'artist' in tags and tags['artist']:
			tmp += '%s ' % tags['artist']
			if 'title' in tags and tags['title']:
				tmp += '- '
		if 'title' in tags and tags['title']:
			tmp += '%s ' % tags['title']
		else:
			tmp += '%s ' % status['file']
		return '%s[%s/%s]' % (tmp, status['position'], status['duration'])
	return None

def cmus_command(*args):
	subprocess.check_call(['cmus-remote'] + list(args))

def cmus_vol(delta):
	cmus_command('-v', delta)
	(_, _, settings) = cmus_info()
	l = settings['vol_left']
	r = settings['vol_right']
	if l == r:
		return '%s%%' % l
	return 'L:%s%% R:%s%%' % (l,r)

commands = {
	'Play': lambda: cmus_command('-p'),
	'Play/Pause': lambda: cmus_command('-u'),
	'Stop': lambda: cmus_command('-s'),
	'Previous Track': lambda: cmus_command('-r'),
	'Next Track': lambda: cmus_command('-n'),
	'Volume Up': lambda: cmus_vol('+%i%%' % vol_delta),
	'Volume Down': lambda: cmus_vol('-%i%%' % vol_delta),
}

music.register_music_backend('cmus', module)
