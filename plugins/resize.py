#!/bin/echo Don't call me directly

from pygmi import keys, Tag

if __name__ == '__main__':
	import sys
	print "Don't call me directly"
	sys.exit(0)

#### OPTION 1: Ctrl grows toward direction, ctrl+shift shrinks from same direction
# Like "normal" wmii resize bindings, but without having to switch to resize mode
def register_normal_resize_keys():
	# Taken from wmiirc.py, but for mode = main
	def addresize(mod, desc, cmd, *args):
	    keys.bind('main', ("Quick Resize",
		(mod + '%(left)s',  "%s selected client to the left" % desc,
		    lambda k: Tag('sel').ctl(cmd, 'sel sel', 'left',
					     *args)),
		(mod + '%(right)s', "%s selected client to the right" % desc,
		    lambda k: Tag('sel').ctl(cmd, 'sel sel', 'right',
					     *args)),
		(mod + '%(up)s',    "%s selected client up" % desc,
		    lambda k: Tag('sel').ctl(cmd, 'sel sel', 'up',
					     *args)),
		(mod + '%(down)s',  "%s selected client down" % desc,
		    lambda k: Tag('sel').ctl(cmd, 'sel sel', 'down',
					     *args)),
	    ))
	addresize('%(mod)s-Control-', 'Grow', 'grow')
	addresize('%(mod)s-Control-Shift-', 'Shrink', 'grow', '-1')

#### OPTION 2: Ctrl grows toward direction, ctrl+shift shrinks from opposite direction
# Shrinking is reversed from wmii normal style so that things move in the
# direction pressed. Depending on context this may make more or less sense,
# overall I would say it isn't really any better than the normal bindings.
def register_swapped_resize_keys():
	keys.bind('main', ("Quick Resize",
		('%(mod)s-Control-%(left)s',  "Grow selected client to the left",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'left')),
		('%(mod)s-Control-%(right)s', "Grow selected client to the right",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'right')),
		('%(mod)s-Control-%(up)s',    "Grow selected client up",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'up')),
		('%(mod)s-Control-%(down)s',  "Grow selected client down",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'down')),

		('%(mod)s-Control-Shift-%(left)s',  "Shrink selected client to the right",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'right', '-1')),
		('%(mod)s-Control-Shift-%(right)s', "Shrink selected client to the left",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'left', '-1')),
		('%(mod)s-Control-Shift-%(up)s',    "Shrink selected client down",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'down', '-1')),
		('%(mod)s-Control-Shift-%(down)s',  "Shrink selected client up",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'up', '-1')),
	))

#### OPTION 3: Ctrl manipulates bottom right corder, ctrl+shift manipulates upper left corner
# Here the controls are re-thought out to be possibly more intuitive - pressing
# left will undo what happened when right was pressed (rather than growing the
# opposite side) and so on.
def register_corner_resize_keys():
	keys.bind('main', ("Quick Resize",
		('%(mod)s-Control-%(left)s',  "Shrink from right",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'right', '-1')),
		('%(mod)s-Control-%(right)s', "Grow to right",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'right')),
		('%(mod)s-Control-%(up)s',    "Shrink from bottom",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'down', '-1')),
		('%(mod)s-Control-%(down)s',  "Grow to bottom",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'down')),

		('%(mod)s-Control-Shift-%(left)s',  "Grow to left",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'left')),
		('%(mod)s-Control-Shift-%(right)s', "Shrink from left",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'left', '-1')),
		('%(mod)s-Control-Shift-%(up)s',    "Grow to top",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'up')),
		('%(mod)s-Control-Shift-%(down)s',  "Shrink from up",
			lambda k: Tag('sel').ctl('grow', 'sel sel', 'up', '-1')),
	));

#### OPTION 4: As 3, but swap corner when requested resizing on an edge (which
#              is unlikely what the user actually wanted to do). This will
#              second guess the user and may make things less consistent, but
#              will usually "do the right thing".
# TODO: Unimplemented

def unbind_keys():
	keys.unbind('main', '%(mod)s-Control-%(left)s')
	keys.unbind('main', '%(mod)s-Control-%(right)s')
	keys.unbind('main', '%(mod)s-Control-%(up)s')
	keys.unbind('main', '%(mod)s-Control-%(down)s')
	keys.unbind('main', '%(mod)s-Control-Shift-%(left)s')
	keys.unbind('main', '%(mod)s-Control-Shift-%(right)s')
	keys.unbind('main', '%(mod)s-Control-Shift-%(up)s')
	keys.unbind('main', '%(mod)s-Control-Shift-%(down)s')

