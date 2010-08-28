#!/usr/bin/env python
# vi:expandtab:ts=2:sw=2

import subprocess
import re

WMII_NORMCOLOURS_TEXT        = '#888888'
WMII_NORMCOLOURS_BACKGROUND  = '#222222'
WMII_NORMCOLOURS_BORDER      = '#333333'
WMII_NORMCOLOURS = WMII_NORMCOLOURS_TEXT \
          + ' ' + WMII_NORMCOLOURS_BACKGROUND \
          + ' ' + WMII_NORMCOLOURS_BORDER
WMII_FOCUSCOLOURS_TEXT       = '#ffffff'
WMII_FOCUSCOLOURS_BACKGROUND = '#285577'
WMII_FOCUSCOLOURS_BORDER     = '#4c7899'
WMII_FOCUSCOLOURS = WMII_FOCUSCOLOURS_TEXT \
           + ' ' + WMII_FOCUSCOLOURS_BACKGROUND \
           + ' ' + WMII_FOCUSCOLOURS_BORDER
WMII_ERRCOLOURS_TEXT        = '#ffcc88'
WMII_ERRCOLOURS_BACKGROUND  = '#443322'
WMII_ERRCOLOURS_BORDER      = '#333333'
WMII_ERRCOLOURS = WMII_ERRCOLOURS_TEXT \
          + ' ' + WMII_ERRCOLOURS_BACKGROUND \
          + ' ' + WMII_ERRCOLOURS_BORDER

WMII_BACKGROUND='#333333'
WMII_FONT='fixed'

# Internal display should start with this string from xrandr:
INTERNAL_DISPLAY='LVDS'

def WMII_MENU(items, prompt=None):
  """
  Port of the standard wmii menu using dmenu
  """
  command = ['dmenu', '-b', '-fn', WMII_FONT, '-nf', WMII_NORMCOLOURS_TEXT,
      '-nb', WMII_NORMCOLOURS_BACKGROUND, '-sf', WMII_FOCUSCOLOURS_TEXT, '-sb',
      WMII_FOCUSCOLOURS_BACKGROUND]
  if prompt is not None:
    command += ['-p', prompt]
  p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  for item in [(x + '\n').encode() for x in items]:
    p.stdin.write(item)
  p.stdin.close()
  result = p.stdout.read().decode()
  p.wait()
  return result

def wmiiCommand(file, command=None, action='create'):
  p = subprocess.Popen(['wmiir', action, file], stdin=subprocess.PIPE)
  if command is not None:
    p.stdin.write(command.encode())
    p.stdin.close()
  p.wait()

class __clsStatus(object):
  __runningTimers={}

  def display(cls, message, barfile=None, timeout=None,
      colour=WMII_NORMCOLOURS):
    """
    Display a message for timeout seconds in the wmii bar section barfile.

      message: The message to display
      barfile: Identify the file in which to place the message as passed to
               wmiir
      timeout: Specify time to automatically remove message, or None to
               indicate the message does not expire
       colour: Specify a colour string for the message, default WMII
               colours will be used if none specified
    """
    if barfile is None:
      import time
      import random
      barfile = '/lbar/aaa-' + str(time.time()) + str(random.random())
    if barfile in cls.__runningTimers:
      cls.__runningTimers[barfile].cancel()

    wmiiCommand(barfile, colour + ' ' + message)

    if timeout is not None:
      import threading
      t = threading.Timer(timeout, cls.remove, [barfile])
      t.start()
      cls.__runningTimers[barfile] = t

  def remove(cls, barfile):
    wmiiCommand(barfile, action='remove')

  def __timerExpire(cls, barfile):
    cls.remove(barfile)
    del cls.__runningTimers[barfile]

status = __clsStatus()

def __disableXAutoLock():
  subprocess.call(['xautolock', '-disable'])

def disableXAutoLock():
  subprocess.call(['xautolock', '-disable'])

  # FIXME: Race condition with restarting wmii
  import threading
  t = threading.Timer(5, __disableXAutoLock)
  t.start()

def enableXAutoLock():
  subprocess.call(['xautolock', '-enable'])

def disableScreenBlanking():
  subprocess.call(['xset', 's', 'off'])
  subprocess.call(['xset', '-dpms'])

