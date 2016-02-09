__all__ = ["DOMToPython", "DOMDocument"]

'''
    TODO:
    - warning on xml tags called __tag__
'''

import xml.etree.ElementTree as ET
import io
import sys

def dom_to_python(filename_xml, tab=' '*4):
    def element_to_python(node, level, output):
        # write indent
        output.write(tab*level)
        # 'with' if node has children
        if node:
            output.write('with ')
        # create the node
        output.write('doc.'+node.tag)
        # add any text as a parameter
        stripped_text = node.text.strip()
        if stripped_text:
            output.write('("'+stripped_text+'")')
        # if there's attributes, add a second set of keyword parameters
        if node.attrib:
            output.write(' (')
            prefix = ''
            for key, value in node.attrib.items():
                output.write(prefix+key+'="'+value+'"')
                prefix = ', '
            output.write(')')
        # follow any with with a colon
        if node:
            output.write(':')
        output.write('\n')
        # process child nodes
        for child in node:
            element_to_python(child, level+1, output)

    output = io.StringIO()
    tree = ET.parse(filename_xml)
    root = tree.getroot()
    output.write('doc = domtopython.DOMDocument()\n')
    element_to_python(root, 0, output)
    output.write('doc.print_xml()\n')
    return output.getvalue()

class DOMNode:
    def __init__(self, document, tag, *args, **kwargs):
        # keep a reference to document node is part of
        self.__document = document
        # xml tag, attributes and child nodes
        self.__tag = tag
        self.__attributes = {}
        self.__children = []
        # set any content and attributes
        self.__update_xml(args, kwargs)

    # update the node's xml content and attributes
    def __update_xml(self, args, kwargs):
        # add valid positional arguments as text content of the node
        for value in args:
            if not isinstance(value, (str,bytes)):
                raise ValueError("Error: non-string argument for element content (%r)" % (value))
        if args:
            self.__children.append("".join(args))
        # add valid keyword arguments as attributes of the node
        for keyword, value in kwargs.items():
            if not isinstance(value, (str,bytes)):
                raise ValueError("Error: non-string argument for attribute value (%r)" % (value))
            if not isinstance(keyword, (str,bytes)):
                raise ValueError("Error: non-string argument for attribute name (%r)" % (keyword))
        self.__attributes.update(kwargs)

    # upon accessing an unknown attribute of DOMNode, create a matching node
    def __getattr__(self, item):
        child_node = DOMNode(self.__document, item)
        self.__children.append(child_node)
        return child_node

    # upon calling DOMNode, treat its parameters as content and named parameters as attributes
    def __call__(self, *args, **kwargs):
        self.__update_xml(args, kwargs)
        # return self, to allow continuation with next call
        return self

    # when entering, push self on the stack of document and set context to document
    def __enter__(self):
        return self.__document(self)

    # when exiting, pop self off of the stack of document
    def __exit__(self, type, value, traceback):
        self.__document(None)

    # recursive print routine, printing the current node and its children
    def print_xml(self, level):
        def xml_attributes():
            attributes = ''
            for attribute, value in self.__attributes.items():
                attributes += ' '+attribute+'="'+value+'"'
            return attributes
        if self.__children:
            print (self.__document['tab']*level+'<'+self.__tag+xml_attributes()+'>')
            for child in self.__children:
                if isinstance(child, (str,bytes)):
                    print(str(self.__document['tab']*(level+1))+child)
                else:
                    child.print_xml(level+1)
            print (self.__document['tab']*level+'</'+self.__tag+'>')
        else:
            print (self.__document['tab']*level+'<'+self.__tag+' />')

class DOMDocument(object):
    # setup the document with a root DOMNode and put it on a stack
    def __init__(self): # , root_tag, *args, **kwargs
        # root_node = DOMNode(self, root_tag, *args, **kwargs)
        self.__stack = [] #root_node
        self.__opts = {
            'header': True,
            'encoding': 'utf-8',
            'tab': ' '*4
        }

    # accessing unknown items is passed to the node op top of the stack
    def __getattr__(self, item):
        if self.__stack:
            return getattr(self.__stack[-1], item)
        else:
            self.__root_node = DOMNode(self, item)
            return self.__root_node

    # calling the DOMDocument with (None), pops the stack (after exit of DOMNode)
    # calling the DOMDocument with (node), pushes the node on the stack (on enter of DOMNode)
    def __call__(self, node):
        if node is None:
            self.__stack.pop()
        else:
            self.__stack.append(node)
            # return self, to allow continuation with next call
            return self

    # make DOMDocument subscriptable, for options access
    def __getitem__(self, name):
        return self.__opts[name]

    def print_xml(self):
        if self['header']:
            print ('<?xml version="1.0" encoding="%s"?>' % self['encoding'])
        self.__root_node.print_xml(0)
