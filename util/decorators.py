#!/usr/bin/env python2.6
# vi:sw=2:ts=2:expandtab

def async(func):
  def wrap(*args, **kwargs):
    import threading
    return threading.Thread(target=func, args=args, kwargs=kwargs).start()
  return wrap

def singleton(self):
  instances = {}
  def getinstance():
    if self not in instances:
      instances[self] = self()
    return instances[self]
  return getinstance
