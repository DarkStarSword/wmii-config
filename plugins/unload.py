#!/usr/bin/env python

if __name__ == '__main__':
	import sys
	print "Don't call me directly"
	sys.exit(0)

def keys_unbind(self, mode, key):
	try: del self.modes[mode]['keys'][key]
	except: pass
	for group in self.modes[mode]['desc']:
		try: self.modes[mode]['desc'][group].remove(key)
		except: pass

def keys_cleanup(self):
	for mode in self.modes:
		for group in self.modes[mode]['desc'].keys():
			for key in self.modes[mode]['desc'][group][:]:
				if self.modes[mode]['keys'][key].__doc__ == '':
					self.modes[mode]['desc'][group].remove(key)
			if self.modes[mode]['desc'][group] == []:
				del self.modes[mode]['desc'][group]
		for group in self.modes[mode]['groups'][:]:
			try:
				if self.modes[mode]['desc'][group] == []:
					self.modes[mode]['groups'].remove(group)
			except:
					self.modes[mode]['groups'].remove(group)

def patch_pygmi():
	import pygmi
	pygmi.event.Keys.unbind = keys_unbind
	pygmi.event.Keys.cleanup = keys_cleanup

patch_pygmi()
