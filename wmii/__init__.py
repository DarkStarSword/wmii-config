#!/usr/bin/env python2.6
# vi:sw=2:expandtab:ts=2

from util.decorators import async

WMII_NORMCOLOURS_TEXT        = '#888888'
WMII_NORMCOLOURS_BACKGROUND  = '#222222'
WMII_NORMCOLOURS_BORDER      = '#333333'
WMII_NORMCOLOURS = WMII_NORMCOLOURS_TEXT \
          + ' ' + WMII_NORMCOLOURS_BACKGROUND \
          + ' ' + WMII_NORMCOLOURS_BORDER

WMII_MSGCOLOURS_TEXT        = '#FFFFFF'
WMII_MSGCOLOURS_BACKGROUND  = '#2222FF'
WMII_MSGCOLOURS_BORDER      = '#333333'
WMII_MSGCOLOURS = WMII_MSGCOLOURS_TEXT \
          + ' ' + WMII_MSGCOLOURS_BACKGROUND \
          + ' ' + WMII_MSGCOLOURS_BORDER
WMII_MSG1COLOURS_TEXT        = '#000088'
WMII_MSG1COLOURS_BACKGROUND  = '#8888FF'
WMII_MSG1COLOURS_BORDER      = '#CCCCFF'
WMII_MSG1COLOURS = WMII_MSG1COLOURS_TEXT \
          + ' ' + WMII_MSG1COLOURS_BACKGROUND \
          + ' ' + WMII_MSG1COLOURS_BORDER

import subprocess
def command(file, command=None, action='create'):
  p = subprocess.Popen(['wmiir', action, file], stdin=subprocess.PIPE)
  if command is not None:
    p.stdin.write(command.encode())
    p.stdin.close()
  p.wait()

import wmii.__status
status = wmii.__status.__clsStatus()

@async
def dispLongMsg(msg):
  import subprocess
  xmsg = subprocess.Popen(['xmessage', '-nearmouse', '-file', '-'],
      stdin=subprocess.PIPE)
  xmsg.stdin.write(msg)
  xmsg.stdin.close()
  xmsg.wait()

