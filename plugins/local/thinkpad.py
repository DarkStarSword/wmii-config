from pygmi import *

from pluginmanager import notify, notify_exception
from launch import launch, _launch

keys.bind('main', (
	"ThinkPad specific keys",
	('Mod1-Control-x', "Re-apply X11 settings",
		lambda k: fixX11()),
	))

@notify_exception
def fixX11():
	notify("Applying X11 settings")
	_launch("xinput set-float-prop 'Primax Lenovo Laser Mouse' 'Device Accel Constant Deceleration' 2".split())
	_launch("setxkbmap -option terminate:ctrl_alt_bksp".split())
	_launch("setxkbmap -option keypad:pointerkeys".split())

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts
