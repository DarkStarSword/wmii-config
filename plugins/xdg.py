#!/usr/bin/env python

# http://standards.freedesktop.org/autostart-spec/autostart-spec-0.5.html

# NOTE: Importing this plugin does not actually start anything to give the
# importer a chance to update any settings, etc. The importer must run
# autostart_once() when it is ready. Subsequent calls to autostart_once will
# fail, even if this plugin is reloaded!

import pluginmanager
from pluginmanager import notify, notify_exception, persist
import launch

environment_name = 'WMII'
ignore_only_shown_in_environs = []
ignore_only_shown_in_filenames = []

class DesktopFile(dict):
	# http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-1.1.html

	class DesktopFileParseError(Exception): pass

	import re
	_re_groupname = re.compile(r'^\[(?P<name>[^\[\]]*)\]$')
	_re_comment = re.compile(r'^\s*$|^\s*#')
	_re_entry = re.compile(r'^(?P<key>[A-Za-z0-9-]+)(\[(?P<locale>[^\]]*)\])?\s*=\s*(?P<value>.*)$')

	class string(str):
		def __new__(self, val):
			ret = ''
			while val != '':
				(head, sep, val) = val.partition('\\')
				ret = ret + head
				if sep != '\\' or len(val) == 0 or val[0] not in 'sntr\\':
					ret += sep
					continue
				if   val[0] == 's': ret += ' '
				elif val[0] == 'n': ret += '\n'
				elif val[0] == 't': ret += '\t'
				elif val[0] == 'r': ret += '\r'
				elif val[0] == '\\': ret += '\\'
				val = val[1:]
			return ret
	class localestring(str): pass
	class numeric(float): pass
	class strings(list):
		import re
		_re_val_delim = re.compile(r'(?<!\\);')

		def __init__(self, val):
			values = self._re_val_delim.split(val)
			if values[-1] != '':
				raise DesktopFile.DesktopFileParseError('value of type "string(s)" not terminated: %s' % val)
			values.pop()
			values = [ DesktopFile.string(x) for x in values ]
			list.__init__(self, values)
	class localestrings(strings): pass
	def boolean(val):
		if val not in ['true', 'false']:
			raise DesktopFile.DesktopFileParseError('Invalid boolean value: %s' % val)
		return val == 'true'

	key_types = {
		'Type'           : string,
		'Version'        : string,
		'Name'           : localestring,
		'GenericName'    : localestring,
		'NoDisplay'      : boolean,
		'Comment'        : localestring,
		'Icon'           : localestring,
		'Hidden'         : boolean,
		'OnlyShowIn'     : strings,
		'NotShowIn'      : strings,
		'TryExec'        : string,
		'Exec'           : string,
		'Path'           : string,
		'Terminal'       : boolean,
		'Actions'        : strings,
		'MimeTypes'      : strings,
		'Categories'     : strings,
		'Keywords'       : localestrings,
		'StartupNotify'  : boolean,
		'StartupWMClass' : string,
		'URL'            : string,
	}

	required = {
		'Application' : ['Type', 'Name', 'Exec'],
		'Link'        : ['Type', 'Name', 'URL'],
		'Directory'   : ['Type', 'Name'],
	}

	@notify_exception
	def __init__(self, filename):
		f = open(filename)
		groupname = None
		for (lineno, line) in enumerate(map(str.strip, f.readlines())):
			sanity = []
			m = self._re_groupname.match(line)
			if m:
				sanity.append('GROUP NAME')
				groupname = m.groupdict()['name']
				if groupname in self:
					raise self.DesktopFileParseError('%s:%d: Group "%s" already defined' % (filename, lineno, groupname))
				self[groupname] = {}

			m = self._re_entry.match(line)
			if m:
				sanity.append('ENTRY')
				if groupname is None:
					raise self.DesktopFileParseError('%s:%d: "%s" before group name' % (filename, lineno, line))
				g = m.groupdict()
				key = g['key']
				value = g['value']

				# FIXME: Ignoring anything with a locale for now
				if g['locale'] is not None:
					continue

				if key in self[groupname]:
					raise self.DesktopFileParseError('%s:%d: "%s::%s" already defined' % (filename, lineno, groupname, key))

				self[groupname][key] = self.key_types[key](value) if key in self.key_types else self.string(value)

			if self._re_comment.match(line):
				sanity.append('COMMENT')

			if len(sanity) != 1:
				raise self.DesktopFileParseError('%s:%d: "%s" Matched %s' % (filename, lineno, line, ', '.join(sanity) if sanity != [] else None))
		f.close()

		# I'm not checking other actions as I'm not clear on what is or
		# is not required of them.
		required = set(self.required[self['Desktop Entry']['Type']])
		missing = required.difference(self['Desktop Entry'])
		if missing != set():
			raise self.DesktopFileParseError('%s missing required keys: %s' % (filename, ', '.join(missing)))

	# FIXME: TODO... For now, I'll just exec with shell=True which will
	# take care of the quoting... It won't take care of %F, etc. but I
	# don't need them for autostart files.
	# def Exec(self):
	# 	'''
	# 	Parse the exec string into a list suitable for popen
	# 	'''
	# 	# Spec... english... good... yesno?
	# 	# The spec gets a bit confusing here in terms of how things are
	# 	# quoted/escaped. XXX: As a result, this is probably wrong.
	# 	#
	# 	# Note the Exec string is escaped twice - once because it is
	# 	# type string, and here.
	# 	#
	# 	# FIXME: There is also the matter of fields, which I haven't
	# 	# implemented yet.
	# 	exe = self['Desktop Entry']['Exec']

	def __str__(self):
		s = ''
		for g in self:
			s += g + '\n\t'
			s += '\n\t'.join([ '%s: %s' % (x, self[g][x]) for x in self[g] ])
			s += '\n'
		return s