def enableScreenBlanking():
  subprocess.call(['xset', 's', 'on'])
  subprocess.call(['xset', '+dpms'])

def isInternalDisplay(display):
  return display.startswith(INTERNAL_DISPLAY)

def enumerateDisplays():
  """
  Enumerate connected displays and supported resolutions
  Returns:
  * A dictionary of connected Displays and the resolutions they support
  * A list of tuples of currently active displays and their current resolution
  * A dictionary of disconnected displays (no resolution)
  * The display device that is believed to be the internal display, if any
  """
  displays = {}
  disabledDisplays = {}
  device = None
  activeDisplays = []
  internalDisplay = None
  xrandr = subprocess.Popen('xrandr', stdout=subprocess.PIPE)
  for line in [x.decode() for x in xrandr.stdout.readlines()]:
    match = re.match('(?P<device>[\w-]+) (?P<disconnected>dis)?connected ', line)
    if match:
      device = match.group('device')
      if isInternalDisplay(device):
        internalDisplay = device
      if match.group('disconnected') is not None:
        device = None
        disabledDisplays[match.group('device')] = []
      else:
        displays[device] = []
    elif device is not None:
      match = re.match(' +(?P<resolution>\w+)', line)
      if match:
        resolution = match.group('resolution')
        displays[device].append(resolution)
        if line.find('*') != -1:
          activeDisplays += [(device, resolution)]
  xrandr.wait()
  return (displays, activeDisplays, disabledDisplays, internalDisplay)

def intersectResolutions(displays):
  """
  Find the subset of resolutions supported by all displays
  """
  intersect = None
  for display in displays:
    resolutions = displays[display]
    if intersect is None:
      intersect = resolutions
    else:
      intersect = [r for r in resolutions if r in intersect]
  return intersect

def largestResolution(resolutions):
  """
  Return the largest resolution in the list.
  STUB: Assumes the first entry is the largest, as if outputted by xrandr
  """
  return resolutions[0]

def setResolution(devices, resolution, internalDisplay, disabledDevices = None,
    layout=None):
  """
  Call xrandr to set the resolution of all given devices to resolution
  """
  command=['xrandr']
  for device in devices:
    command += ['--output', device, '--mode', resolution]
    if layout is None or isInternalDisplay(device):
      command += ['--pos', '0x0']
    elif layout is not None:
      command += [layout, internalDisplay]
    if resolution not in devices[device]:
      xrandr = subprocess.Popen(['xrandr', '--addmode', device, resolution],
          stderr=subprocess.PIPE)
      err = xrandr.stderr.read()
      wait(xrandr)
      if (err != ''):
        status.display(err.replace('\n','') + ' (' + device + ')', timeout=5,
            colour=WMII_ERRCOLOURS)
        return 1
  if disabledDevices is not None:
    for device in disabledDevices:
      command += ['--output', device, '--off', '--pos', '0x0']
  xrandr = subprocess.Popen(command, stderr=subprocess.PIPE)
  err = xrandr.stderr.read()
  ret = xrandr.wait()
  if (err != ''):
    status.display(err.replace('\n','') + ' (' + device + ')', timeout=5,
        colour=WMII_ERRCOLOURS)
  return ret

def restartWmii():
  pass # No longer required in wmii 3.9
#  """
#  Tell wmii to exec itself - to work around the fact that it doesn't listen
#  to resolution changes
#  """
#  wmiiCommand('/ctl', 'exec wmii', 'write')

def lidOpen():
  """
  Return True if the lid is open according to ACPI, False if it is closed
  and None if the state is unknown, or no lid exists.
  """
  import glob
  ret = True

  fn = glob.glob('/proc/acpi/button/lid/*/state')
  if len(fn) != 1: return None

  fd = open(fn[0])
  if fd.read().find('closed') != -1: ret = False
  fd.close
  return ret

def onlyInternalActive(activeDisplays):
  return len(activeDisplays) == 1 and activeDisplays[0][0].startswith(INTERNAL_DISPLAY)

def permutations(list, seperator):
  perms = []
  if len(list) == 1: return list
  perms += permutations(list[1:], seperator)
  return [list[0] + seperator + x for x in perms] + perms + [list[0]]

