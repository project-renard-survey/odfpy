#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2006 Søren Roug, European Environment Agency
#
# This is free software.  You may redistribute it under the terms
# of the Apache license and the GNU General Public License Version
# 2 or at your option any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#
from xml.sax import make_parser,handler
from xml.sax.xmlreader import InputSource
import xml.sax.saxutils
import sys

RELAXNS=u"http://relaxng.org/ns/structure/1.0"

elements = {}
currdef = None
currelement = None
currnode = None

from odf.namespaces import *

class Node:
    ns = None
    name = None

class Element(Node):
    " Element "
    def __init__(self):
        self.attrs = {}

class Attribute(Node):
    " Attribute "

#
#
class S22RelaxParser(handler.ContentHandler):

    def __init__(self):
        self.data = []
        self.level = 0

    def text(self):
        return ''.join(self.data)

    def characters(self, data):
        self.data.append(data)

    def startElementNS(self, tag, qname, attrs):
        global currnode, currelement
        if tag == (RELAXNS, 'element'):
            currelement = currnode = Element()
        elif tag == (RELAXNS, 'attribute'):
            currnode = Attribute()
        elif tag == (RELAXNS, 'name'):
            currnode.ns = attrs.get((None,'ns'),'')
            self.data = []

    def endElementNS(self, tag, qname):
        global currnode, currelement
        if tag == (RELAXNS, 'element'):
            elements[(currelement.ns, currelement.name)] = currelement
            currelement = None
        elif tag == (RELAXNS, 'attribute'):
            currelement.attrs[currnode.name] = currnode
            currnode = None
        elif tag == (RELAXNS, 'name'):
            currnode.name = self.text()
        elif tag == (RELAXNS, 'anyName'):
            currnode.name = "__ANYNAME__"
        self.data = []

def parse_rng(relaxfile):
    content = file(relaxfile)
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(S22RelaxParser())
    parser.setErrorHandler(handler.ErrorHandler())

    inpsrc = InputSource()
    inpsrc.setByteStream(content)
    parser.parse(inpsrc)


if __name__ == "__main__":
    parse_rng("simplified-7-22.rng")

    print "allowed_attributes = {"

    slist = elements.keys()
    slist.sort()
    for s in slist:
        e = elements[s]
        if e.name == u'__ANYNAME__':
            continue
        if len(e.attrs.values()) == 1 and e.attrs.values()[0].name == u'__ANYNAME__':
            print "\t(%sNS,u'%s'): None," % (nsdict.get(e.ns,'unknown').upper(), e.name)
        else:
            print "\t(%sNS,u'%s'):(" % (nsdict.get(e.ns,'unknown').upper(), e.name)
            for a in e.attrs.values():
                print "\t\t(%sNS,u'%s')," % (nsdict.get(a.ns,'unknown').upper(), a.name)
            print "\t),"
    print "}"
