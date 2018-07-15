#!/usr/bin/python
# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:bob05.20150128152642.4: * @file py/leo2nlx.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< documentation >>
#@+node:bob05.20150128152642.5: ** << documentation >>
"""
Generate a NoteLynX XML project file that represents the specified
Leo-Editor File
"""
#@-<< documentation >>
#@+<< Copyright >>
#@+node:bob05.20150203124337.4: ** << Copyright >>
"""
leo2nlx.py - Leo-Editor file compare functions
Copyright (C) 2015 Robert F. Hossley.  All Rights Reserved.

leo2nlx.py is Open Software and is distributed under the terms of the
MIT License. The gist of the license is that leo2nlx.py is absolutely
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
#@+node:bob05.20150128152642.6: ** << imports >>
import argparse
import os
import xml.etree.ElementTree as ET

import leo.core.leoBridge as leoBridge
#@-<< imports >>

#@+others
#@+node:bob05.20150128152642.7: ** cmdLineHandler()
def cmdLineHandler():
    """
    Command Line Handler

    @param return:  argparse.Namespace object containing all the parsed
        command line arguments.
    """

    parser = argparse.ArgumentParser(description='Leo-Editor to NoteLynX', usage='%(prog)s inFile outFile')
    parser.add_argument('inFile', help='Pathname of a .leo file.  .leo is added automatically if needed.')
    parser.add_argument('outFile', help='Pathname of an xml file to be created or overwritten. .xml is added automatically if needed.')
    args = parser.parse_args()
    
    if not args.inFile.endswith('.leo'):
        args.inFile = args.inFile + '.leo'
    if not args.outFile.endswith('.xml'):
        args.outFile = args.outFile + '.xml'

    return args
#@+node:bob05.20150128152642.8: ** main()
def main():
    args = cmdLineHandler()

    bridge = leoBridge.controller(gui='nullGui', silent=True,
        verbose=False, loadPlugins=False, readSettings=False)
    cmdrIn = bridge.openLeoFile(args.inFile)
    leo2nlx(cmdrIn, args.outFile)
    cmdrIn.close()
#@+node:bob05.20150130154417.2: ** class NodeObj
class NodeObj(object):
    #@+others
    #@+node:bob05.20150130154417.3: *3* __init__()
    def __init__(self, hdr, bdy):
        self.hdr = hdr
        self.bdy = bdy
        self.children = None
        self.parents = None
        self.visited = None
        self.nodeID = None
    #@+node:bob05.20150130154417.4: *3* __repr__()
    def __repr__(self):
        return 'Node ID: {ni} Headline: "{hdr}"'.format(
            ni=self.nodeID, hdr=self.hdr)
    #@-others
#@+node:bob05.20150128152642.9: ** leo2nlx()
def leo2nlx(cmdrIn, outPath):
    """ Traverse a Leo-Editor Outline producing a 
    NoteLynX XML project file
    
    Arguments:
        cmdrIn:  Leo-Editor commander for the target
            input file.
        outPath:  Pathname of XML file to be produced.

    Returns:
        None

    """
    def _allVnodes():
        yield hiddenVnode
        for vnode in cmdrIn.all_vnodes_iter():
            yield vnode

    vnode2nobj = dict()
    # Create all Node Objects
    hiddenNobj = None
    hiddenVnode = None
    for vnode in cmdrIn.all_vnodes_iter():
        nobj = NodeObj(vnode.h, vnode.b)
        vnode2nobj[vnode] = nobj
        pv = vnode.parents[0]
        if (pv.gnx == 'hidden-root-vnode-gnx' 
            and
            hiddenNobj is None):
            title = os.path.splitext(os.path.basename(outPath))[0]
            hiddenNobj = NodeObj(title, '')
            hiddenVnode = pv
            vnode2nobj[hiddenVnode] = hiddenNobj
    # Fill in the children list and parent list in each Node Object
    for vnode in  _allVnodes():
        nodeObjx = vnode2nobj[vnode]
        nodeObjx.children = [vnode2nobj[vnode] for vnode in vnode.children]
        nodeObjx.parents = [vnode2nobj[vnode] for vnode in vnode.parents]
    # Walk the NodeObj tree assigning node ID's
    nodeID = 1
    for nodex in bffvWalk(hiddenNobj):
        nodex.nodeID = nodeID
        nodeID += 1
    # Walk the NodeObj tree generating XML
    xmlRoot = ET.Element('network')
    for nodex in bffvWalk(hiddenNobj):
        links = [str(nodey.nodeID) for nodey in nodex.parents]
        linkTypes = ['1' for nodey in nodex.parents]
        links = links + [str(nodey.nodeID) for nodey in nodex.children]
        linkTypes = linkTypes + ['3' for nodey in nodex.children]
        _ = ET.SubElement(xmlRoot, 'node',
            {'id': str(nodex.nodeID),
            'title': nodex.hdr,
            'body': nodex.bdy,
            'links': ' '.join(links) ,
            'linkTypes': ' '.join(linkTypes) })
    
    ET.ElementTree(xmlRoot).write(outPath, encoding='utf-8')
        
#@+node:bob05.20150131111640.2: ** bffvWalk() - Breadth First node Walk
def bffvWalk(rootNodeObj):
    """ Breadth First node Walk
    Generator returning every Vnode in Breadth First Order.

    Arguments:
        rootNodeObj:  Root Node Object

    Returns:
        nodex:  Next node in the tree.

    Exceptions:
        StopIteration:  All nodes have been returned.

    """

    clearAllVisited(rootNodeObj)
    #fifo = [(nodeObjx, None) for nodeObjx in rootNodeObj.children]
    fifo = [(rootNodeObj, None)]
    while True:
        if fifo:
            parent, index = fifo[0]
            if index is None:
                if not parent.visited:
                    parent.visited = True
                    yield parent
                del fifo[0]
                fifo.append((parent, 0))
            else:
                if index < len(parent.children):
                    nxtVnode = parent.children[index]
                    if not nxtVnode.visited:
                        nxtVnode.visited = True
                        yield nxtVnode
                    fifo[0] = (parent, index + 1)
                    fifo.append((nxtVnode, 0))
                else:
                    del fifo[0]
        else:
            break
#@+node:bob05.20150131111640.3: ** clearAllVisited()
def clearAllVisited(rootNodeObj):
    """ Attach a "visited" attribute with value False
    to each NodeObj
    
    Arguments:
        rootNodeObj:  Root node object
    
    Returns:
        None
    
    This is easier than bffvWalk() because it doesn't matter
    if the attribute is attached several times to a node.
    This occurs when there are clones.
    """

    rootNodeObj.visited = False
    for nodex in rootNodeObj.children:
        clearAllVisited(nodex)
#@-others

if __name__ == '__main__':
    main()
#@-leo
