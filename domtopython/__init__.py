__all__ = ["DOMToPython", "DOMDocument"]

'''
    TODO:
    - warning on xml tags called __tag__
'''

class DOMToPython:
    def __init__(self, doc):
        self.__doc = doc

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
    def print_xml(self):
        def xml_attributes():
            attributes = ''
            for attribute, value in self.__attributes.items():
                attributes += ' '+attribute+'="'+value+'"'
            return attributes
        if self.__children:
            print ('<'+self.__tag+xml_attributes()+'>')
            for child in self.__children:
                if isinstance(child, (str,bytes)):
                    print(child)
                else:
                    child.print_xml()
            print ('</'+self.__tag+'>')
        else:
            print ('<'+self.__tag+'/>')

class DOMDocument(object):
    # setup the document with a root DOMNode and put it on a stack
    def __init__(self, root_tag, *args, **kwargs):
        root_node = DOMNode(self, root_tag, *args, **kwargs)
        self.__stack = [root_node]

    # accessing unknown items is passed to the node op top of the stack
    def __getattr__(self, item):
        return getattr(self.__stack[-1], item)

    # calling the DOMDocument with (None), pops the stack (after exit of DOMNode)
    # calling the DOMDocument with (node), pushes the node on the stack (on enter of DOMNode)
    def __call__(self, node):
        if node is None:
            self.__stack.pop()
        else:
            self.__stack.append(node)
            # return self, to allow continuation with next call
            return self
