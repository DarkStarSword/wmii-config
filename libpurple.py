#!/usr/bin/env python2.6
# vi:sw=2:expandtab:ts=2

import dbus
import subprocess
import threading
import gobject
from dbus.mainloop.glib import DBusGMainLoop

import globals
import wmii
from util.decorators import singleton

@singleton
class purplelistener(object):
  __mainloop = None
  purple = None

  def __init__(self):
    import wmii.event
    wmii.event.dispatcher().regExitCallback(self.__exit)
    threading.Thread(target=self.__purplelisten).start()

  def __purplelisten(self):
    DBusGMainLoop(set_as_default=True)
    gobject.threads_init()

    self.session_bus = dbus.SessionBus()

    # Add listeners for purple events:
    self.session_bus.add_signal_receiver(self.__ReceiveMsg, 'ReceivedChatMsg', \
        'im.pidgin.purple.PurpleInterface', None, '/im/pidgin/purple/PurpleObject')
    self.session_bus.add_signal_receiver(self.__ReceiveMsg, 'ReceivedImMsg', \
        'im.pidgin.purple.PurpleInterface', None, '/im/pidgin/purple/PurpleObject')

    # This thread goes away to run the main loop:
    self.__mainloop = gobject.MainLoop()
    self.__mainloop.run()

  def __connectProxy(self):
    try:
      obj = self.session_bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
      self.purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
    except:
      self.purple = None

  def __resolveBuddyName(self, account, name, reconnect = False):
    if self.purple is None or reconnect:
      self.__connectProxy()

    try:
      buddy = self.purple.PurpleFindBuddy(account, name)
      if buddy != 0: return self.purple.PurpleBuddyGetAlias(buddy)
      else: return name
    except:
      if reconnect: return name
      else: return self.__resolveBuddyName(account, name, True)

  def __ReceiveMsg(self, account, name, message, conversation, flags):
    alias = self.__resolveBuddyName(account, name)

    import util.html
    wmii.status.display("%s: %s" % (alias, util.html.strip_html(message)),
        barfile='/rbar/afinch-'+name, timeout=5,
        colour=[wmii.WMII_MSGCOLOURS, wmii.WMII_MSG1COLOURS])

  def __exit(self):
    self.__mainloop.quit()

@singleton
class finch(object):
  __finchprocess = None

  def run(self):
    # FIXME: Detect finch already running launched elsewhere
    if self.__finchprocess is None:
      threading.Thread(target=self.__run).start()
    else:
      wmii.status.display('Finch already running...')

  def __run(self):
    try:
      self.__finchprocess = subprocess.Popen([globals.term, '-e', 'finch']) 
    except:
      wmii.status.display('Failed to execute finch')
    else:
      purplelistener()
      threading.Thread(target=self.__waitOnFinch).start()

  def __waitOnFinch(self):
    self.__finchprocess.wait()
    self.__finchprocess = None

if __name__ == '__main__':
  finch().run()
