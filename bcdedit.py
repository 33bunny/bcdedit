#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Loic Jaquemet loic.jaquemet+python@gmail.com
#

__author__ = "Loic Jaquemet loic.jaquemet+python@gmail.com"

import argparse
import ctypes
import functools
import logging
import os
import time
import sys
import uuid

import hivex
import bcdtypes

'''
  BCD ref (BCD.docx): http://msdn.microsoft.com/en-us/windows/hardware/gg463059.aspx
  BCD WMI ref: http://msdn.microsoft.com/en-us/library/windows/desktop/aa964229%28v=vs.85%29.aspx
'''

def show(opts):
  f = opts.bcdfile
  print "%s: %d bytes"%(f.name, os.path.getsize(f.name))
  print '---'
  h = hivex.Hivex(f.name)
  h.debug=opts.debug
  r = h.root()
  print h.node_name( r )
  # print childs
  print_objects(h, r, '')


def print_objects(h, root, prefix):
  getchildren = h.node_children
  getname = h.node_name
  myname = getname(root)
  ts = functools.partial(print_ts,h)
  dbg = ''

  for c in getchildren( root ):
    print '%s\t%s'%(prefix, getname(c))
    if getname(c) == 'Objects':
      for guid_node in getchildren( c ):
        guid = uuid.UUID(getname(guid_node))
        guid_desc = bcdtypes.guid_desc(str(guid))
        print '%s\t%s - %s %d'%(prefix, guid, guid_desc, guid_node)
        print_name_rec(h, guid_node, prefix+'\t')
    else:
      pass # Description ?


def print_name_rec(h, node, prefix):
  getchildren = h.node_children
  getname = h.node_name
  myname = getname(node)
  ts = functools.partial(print_ts,h)
  dbg = ''
  if myname == 'Elements':
    print_name_el(h, node, prefix)
  else:
    for c in getchildren( node ):
      if h.debug: dbg = ' (%s)'%(ts(node)) 
      print '%s\t%s%s'%(prefix, getname(c), dbg)
      print_name_rec(h, c, prefix+'\t')
    else:
      pass

def print_name_el(h, node, prefix):
  # 31-28 : object code
  # 27-0: category specific data
  getchildren = h.node_children
  getname = h.node_name
  ts = functools.partial(print_ts,h)
  myname = getname(node)
  dbg = ''
  for c in getchildren( node ):
    if h.debug: dbg = ' (%s)'%(ts(node)) 
    # get the object type
    obj_type = int(getname(c),16)
    name = bcdtypes.type_desc(obj_type)
    # get the object code ? first 4 bits
    # code = bcdtypes.object_code_desc(obj_type)
    code = el_to_bin(obj_type)
    print '%s\t%x %s %s%s'%(prefix, obj_type, code,  name,  dbg),
    vals = h.node_values(c)
    for v in vals:
      print v, el_to_bin_16(v), h.value_type(v)

  #print h.node_values(node)

def print_ts(h, node):
  return time.ctime( h.node_timestamp(node)/100000000) 

def el_to_bin(i):
  return '{:0>32b}'.format(i)

def el_to_bin_16(i):
  return '{:0>16b}'.format(i)

  
def edit(opts):
  f = opts.bcdfile

def argparser():
  rootparser = argparse.ArgumentParser(prog='bcdedit', 
    description='Edit Windows BCD - Boot Configuration Data file.')

  rootparser.add_argument('--debug', action='store_true', help='Debug mode on.')
  rootparser.add_argument('bcdfile', type=argparse.FileType('rb'), action='store', help='BCD file.')

  subparsers = rootparser.add_subparsers(help='sub-command help')
  
  # bcdedit: create, set, export, 
  ## ref http://msdn.microsoft.com/en-us/library/ff793653%28v=winembedded.60%29.aspx
  
  #'-createstore', help='Creates a new empty boot-configuration data store. The created store is not a system store.')
  #'export', help='Exports the contents of the system store into a file. This file can be used later to restore the state of the system store. This command is valid only for the system store.')
  #'import', help='Restores the state of the system store by using a backup data file previously generated by using the /export option. This command deletes any existing entries in the system store before the import occurs. This command is valid only for the system store.')
  #'store', help='This option can be used with most bcdedit commands to specify the store to be used. If this option is not specified, BCDEdit operates on the system store. Running the bcdedit /store command by itself is the same as running the bcdedit /enum active command.')

  #'copy', help='Makes a copy of a specified boot entry in the same system store.')
  #'create', help='Creates a new entry in the boot-configuration data store. If a well-known identifier is specified, the /application, /inherit, and /device options cannot be specified. If an identifier is not specified or not well known, an /application, /inherit, or /device option must be specified.')
  #'delete', help='Deletes an element from a specified entry.')

  #'deletevalue', help='Deletes a specified element from a boot entry.')
  #'set', help='Sets an entry option value.')

  '''/bootdebug Enables or disables boot debugging for a boot application.
/bootems Enables or disables Emergency Management Services for a boot application.
/bootsequence Sets the one-time boot sequence for the boot manager.
/copy Makes copies of entries in the store.
/create Creates new entries in the store.
/createstore Creates a new (empty) boot configuration data store.
/dbgsettings Sets the global debugger parameters.
/debug Enables or disables kernel debugging for an operating system entry.
/default Sets the default entry that the boot manager will use.
/delete Deletes entries from the store.
/deletevalue Deletes entry options from the store.
/displayorder Sets the order in which the boot manager displays the multiboot menu.
/ems Enables or disables Emergency Management Services for an operating system entry.
/emssettings Sets the global Emergency Management Services parameters.
/enum Lists entries in the store.
/export Exports the contents of the system store to a file. This file can be used later to restore the state of the system store.
/hypervisorsettings Sets the hypervisor parameters.
/import Restores the state of the system store by using a backup file created with the /export command.
/mirror Creates a mirror of entries in the store.
/set Sets entry option values in the store.
/sysstore Sets the system store device. This only affects EFI systems.
/timeout Sets the boot manager timeout value.
/toolsdisplayorder Sets the order in which the boot manager displays the tools menu.
/v Sets output to verbose mode. 
'''

  # bootrec: fixmbr, fixboot, rebuildbcd

  showp = subparsers.add_parser('show', help='show things.')
  showp.set_defaults(func=show)  

  editp = subparsers.add_parser('edit', help='edit things.')
  editp.set_defaults(func=edit)  

  showp.add_argument('item', type=str, choices=['all','device'], action='store', default=None, 
        help='What to show.')
  
  return rootparser

def main(argv):

  parser = argparser()
  opts = parser.parse_args(argv)

  level=logging.INFO
  if opts.debug :
    level=logging.DEBUG
  else:
    pass

  opts.func(opts)
  
  


if __name__ == "__main__":
  main(sys.argv[1:])

