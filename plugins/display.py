#!/usr/bin/env python
# vi:expandtab:ts=2:sw=2

# TODO: A lot of this still needs to be updated or pythonised.
# - Is there a more pythonic way than calling xrandr and parsing output? A library?
# - If number of xinerama screens decreases, prompt to collect missing windows

import subprocess
import re

from pluginmanager import notify, notify_exception, Menu

# Internal display should start with this string from xrandr:
INTERNAL_DISPLAY='LVDS'

def disableAutoLock():
  try:
    import lock
    lock.disableAutoLock()
  except ImportError:
    pass

def enableAutoLock():
  try:
    import lock
    lock.enableAutoLock()
  except ImportError:
    pass

screen_blanking_enabled = True
def disable_screen_blanking():
  global screen_blanking_enabled
  subprocess.call(['xset', 's', 'off'])
  subprocess.call(['xset', '-dpms'])
  screen_blanking_enabled = False
  notify('Screen Blanking DISABLED', key='display-blanking')

def enable_screen_blanking():
  global screen_blanking_enabled
  subprocess.call(['xset', 's', 'on'])
  subprocess.call(['xset', '+dpms'])
  screen_blanking_enabled = True
  notify('Screen Blanking Enabled', key='display-blanking')

@notify_exception
def toggle_screen_blanking():
  disable_screen_blanking() if screen_blanking_enabled else enable_screen_blanking()

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
      # FIXME: On nvidia we get a non-fatal error, we should not return failure or we will mess up xautolock disabling, etc
      wait(xrandr)
      if (err != ''):
        notify(err.replace('\n','') + ' (' + device + ')', colours='errcolors')
        return 1
  if disabledDevices is not None:
    for device in disabledDevices:
      command += ['--output', device, '--off', '--pos', '0x0']
  xrandr = subprocess.Popen(command, stderr=subprocess.PIPE)
  err = xrandr.stderr.read()
  ret = xrandr.wait()
  if (err != ''):
    notify(err.replace('\n','') + ' (' + device + ')', colours='errcolors')
  return ret

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

def _changeDisplays(interactive=True, targetDisplays=None, resolution=None,
    layout=None):
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
  notice = notify('Stand by...', key='display')
  (displays, activeDisplays, disabledDisplays, internalDisplay) = enumerateDisplays()
  interactive = interactive and activeDisplays and not \
      (onlyInternalActive(activeDisplays) and lidOpen() == False)
  notice.remove()

  if interactive or targetDisplays:
    if targetDisplays is None:
      if len(displays) + len(disabledDisplays) == 1:
        targetDisplays = [displays.keys()[0]]
      else:
        targetDisplays = Menu(['Auto'] + permutations(list(displays), '+') \
            + ['Show Disconnected'], prompt='Displays:')().split('+')
        if (targetDisplays == ['Show Disconnected']):
          targetDisplays = Menu(permutations(list(displays) \
              + list(disabledDisplays), '+'), prompt='Displays:')().split('+')
    if (targetDisplays == ['']): return
    elif (targetDisplays == ['Auto']):
      interactive = False
    else:
      for display in displays:
        disabledDisplays[display] = displays[display]
      displays = {}
      for display in targetDisplays:
        if display not in disabledDisplays:
          notify("Display %s unknown!" % display, key='display', colours='errcolors')
          return
        displays[display] = disabledDisplays[display]
        del disabledDisplays[display]
  elif len(displays) > 1 and internalDisplay in displays and lidOpen() == False:
    disabledDisplays[internalDisplay] = displays[internalDisplay]
    del displays[internalDisplay]

  if resolution is None:
    resolutions = intersectResolutions(displays)
    if interactive:
      resolution = Menu(resolutions, prompt='Resolution:')()
      if (resolution == ''): return
      if not re.match('^\d+x\d+$', resolution):
        notify(resolution + " is not a valid resolution", colours='errcolors')
        return
    else:
      resolution = largestResolution(resolutions)

  notice = notify('Stand by...', key='display')
  ret = setResolution(displays, resolution, internalDisplay, disabledDisplays,
      layout)
  notice.remove()
  if ret == 0:
    return resolution, activeDisplays

@notify_exception
def changeDisplays(interactive=True, targetDisplays=None, resolution=None,
    layout=None):
  ret = _changeDisplays(interactive, targetDisplays, resolution, layout)
  try:
    import background
    background.set_background()
  except:
    pass
  return ret

@notify_exception
def restoreDisplays(restoreDisplays):
  changeDisplays(interactive=False,
      targetDisplays=list(zip(*restoreDisplays)[0]),
      resolution=restoreDisplays[0][1])

@notify_exception
def magicChangeAndPresent(pdf):
  layout=Menu(['Ordinary PDF', 'Speaker Notes on Right', 'Speaker Notes on Left'], prompt='PDF Layout:')()
  if layout == '': return
  layout = {
      'Ordinary PDF':           None,
      'Speaker Notes on Right': '--left-of',
      'Speaker Notes on Left':  '--right-of',
      }.get(layout)
  ret = changeDisplays(layout=layout)
  if ret is not None:
    disableAutoLock()
    disable_screen_blanking()

    (resolution, oldSetup) = ret
    [width, height] = [int(x) for x in resolution.split('x')]
    command = ['impressive', '-t', 'Crossfade', '-T', '100']
    if layout:
      command += ['-f', '-g', str(width*2)+'x'+str(height)]
    command += [pdf]
    subprocess.call(command)

    enable_screen_blanking()
    enableAutoLock()
    restoreDisplays(oldSetup)

@notify_exception
def selectAndPresent():
  import os
  dirname = os.path.expanduser('~')
  files = [f for f in os.listdir(dirname)
      if f.lower().endswith('.pdf')
      and os.path.isfile(os.path.join(dirname, f))]
  f = Menu(files)()
  if not os.path.isfile(os.path.join(dirname, f)):
    notice(f+" is not a file", colours='errcolors')
    return
  magicChangeAndPresent(f)

if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    magicChangeAndPresent(sys.argv[1])
  else:
    changeDisplays()

# TODO: Use --primary to select display with wmii bar
