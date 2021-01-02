#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
#       This file is part of the E-Cell System
#
#       Copyright (C) 1996-2020 Keio University
#       Copyright (C) 2008-2020 RIKEN
#       Copyright (C) 2005-2009 The Molecular Sciences Institute
#
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
#
# E-Cell System is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
# 
# E-Cell System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with E-Cell System -- see the file COPYING.
# If not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# 
#END_HEADER

__all__ = [
    'XML',
    ]

try:
    from gtk import Builder, Action
    from warnings import warn
    import os

    class XML(object):
        def __init__(self, fname, root=None, domain="", typedict={}):
            self.builder = Builder()
            if domain:
                self.builder.set_translation_domain(domain)
            cwd = os.getcwd()
            os.chdir(os.path.dirname(fname))
            self.builder.add_from_file(fname)
            os.chdir(cwd)

        def signal_connect(self, handler_name, func):
            self.builder.connect(handler_name, func)

        def signal_autoconnect(self, dict):
            self.builder.connect_signals(dict)

        def get_widget(self, name):
            obj = self.builder.get_object(name)
            if isinstance(obj, Action):
                obj = obj.get_proxies()[0]
            return obj

    #
    # The following code has been pasted from gtk-builder-convert
    #
    # Copyright (C) 2006-2008 Async Open Source
    #                         Henrique Romano <henrique@async.com.br>
    #                         Johan Dahlin <jdahlin@async.com.br>
    #

    from xml.dom import minidom, Node

    DIALOGS = ['GtkDialog',
               'GtkFileChooserDialog',
               'GtkMessageDialog']
    WINDOWS = ['GtkWindow'] + DIALOGS

    def get_child_nodes(node):
        assert node.tagName == 'object'
        nodes = []
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName != 'child':
                continue
            nodes.append(child)
        return nodes

    def get_properties(node):
        assert node.tagName == 'object'
        properties = {}
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName != 'property':
                continue
            value = child.childNodes[0].data
            properties[child.getAttribute('name')] = value
        return properties

    def get_property(node, property_name):
        assert node.tagName == 'object'
        properties = get_properties(node)
        return properties.get(property_name)

    def get_property_node(node, property_name):
        assert node.tagName == 'object'
        properties = {}
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName != 'property':
                continue
            if child.getAttribute('name') == property_name:
                return child

    def get_signal_nodes(node):
        assert node.tagName == 'object'
        signals = []
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName == 'signal':
                signals.append(child)
        return signals

    def get_property_nodes(node):
        assert node.tagName == 'object'
        properties = []
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            # FIXME: handle comments
            if child.tagName == 'property':
                properties.append(child)
        return properties

    def get_accelerator_nodes(node):
        assert node.tagName == 'object'
        accelerators = []
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName == 'accelerator':
                accelerators.append(child)
        return accelerators

    def get_object_node(child_node):
        assert child_node.tagName == 'child', child_node
        nodes = []
        for node in child_node.childNodes:
            if node.nodeType != Node.ELEMENT_NODE:
                continue
            if node.tagName == 'object':
                nodes.append(node)
        assert len(nodes) == 1, nodes
        return nodes[0]

    def copy_properties(node, props, prop_dict):
        assert node.tagName == 'object'
        for prop_name in props:
            child = get_property_node(node, prop_name)
            if child is not None:
                prop_dict[prop_name] = child

        return node

except:
    from gtk.glade import *
