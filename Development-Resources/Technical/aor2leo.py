#!/usr/bin/python
# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:bob05.20150110164538.2: * @file py/aor2leo.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< documentation >>
#@+node:bob05.20150110164538.3: ** << documentation >>
"""
Generate a Leo-Editor file that represents the specified
"Bonsai CSV UTF-8" file

The Android Outliner can export a "Bonsai CSV UTF-8" representing
a outline.  Program aor2leo.py generates a Leo-Editor outline
with the same structure and contents as the Android Outliner outline.

The Leo-Editor "node headline" corresponds to the Android Outliner
"Activity Name".  The Leo-Editor "node body" corresponds to the
Android Outliner "Activity Note."

The Android Outliner does not implement anything like Leo-Editor
"clones."  Hence, aor2leo.py never generates a cloned node.
"""
#@-<< documentation >>
#@+<< Copyright >>
#@+node:bob05.20150203124337.3: ** << Copyright >>
"""
aor2leo.py - Leo-Editor file compare functions
Copyright (C) 2015 Robert F. Hossley.  All Rights Reserved.

aor2leo.py is Open Software and is distributed under the terms of the
MIT License. The gist of the license is that aor2leo.py is absolutely
free, even for commercial use (including resale). There is no GNU-like
"copyleft" restriction. The Open Source Initiative board has voted to certify
the MIT license as Open Source. This license is compatible with the GPL.

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the name of Robert F. Hossley
not be used in advertising or publicity pertaining to distribution of
the software without specific, written prior permission.

DISCLAIMER OF WARRANTIES

Robert F. Hossley SPECIFICALLY DISCLAIMS ALL WARRANTIES, EXPRESSED
OR IMPLIED, WITH RESPECT TO THIS COMPUTER SOFTWARE, INCLUDING BUT NOT
LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE. IN NO EVENT SHALL REAM BE LIABLE FOR ANY LOSS OF
PROFIT OR ANY COMMERCIAL DAMAGE, INCLUDING BUT NOT LIMITED TO SPECIAL,
INCIDENTAL, CONSEQUENTIAL OR OTHER DAMAGES.

"""

#@-<< Copyright >>
#@+<< imports >>
#@+node:bob05.20150110164538.4: ** << imports >>
import argparse
import csv
import os.path

import leo.core.leoBridge as leoBridge
#@-<< imports >>

#@+others
#@+node:bob05.20150110164538.5: ** cmdLineHandler()
def cmdLineHandler():
    """
    Command Line Handler

    @param return:  argparse.Namespace object containing all the parsed
        command line arguments.
    """

    parser = argparse.ArgumentParser(description='Android Outliner to Leo-Editor', usage='%(prog)s inFile outFile')
    parser.add_argument('inFile', help='Pathname of a csv file. .csv is added automatically if needed.')
    parser.add_argument('outFile', help='Pathname of a .leo file to be created.  .leo is added automatically if needed.')
    args = parser.parse_args()
    
    if not args.inFile.endswith('.csv'):
        args.inFile = args.inFile + '.csv'
    if not args.outFile.endswith('.leo'):
        args.outFile = args.outFile + '.leo'

    return args
#@+node:bob05.20150110164538.6: ** main()
def main():
    args = cmdLineHandler()

    fdIn = open(args.inFile, 'r')
    csvReader = csv.reader(fdIn)
    outList = [(row[0].decode('utf-8'), row[14].decode('utf-8'), int(row[3])) for row in csvReader]
    fdIn.close()
    
    if os.path.isfile(args.outFile):
        raise ValueError('File already exists {0}'.format(args.outFile))
    bridge = leoBridge.controller(gui='nullGui', silent=True,
        verbose=False, loadPlugins=False, readSettings=False)
    cmdrOut = bridge.openLeoFile(args.outFile)
    aor2leo(cmdrOut, outList)
    cmdrOut.save()
    cmdrOut.close()

#@+node:bob05.20150110164538.7: ** aor2leo()
def aor2leo(cmdrOut, outList):
    """ Convert a list of triplets representing an
    Android Outliner outline to a Leo-Editor file
    
    Arguments:
        cmdrOut:  Leo-Editor commander for the target
            output file.
        outList:  A list representing an outline:
            [(hdl, bdy, depth), ...]
                hdl:  Headline
                bdy:  Body
                depth:  Node depth (0 --> Root)
            If outList[k] depth is N and
            outList[k+1] depth is N+1, then
            the outList[k] node is the parent
            of the outList[k+1] node.

    Returns:
        None
    """

    allPos = [posx.copy() for posx in cmdrOut.all_positions()]
    if len(allPos) > 1:
        raise ValueError('New Leo-Editor file created with '
            ' {cnt} nodes.'.format(len(allPos)))
    creationRoot = allPos[0]
    lastRoot = creationRoot
    lastNode = creationRoot
    lastDepth = 0
    for (curHdl, curBdy, curDepth) in outList:
        if curDepth == 0:
            lastRoot = lastRoot.insertAfter()
            lastNode = lastRoot
            lastDepth = 0
        elif curDepth == lastDepth:
            lastNode = lastNode.insertAfter()
        elif curDepth == (lastDepth + 1):
            lastNode = lastNode.insertAsLastChild()
            lastDepth = curDepth
        else:
            raise ValueError('Invalid outline description '
                'Node depth jumped from {d1} to {d2}'.format(
                d1=lastDepth, d2=curDepth))
        lastNode.h = curHdl
        lastNode.b = curBdy
    creationRoot.doDelete()
#@-others

if __name__ == '__main__':
    main()
#@-leo