def changeDisplays(restart=True, interactive=True, targetDisplays=None,
    resolution=None, layout=None):
  """
  Select active displays. Prompt the user for which display[s] to switch
  to, then prompt for the resolution and switch to the selected displays.

  Interactively this only supports cloned layout. wmii needs support for
  extended displays before it would be smart to allow the user to pick other
  layouts.

  Non interactively a different layout can be passed, which currently will
  trigger a stub and place the external displays on the left of the internal
  display (regardless of the contents of the layout parameter) to facilitate
  beamer presentations with the speaker notes on the right. This support is
  incomplete and will NOT handle edge cases.
  """
  status.display('Stand by...', barfile='/lbar/display')
  (displays, activeDisplays, disabledDisplays, internalDisplay) = enumerateDisplays()
  interactive = interactive and activeDisplays and not \
      (onlyInternalActive(activeDisplays) and lidOpen() == False)
  status.remove('/lbar/display')

  if interactive or targetDisplays:
    if targetDisplays is None:
      targetDisplays = WMII_MENU(['Auto'] + permutations(list(displays), '+') \
          + ['Show Disconnected'], 'Displays:').split('+')
      if (targetDisplays == ['Show Disconnected']):
        targetDisplays = WMII_MENU(permutations(list(displays) \
            + list(disabledDisplays), '+'), 'Displays:').split('+')
    if (targetDisplays == ['']): return
    elif (targetDisplays == ['Auto']):
      interactive = False
    else:
      for display in displays:
        disabledDisplays[display] = displays[display]
      displays = {}
      for display in targetDisplays:
        if display not in disabledDisplays:
          status.display(("Display %s unknown!" % display), timeout=5,
              colour=WMII_ERRCOLOURS)
          return
        displays[display] = disabledDisplays[display]
        del disabledDisplays[display]
  elif len(displays) > 1 and internalDisplay in displays and lidOpen() == False:
    disabledDisplays[internalDisplay] = displays[internalDisplay]
    del displays[internalDisplay]

  if resolution is None:
    resolutions = intersectResolutions(displays)
    if interactive:
      resolution = WMII_MENU(resolutions, 'Resolution:')
      if (resolution == ''): return
      if not re.match('^\d+x\d+$', resolution):
        status.display(resolution + " is not a valid resolution", timeout=5,
            colour=WMII_ERRCOLOURS)
        return
    else:
      resolution = largestResolution(resolutions)

  status.display('Stand by...', barfile='/lbar/display')
  ret = setResolution(displays, resolution, internalDisplay, disabledDisplays,
      layout)
  status.remove('/lbar/display')
  if ret == 0 and restart:
    restartWmii() # wmii does not pick up resolution changes
  if ret == 0:
    return resolution, activeDisplays

def restoreDisplays(restoreDisplays):
  changeDisplays(interactive=False,
      targetDisplays=list(zip(*restoreDisplays)[0]),
      resolution=restoreDisplays[0][1])

def magicChangeAndPresent(pdf):
  layout=WMII_MENU(['Ordinary PDF', 'Speaker Notes on Right', 'Speaker Notes on Left'], 'PDF Layout:')
  if layout == '': return
  layout = {
      'Ordinary PDF':           None,
      'Speaker Notes on Right': '--left-of',
      'Speaker Notes on Left':  '--right-of',
      }.get(layout)
  ret = changeDisplays(layout=layout)
  if ret is not None:
    disableXAutoLock()
    disableScreenBlanking()

    (resolution, oldSetup) = ret
    [width, height] = [int(x) for x in resolution.split('x')]
    command = ['impressive', '-t', 'Crossfade', '-T', '100']
    if layout:
      command += ['-f', '-g', str(width*2)+'x'+str(height)]
    command += [pdf]
    subprocess.call(command)

    enableScreenBlanking()
    enableXAutoLock()
    restoreDisplays(oldSetup)

def selectAndPresent():
  import os
  dirname = os.path.expanduser('~')
  files = [f for f in os.listdir(dirname)
      if f.lower().endswith('.pdf')
      and os.path.isfile(os.path.join(dirname, f))]
  f = WMII_MENU(files)
  if not os.path.isfile(os.path.join(dirname, f)):
    status.display(f+" is not a file")
    return
  magicChangeAndPresent(f)

if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    magicChangeAndPresent(sys.argv[1])
  else:
    changeDisplays()
