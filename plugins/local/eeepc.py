from pygmi import *

from pluginmanager import notify, notify_exception, imported_from_wmiirc

if imported_from_wmiirc():
  import wmiirc
  wmiirc.wmii['font'] = '6x9'
  wmiirc.wmii['fontpad'] = '0 0 -1 -1'

keys.bind('main', (
	"EeePC specific keys",
	('%(mod)s-F1', "Toggle Auto Suspend",
		lambda k: toggle_auto_suspend()),
	))

@notify_exception
def toggle_auto_suspend():
	import os
	file = '/tmp/noautosuspend'
	if os.path.exists(file):
		os.remove(file)
		notify('Auto Suspend Enabled', 'suspend')
	else:
		open(file, 'w').close()
		notify('Auto Suspend Disabled', 'suspend')

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts
