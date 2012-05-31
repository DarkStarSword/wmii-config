#!/usr/bin/env python

from pluginmanager import notify, notify_exception

import wmiidbus
import dbus
import dbus.service

class libnotify(dbus.service.Object):
	@notify_exception
	def __init__(self, bus):
		bus_name = dbus.service.BusName('org.freedesktop.Notifications', bus = bus)
		dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/Notifications')

	@dbus.service.method(dbus_interface='org.freedesktop.Notifications',
			     in_signature='susssasa{sv}i', out_signature='u')
	# @notify_exception #dbus.service.method inspects the passed function, which doesn't work with this
	def Notify(self, app_name, id, icon, summary, body, actions, hints, timeout):
		print 'Notify: [%d] app_name: %s, icon: %s, actions: %s, hints: %s' % (id, app_name, icon, repr(actions), repr(hints))
		if not timeout:
			notify('libnotify called with timeout %s' % repr(timeout))
			timeout = 5000
		notify('%s: %s' % (summary, body), timeout = timeout / 1000.0, colours='msgcolors')
		return 0

	@dbus.service.method(dbus_interface='org.freedesktop.Notifications',
			     out_signature='ssss')
#       <arg name="return_name" type="s" direction="out"/>
#       <arg name="return_vendor" type="s" direction="out"/>
#       <arg name="return_version" type="s" direction="out"/>
#       <arg name="return_spec_version" type="s" direction="out"/>
	# @notify_exception #dbus.service.method inspects the passed function, which doesn't work with this
	def GetServerInformation(self):
		notify('libnotify.py: Untested GetServerInformation called')
		return ('wmii', 'Ian Munsie', '0.1', None)

	@dbus.service.method(dbus_interface='org.freedesktop.Notifications',
			     out_signature='as')
#       <arg name="return_caps" type="as" direction="out"/>
	# @notify_exception #dbus.service.method inspects the passed function, which doesn't work with this
	def GetCapabilities(self):
		notify('libnotify.py: Unimplemented GetCapabilities called')
		return []

	@dbus.service.method(dbus_interface='org.freedesktop.Notifications',
			     in_signature='u')
	# @notify_exception #dbus.service.method inspects the passed function, which doesn't work with this
	def CloseNotification(self, id):
		notify('libnotify.py: Unimplemented CloseNotification called')

_notify = None

@notify_exception
def main():
	global _notify

	session_bus = wmiidbus.get_session_bus()

	_notify = libnotify(session_bus)

def unload():
	global _notify

	notify('WARNING: libnotify.py unload called, but is unimplemented!')
	# XXX TODO: disconnect from bus
	_notify = None

main()


# Should look like:
# u'<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
# "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
# <node>
#   <interface name="org.freedesktop.DBus.Introspectable">
#     <method name="Introspect">
#       <arg name="data" direction="out" type="s"/>
#     </method>
#   </interface>
#   <interface name="org.freedesktop.DBus.Properties">
#     <method name="Get">
#       <arg name="interface" direction="in" type="s"/>
#       <arg name="propname" direction="in" type="s"/>
#       <arg name="value" direction="out" type="v"/>
#     </method>
#     <method name="Set">
#       <arg name="interface" direction="in" type="s"/>
#       <arg name="propname" direction="in" type="s"/>
#       <arg name="value" direction="in" type="v"/>
#     </method>
#     <method name="GetAll">
#       <arg name="interface" direction="in" type="s"/>
#       <arg name="props" direction="out" type="a{sv}"/>
#     </method>
#   </interface>
#   <interface name="org.freedesktop.Notifications">
#     <method name="GetServerInformation">
#       <arg name="return_name" type="s" direction="out"/>
#       <arg name="return_vendor" type="s" direction="out"/>
#       <arg name="return_version" type="s" direction="out"/>
#       <arg name="return_spec_version" type="s" direction="out"/>
#     </method>
#     <method name="GetCapabilities">
#       <arg name="return_caps" type="as" direction="out"/>
#     </method>
#     <method name="CloseNotification">
#       <arg name="id" type="u" direction="in"/>
#     </method>
#     <method name="Notify">
#       <arg name="app_name" type="s" direction="in"/>
#       <arg name="id" type="u" direction="in"/>
#       <arg name="icon" type="s" direction="in"/>
#       <arg name="summary" type="s" direction="in"/>
#       <arg name="body" type="s" direction="in"/>
#       <arg name="actions" type="as" direction="in"/>
#       <arg name="hints" type="a{sv}" direction="in"/>
#       <arg name="timeout" type="i" direction="in"/>
#       <arg name="return_id" type="u" direction="out"/>
#     </method>
#   </interface>
# </node>
# '
