from pygmi import *

from pluginmanager import notify, notify_exception
from launch import launch, _launch
import wacom
import xdg
import wmiirc

xdg.ignore_only_shown_in_filenames = ['ibm-asset-management.desktop', 'ibm-registration-tool.desktop']

keys.bind('main', (
	"ThinkPad specific keys",
	('Mod1-Control-x', "Re-apply X11 settings",
		lambda k: fixX11()),
	('%(mod)s-F5', "Change Displays",
		lambda k: changeDisplays()),
	))

def changeDisplays():
	from pluginmanager import Menu
	import background, display
	import subprocess
	profile = Menu(['internal', 'work', 'home', 'xrandr'], prompt='Display Profile:')()
	if profile == 'internal':
		#subprocess.call('xrandr --output LVDS-0 --off           --output DP-1 --mode 1600x1200 --output DP-2 --off'.split())
		#subprocess.call('xrandr --output LVDS-0 --mode 1600x900 --output DP-1 --off            --output DP-2 --off'.split())
		subprocess.call('xrandr -s 1600x900'.split())
		background.set_background()
		_launch(wmiirc.tray + ('-SE',))
	elif profile == 'work':
		#subprocess.call('xrandr --output LVDS-0 --off           --output DP-1 --mode 1600x1200 --output DP-2 --off'.split())
		#subprocess.call('xrandr --output LVDS-0 --off           --output DP-1 --mode 1600x1200 --output DP-2 --mode 1600x1200 --right-of DP-1'.split())
		subprocess.call('xrandr -s 3200x1200'.split())
		background.set_background()
		_launch(wmiirc.tray + ('-SE',))
	elif profile == 'home':
		# REMEMBER: Reconfigure meta-modes & associated DPYs first!
		subprocess.call('xrandr -s 3520x1080'.split())
		background.set_background()
		_launch(wmiirc.tray + ('-SE',))
	elif profile == 'xrandr':
		display.changeDisplays()

@notify_exception
def fixX11():
	notify("Applying X11 settings")
	_launch(['xinput', 'set-float-prop', 'Primax Lenovo Laser Mouse', 'Device Accel Constant Deceleration', '2'])
	_launch(['xinput', 'set-float-prop', 'Dell BT Mouse', 'Device Accel Constant Deceleration', '2'])
	_launch("setxkbmap -option terminate:ctrl_alt_bksp".split())
	_launch("setxkbmap -option keypad:pointerkeys".split())

	wacom.apply_profile('Wacom Intuos3 9x12 pad', 'gimp')

fixX11()

keys.mode = keys.mode # Refresh current key bindings - only required when [re]loading plugin after event loop starts

_launch(wmiirc.tray + ('-SE',))
