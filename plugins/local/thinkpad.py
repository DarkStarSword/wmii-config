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

def fix_tray():
	try:
		_launch(wmiirc.tray + ('-SE',))
	except AttributeError:
		notify('Warning: No Tray', 'tray')

def changeDisplays():
	from pluginmanager import Menu
	import background, display
	import subprocess
	profile = Menu(['internal', 'work', 'home', 'xrandr'], prompt='Display Profile:')()
	if profile == 'internal':
		#New nVidia with xrandr 1.2:
		# subprocess.call('xrandr --output LVDS-0 --off           --output DP-1 --mode 1600x1200 --output DP-2 --off'.split())
		# subprocess.call('xrandr --output LVDS-0 --mode 1600x900 --output DP-1 --off            --output DP-2 --off'.split())
		#Old nVidia with metamodes hack:
		# subprocess.call('xrandr -s 1600x900'.split())
		#Nouveau (two steps to work around this can't find crtc for display LVDS-1 bug):
		subprocess.call('xrandr --output DP-1 --off --output DP-2 --off --output DP-3 --off'.split())
		subprocess.call('xrandr --output LVDS-1 --mode 1600x900'.split())
		background.set_background()
		subprocess.call('dispwin -I /home/ian/colorhug/results/w510/w510.icc'.split())
	elif profile == 'work':
		#New nVidia with xrandr 1.2:
		# subprocess.call('xrandr --output LVDS-0 --off           --output DP-1 --mode 1600x1200 --output DP-2 --off'.split())
		# subprocess.call('xrandr --output LVDS-0 --off           --output DP-1 --mode 1600x1200 --output DP-2 --mode 1600x1200 --right-of DP-1'.split())
		#Old nVidia with metamodes hack:
		# subprocess.call('xrandr -s 3200x1200'.split())
		#Nouveau (two steps to work around this can't find crtc for display x bug):
		subprocess.call('xrandr --output LVDS-1 --off --output DP-1 --off'.split())
		subprocess.call('xrandr --output DP-2 --mode 1600x1200 --output DP-3 --mode 1600x1200 --right-of DP-2'.split())
		background.set_background()
		subprocess.call('dispwin -I /home/ian/colorhug/results/left/thinkvision_l.icc'.split())
	elif profile == 'home':
		#Old nVidia with metamodes hack:
		#REMEMBER: Reconfigure meta-modes & associated DPYs first!
		# subprocess.call('xrandr -s 3520x1080'.split())
		#Nouveau (untested,two steps to work around this can't find crtc for display x bug):
		subprocess.call('xrandr --output DP-2 --off --output DP-3 --off'.split())
		subprocess.call('xrandr --output DP-1 --mode 1920x1080 --output LVDS-1 --mode 1600x900 --right-of DP-1'.split())
		background.set_background()
		subprocess.call('dispwin -I /home/ian/colorhug/results/samsung/samsung.icc'.split())
	elif profile == 'xrandr':
		display.changeDisplays()
	fix_tray()

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

fix_tray()
