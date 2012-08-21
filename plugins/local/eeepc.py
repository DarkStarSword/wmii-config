from pluginmanager import imported_from_wmiirc

if imported_from_wmiirc():
  import wmiirc
  wmiirc.wmii['font'] = '6x9'
  wmiirc.wmii['fontpad'] = '0 0 -1 -1'
