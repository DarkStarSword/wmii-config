#!/bin/echo Don't run me directly

trackpad = 'SynPS/2 Synaptics TouchPad' # HACK HACK HACK
enabled_prop = 'Device Enabled' # XXX Is this a standard name?

import re
xinput_prop_spec = re.compile(r'''\s*(?P<prop_name>.+)\s\(\d+\):\s*(?P<val>\S)$''') # XXX This will break if parentheses can be in the value...
def get_xinput_prop(device, prop):
	import subprocess # TODO: Is there a python interface to xinput?
	xinput = subprocess.Popen(['xinput', '--list-props', device], stdout=subprocess.PIPE)
	for line in xinput.stdout:
		match = xinput_prop_spec.match(line)
		if not match:
			continue
		groups = match.groupdict()
		if groups['prop_name'] == prop:
			return groups['val']
	raise KeyError("Property not found in xinput's output")

def set_xinput_prop(device, prop, val):
	import subprocess # TODO: Is there a python interface to xinput?
	subprocess.check_output(map(str, ['xinput', '--set-prop', device, prop, val]))

def disable_trackpad():
	set_xinput_prop(trackpad, enabled_prop, 0)

def enable_trackpad():
	set_xinput_prop(trackpad, enabled_prop, 1)

def toggle_trackpad():
	enabled = int(get_xinput_prop(trackpad, enabled_prop))
	if enabled:
		disable_trackpad()
	else:
		enable_trackpad()