def xdg_config_dirs():
	'''
	Returns a list of xdg config directories in priority order, according to:
	http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html#referencing
	'''
	import os
	dirs = [os.environ['XDG_CONFIG_HOME']] if 'XDG_CONFIG_HOME' in os.environ else ['~/.config']
	dirs += os.environ['XDG_CONFIG_DIRS'].split(':') if 'XDG_CONFIG_DIRS' in os.environ else ['/etc/xdg']
	dirs = map(os.path.expanduser, dirs)
	return dirs

def xdg_files(dirs, pattern):
	'''
	Return files matching pattern in dirs, but if the same match is found
	in multiple dirs, only the highest priority (first) match is returned.
	'''
	import glob, os

	rel_matches = set() # Holds the relative matches without the prefix dir
	for d in dirs:
		matches = set(glob.glob(os.path.join(d, pattern)))
		ignore_matches = [os.path.join(d, m) for m in rel_matches]
		matches = matches.difference(ignore_matches)
		rel_matches.update([os.path.relpath(m, d) for m in matches])
		for m in matches:
			yield m

def autostart_files_iter():
	dirs = xdg_config_dirs()
	files = xdg_files(dirs, 'autostart/*.desktop')
	return files

def autostart():
	import os

	for f in autostart_files_iter():
		try:
			d = DesktopFile(f)
		except Exception, e:
			print '%s while parsing %s: %s' % (e.__class__.__name__, f, str(e))
			continue
		# print d
		d = d['Desktop Entry']
		if 'Hidden' in d and d['Hidden']:
			print 'autostart: Skipping uninstalled %s' % d['Name']
			continue
		if d['Type'] != 'Application':
			print 'autostart: Skipping non-application %s' % d['Name']
			continue
		if 'NotShowIn' in d and environment_name in d['NotShowIn']:
			print 'autostart: Skipping %s which is EXPLICITLY not to be started in %s' % (d['Name'], environment_name)
			continue
		compat_environs = set([environment_name] + ignore_only_shown_in_environs)
		if 'OnlyShowIn' in d \
				and compat_environs.intersection(d['OnlyShowIn']) == set() \
				and os.path.split(f)[1] not in ignore_only_shown_in_filenames:
			print 'autostart: Skipping %s which is implicitly not to be started in %s' % (d['Name'], ', '.join(compat_environs))
			continue
		print 'autostart: Starting %s...' % d['Name']

		# FIXME: shell=True here is lazyness to handle quoted
		# arguments, see above commented out DesktopFile::Exec:
		comm = d['Exec']
		if d['Terminal']:
			comm = launch.terminal(comm)
		launch._launch(comm, shell=True)

@notify_exception
def autostart_once():
	if 'xdg_autostart_run' in persist() and persist()['xdg_autostart_run']:
		print 'xdg_autostart_once already run'
		return
	persist()['xdg_autostart_run'] = True
	autostart()

if __name__ == '__main__':
	pluginmanager.hack_run_manually()
	autostart()
