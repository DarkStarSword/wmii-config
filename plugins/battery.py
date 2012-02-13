#!/bin/echo Don't call me directly

from pluginmanager import notify_exception
from pygmi import defmonitor, wmii

sysdir='/sys/class/power_supply/BAT0'

def set_unknown_anim_colours(state, percent):
	# TODO: This only has to be run when the state or percent changes
	if percent <= 5:
		# We don't know the state, so we don't know if we are on
		# battery or not, play it safe since we are low:
		s = '[%s / critical]' % state.lower()
		anim['unknown'] = [ s, s.upper() ]
		colours['unknown'] = colours['critical']
	elif percent <= 15:
		s = '[%s / warning]' % state.lower()
		anim['unknown'] = [ s, s.upper() ]
		colours['unknown'] = colours['warning']
	else:
		# The state may be important, but it might not be...  We have
		# charge, so make it animate to draw some attention, but try
		# not to be too distracting
		s = '[%s]' % state.lower()
		anim['unknown'] = [ s[:i/2] + s.upper()[i/2] + s[i/2+1:]  for (i, c) in enumerate(''.join([ c*2 for c in s])) ]
		colours['unknown'] = [wmii['focuscolors']]*2 + [wmii['normcolors']]*(len(s)*2-4) + [wmii['focuscolors']]*2

anim = {
	'full':	[":-)"]*4 + [";-)"],
	'charging': ["___", "_-_", "_+_", "-+-", "+++", "+^+"] + ["^^^"]*3,
	'discharging': ["---", "_--", "__-"] + ["___"]*3,
	'warning': ["!---!", "!_--!", "!__-!"] + ["!___!"]*3,
	'critical': ["!'''!", "!!!!!"],
	# 'unknown' defined in code above
}

colours = {
	'full': ('#88bb88', '#223322', '#333333'),
	'charging': wmii['normcolors'],
	'discharging': wmii['normcolors'],
	'warning': ('#ffcc88', '#222222', '#333333'),
	'critical': [('#888888', '#442222', '#333333'), ('#ffcc88', '#443322', '#333333')],
	# 'unknown' defined in code above
}

def read(file):
	# TODO: Can we re-use file descriptors to reduce syscalls & context switching?
	fp = open(file, 'r')
	ret = fp.read().strip()
	fp.close()
	if ret.isdigit():
		return int(ret)
	return ret

def sysfs_read(*args):
	import os
	for file in args:
		try:
			return read(os.path.join(sysdir, file))
		except:
			pass
	raise IOError(args)

phase = -1
cphase = -1
@defmonitor
@notify_exception
def battery(self):
	global phase, cphase

	# TODO: This is based on the bash logic on my thinkpad, but I can't
	# recall which one I re-wrote - it may have been the dell...
	chargingstate = sysfs_read('status')
	remainingcapacity = sysfs_read('charge_now', 'energy_now')
	designcapacity = sysfs_read('charge_full_design', 'energy_full_design')
	lastfullcapacity = sysfs_read('charge_full', 'energy_full')
	voltage = sysfs_read('voltage_now')
	current = sysfs_read('current_now', 'power_now')

	presentrate = voltage * current / 1000000000000

	#percent = remainingcapacity * 100 / designcapacity
	percent = remainingcapacity * 100 / lastfullcapacity

	seconds = 0
	if chargingstate == "Discharging":
		if current:
			seconds = remainingcapacity * 60 * 60 / current
		if percent <= 5:	state = 'critical'
		elif percent <= 15:	state = 'warning'
		else:			state = 'discharging'
	elif chargingstate == "Charging":
		if current:
			seconds = (lastfullcapacity - remainingcapacity) * 60 * 60 / current
		if percent == 100:	state = 'full' # or as good as
		else:			state = 'charging'
	elif chargingstate == "Full":
		state = 'full'
	else:
		state = 'unknown'
		set_unknown_anim_colours(chargingstate, percent)

	state_anim = anim[state]
	state_colours = colours[state]

	phase = (phase + 1) % len(state_anim)
	if isinstance(state_colours, list):
		cphase = (cphase + 1) % len(state_colours)
		state_colours = state_colours[cphase]

	if state.lower() not in ['full', 'unknown']:
		hours = seconds / 60 / 60
		minutes = seconds / 60 % 60
		seconds = seconds % 60
		eta = '(%i:%.2i:%.2i @ %iW) ' % (hours, minutes, seconds, presentrate)
	else:
		eta = ''

	return state_colours, '%i%% %s%s' % (percent, eta, state_anim[phase])
