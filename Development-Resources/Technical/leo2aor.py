#!/usr/bin/python
# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:bob05.20150110121004.2: * @file py/leo2aor.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< documentation >>
#@+node:bob05.20150110121004.3: ** << documentation >>
"""
Generate a "Bonsai CSV UTF-8" file that represents the specified
Leo-Editor File

The Android Outliner can import the "Bonsai CSV UTF-8" creating
an Android Outliner "outline" with the same structure and contents
as the Leo-Editor file.

The Leo-Editor "node headline" corresponds to the Android Outliner
"Activity Name".  The Leo-Editor "node body" corresponds to the
Android Outliner "Activity Note."

The Android Outliner does not implement anything like Leo-Editor
"clones."  Hence, each appearance of a clone in the Leo-Editor file
is an independent activity in the Android Outliner file.
"""
#@-<< documentation >>
#@+<< Copyright >>
#@+node:bob05.20150203124337.2: ** << Copyright >>
"""
leo2aor.py - Leo-Editor file compare functions
Copyright (C) 2015 Robert F. Hossley.  All Rights Reserved.

leo2aor.py is Open Software and is distributed under the terms of the
MIT License. The gist of the license is that leo2aor.py is absolutely
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
#@+node:bob05.20150110121004.4: ** << imports >>
import argparse
import csv

import leo.core.leoBridge as leoBridge
#@-<< imports >>

#@+others
#@+node:bob05.20150110121004.5: ** cmdLineHandler()
def cmdLineHandler():
    """
    Command Line Handler

    @param return:  argparse.Namespace object containing all the parsed
        command line arguments.
    """

    parser = argparse.ArgumentParser(description='Leo-Editor to Android Outliner', usage='%(prog)s inFile outFile')
    parser.add_argument('inFile', help='Pathname of a .leo file.  .leo is added automatically if needed.')
    parser.add_argument('outFile', help='Pathname of a csv file to be created or overwritten. .csv is added automatically if needed.')
    args = parser.parse_args()
    
    if not args.inFile.endswith('.leo'):
        args.inFile = args.inFile + '.leo'
    if not args.outFile.endswith('.csv'):
        args.outFile = args.outFile + '.csv'

    return args
#@+node:bob05.20150110121004.6: ** main()
def main():
    args = cmdLineHandler()

    bridge = leoBridge.controller(gui='nullGui', silent=True,
        verbose=False, loadPlugins=False, readSettings=False)
    cmdrIn = bridge.openLeoFile(args.inFile)
    outList = leo2aor(cmdrIn)
    cmdrIn.close()

    fdOut = open(args.outFile, 'w')
    csvWriter = csv.writer(fdOut)
    csvWriter.writerows(outList)
    fdOut.close()
#@+node:bob05.20150110121004.7: ** leo2aor()
def leo2aor(cmdrIn):
    """ Traverse a Leo-Editor Outline producing a List
    that is a Bonsai CSV representation of the outline
    
    Arguments:
        cmdrIn:  Leo-Editor commander for the target
            input file.

    Returns:
        outList:  a List that is the Bonsai CSV UTF-8 
            representation of the Leo-Editor outline
    """

    outList = list()
    for ptrx in cmdrIn.allNodes_iter():
        oneNode = list()
        oneNode.append(ptrx.h.encode('utf-8'))
        oneNode.append(0)
        oneNode.append(0)
        oneNode.append(len(ptrx.stack))
        oneNode.append(0)
        oneNode.append(0)
        oneNode.append(0)
        oneNode.append('')
        oneNode.append('')
        oneNode.append('')
        oneNode.append('')
        oneNode.append('Unfiled')
        oneNode.append('')
        oneNode.append('')
        oneNode.append(ptrx.b.encode('utf-8'))
        outList.append(oneNode)
    return outList
#@-others

if __name__ == '__main__':
    main()
#@-leo
