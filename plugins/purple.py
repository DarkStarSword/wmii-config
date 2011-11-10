#!/usr/bin/env python

import dbus
import subprocess
import gobject
from dbus.mainloop.glib import DBusGMainLoop

from pluginmanager import notify, notify_exception
from pygmi import wmii

# American spelling is only for consistency with other wmii['...colors']:
if 'msgcolors' not in wmii.cache:
	wmii['msgcolors'] = '#FFFFFF', '#2222FF', '#333333'
	# TODO: Animate once notify supports this
	#wmii['msgcolors'] = [('#FFFFFF', '#2222FF', '#333333'), ('#000088', '#8888FF', '#CCCCFF')]

##
# Removes HTML markup from a text string.
#
# @param text The HTML source.
# @return The plain text.  If the HTML source contains non-ASCII
#     entities or character references, this is a Unicode string.
#
# Code in public domain from:
# http://effbot.org/zone/re-sub.htm
def strip_html(text):
    import re
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            import htmlentitydefs
	    htmlentitydefs.entitydefs['apos'] = "'"
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is
    return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)

_thread = None
_purple = None
_mainloop = None
_session_bus = None

def connect_proxy():
	global _purple
	try:
		obj = _session_bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
		_purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
	except:
		_purple = None

def resolve_buddy_name(account, name, reconnect = False):
	if _purple is None or reconnect:
		connect_proxy()

	try:
		buddy = _purple.PurpleFindBuddy(account, name)
		if buddy != 0: return _purple.PurpleBuddyGetAlias(buddy)
		else: return name
	except:
		if reconnect: return name
		else: return resolve_buddy_name(account, name, reconnect = True)

@notify_exception
def receive_msg(account, name, message, conversation, flags):
  alias = resolve_buddy_name(account, name)

  #notify("%s: %s" % (alias, strip_html(message)), key='purple-'+name, colours=[wmii.WMII_MSGCOLOURS, wmii.WMII_MSG1COLOURS])
  notify("%s: %s" % (alias, strip_html(message)), key='purple-'+name, colours='msgcolors')

def add_listeners(bus):
	bus.add_signal_receiver(receive_msg, 'ReceivedChatMsg', \
	    'im.pidgin.purple.PurpleInterface', None, '/im/pidgin/purple/PurpleObject')
	bus.add_signal_receiver(receive_msg, 'ReceivedImMsg', \
	    'im.pidgin.purple.PurpleInterface', None, '/im/pidgin/purple/PurpleObject')

@notify_exception
def main():
	global _mainloop, _session_bus

	DBusGMainLoop(set_as_default=True)
	gobject.threads_init()

	_session_bus = dbus.SessionBus()

	add_listeners(_session_bus)

	# This thread goes away to run the main loop:
	_mainloop = gobject.MainLoop() # FIXME: It may not be wise to use the glib main loop, how does it work if I have multiple instances?
	_mainloop.run()


def load():
	import threading
	global _thread
	_thread = threading.Thread(target=main, name='Purple-Dbus-Listener')
	_thread.daemon = True
	_thread.start()

def unload():
	global _purple
	_mainloop.quit()
	_session_bus.close()
	_thread.join()
	_purple = None

load()
