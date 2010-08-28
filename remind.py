#!/usr/bin/env python2.6
# vi:ts=2:sw=2:expandtab

import subprocess
import threading
import os
import signal

from util.decorators import singleton
import wmii

@singleton
class remind(object):
  __remindprocess = None

  def __init__(self):
    wmii.event.dispatcher().regExitCallback(self.__exit)
    threading.Thread(target=self.__run).start()

  def __run(self):
    self.__remindprocess = subprocess.Popen(['remind', '-z',
      os.path.expanduser('~/.reminders')], stdout=subprocess.PIPE)
    while True:
      line = self.__remindprocess.stdout.readline().strip()
      if line == 'Contents of AT queue:': break
      if line == '': continue
      wmii.status.display("Reminder: "+line, timeout=30,
        colour=[wmii.WMII_MSGCOLOURS, wmii.WMII_MSG1COLOURS])
    self.__remindprocess.wait()
    del self.__remindprocess #FIXME: Should unregister __exit

  def __exit(self):
    print 'terminating remind'
    try:
      self.__remindprocess.send_signal(signal.SIGINT)
    except: pass #FIXME: Should unregister __exit
