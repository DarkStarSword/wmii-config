#!/usr/bin/env python2.6
# vi:sw=2:ts=2:expandtab

import subprocess
import traceback
from util.decorators import async
from util.decorators import singleton
import wmii

@singleton
class dispatcher(object):
  __wmiiEvents = None
  __registeredSpecificEvents = {}
  __exitCallbacks = []
  __keys = []
  __running = True

  def __init__(self):
    import signal
    signal.signal(signal.SIGINT, self.__SIGINT)

    self.__wmiiEvents = subprocess.Popen(['wmiir', 'read', '/event'], stdout=subprocess.PIPE)
    # FIXME: Test outcome (failure unlikely given we are typically run by wmiirc)
    # FIXME: Use python 9p instead

  def regKeyHandler(self, key, callback, async=False):
    self.__addkey(key)
    self.regSpecificEvent('Key '+key, callback, async)

  def regExitCallback(self, callback):
    self.__exitCallbacks.append(callback)

  def regSpecificEvent(self, event, callback, async=False):
    if event not in self.__registeredSpecificEvents:
      self.__registeredSpecificEvents[event] = []
    self.__registeredSpecificEvents[event].append((callback, async))

  def mainloop(self):
    import wmii
    while self.__running:
      event = self.__readevent()
      if event == 'Start wmiirc' or not self.__wmiiRunning():
        self.__dispatchExit()
        return
      self.__dispatch(event)

  def waitForEvent(self, event):
    while self.__readevent() != event: pass

  def __readevent(self):
    return self.__wmiiEvents.stdout.readline().strip()
  
  def __wmiiRunning(self):
    return self.__wmiiEvents.poll() == None


  def __dispatch(self, event):
    if event in self.__registeredSpecificEvents:
      for (callback, asyn) in self.__registeredSpecificEvents[event]:
        try:
          if asyn:
            async(callback(event))
          else:
            callback(event)
        except:
          msg = traceback.format_exc()
          wmii.dispLongMsg("Exception in wmii callback:\n"+msg)

  def __dispatchExit(self):
    self.__running = False
    for c in self.__exitCallbacks:
      try: c()
      except:
        msg = traceback.format_exc()
        wmii.dispLongMsg("Exception in wmii exit callback:\n"+msg)

  def __SIGINT(self, num, frame):
    self.__dispatchExit()
    raise KeyboardInterrupt

  def __addkey(self, key):
    key += '\n'
    if not key in self.__keys:
      self.__keys.append(key)
      self.regKeys()

  def readWmiiKeys(self):
    wmiir = subprocess.Popen(['wmiir', 'read', '/keys'], stdout=subprocess.PIPE)
    self.__keys = wmiir.stdout.readlines()
    wmiir.wait()

  def regKeys(self):
    wmiir = subprocess.Popen(['wmiir', 'write', '/keys'], stdin=subprocess.PIPE)
    wmiir.stdin.writelines(self.__keys)
    wmiir.stdin.close()
    wmiir.wait()
