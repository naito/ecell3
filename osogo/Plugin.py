#!/usr/bin/env python2

import sys
import os
import imp

from config import *

class PluginModule:

    def __init__( self, name, path=PLUGIN_PATH ):

        self.theName = name

        aFp, aPath, self.theDescription\
             = imp.find_module( self.theName, PLUGIN_PATH )

        self.theDirectoryName = os.path.dirname( aPath )
        
        try:
            self.theModule = imp.load_module( self.theName,
                                              aFp,
                                              aPath,
                                              self.theDescription )
        finally:
            # close fp even in exception
            if aFp:
                aFp.close()


    def createInstance( self, sim, data, parent=None ):
        aConstructor = self.theModule.__dict__[self.theName]
        anArgumentTuple = ( self.theDirectoryName, sim , data )
        apply( aConstructor, anArgumentTuple )



class PluginManager:

    def __init__( self ):
        self.thePluginMap = {}
        self.theInstanceList = []

    def createInstance( self, classname, sim, data, parent=None ):
        try:
            aPlugin = self.thePluginMap[ classname ]
        except KeyError:
            aPlugin = PluginModule( classname )
            self.thePluginMap[ classname ] = aPlugin

        anInstance = aPlugin.createInstance( sim, data, parent )
        self.appendInstance( anInstance )

        return anInstance

    def update( self ):
        for anInstance in self.theInstanceList:
            anInstance.update()

    def appendInstance( self, instance ):
        self.theInstanceList.append( instance )

    def removeInstance( self, instance ):
        self.theInstanceList.remove( instance )

        
if __name__ == "__main__":
    pass
