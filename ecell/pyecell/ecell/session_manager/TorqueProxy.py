#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
#       This file is part of the E-Cell System
#
#       Copyright (C) 2017-2018 Keio University
#       Copyright (C) 2017-2018 RIKEN
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
#
# Designed by Koichi Takahashi <shafi@e-cell.org>
# Programmed by Yasuhiro Naito <ynaito@sfc.keio.ac.jp>

# -*- coding: utf-8 -*-

import os
import popen2
import re
import signal
import sys
import time
from itertools import ifilter
#import json

from ecell.session_manager.Util import *
from ecell.session_manager.SessionManager import *
from ecell.session_manager.Constants import *

QSUB = 'qsub'
QSTAT = 'qstat'
QHOST = 'pbsnodes'
QDEL = 'qdel'

class SessionProxy( AbstractSessionProxy ):
    '''SessionProxy class
    Target environment is Torque.
    '''

    def __init__( self, dispatcher, jobID ):
        AbstractSessionProxy.__init__( self, dispatcher, jobID )
        self.__theTorqueJobID = -1
        self.__theSessionProxyName = "script." + os.path.basename( getCurrentShell() )

    def __del__( self ):
        # print "SessionProxy.__del__() is called."
        self.__cancel()

    def getToqueJobID(self):    # getSGEJobID(self)
        '''return job id 
        '''
        return self.__theTorqueJobID 

    def run( self ):
        '''run process
        Return None
        '''
        if not AbstractSessionProxy.run( self ):
            return False

        # save current directory
        aCwd = os.getcwd()
        #print "\nFirst: {}".format( aCwd )

        try:
            os.chdir( self.getJobDirectory() )
            #print "JobDirStr: {}".format( self.getJobDirectory() )
            #print "JobDirFull: {}\n".format( os.getcwd() )

            args = [ QSUB ]
            args.append( '-V' )
            args.extend( ( '-d', os.getcwd() ) )
            # args.extend( ( '-S', self.getInterpreter()) )
            args.extend( ( '-o', self.getStdoutFileName() ) )
            args.extend( ( '-e', self.getStderrFileName() ) )
            args.extend( ( '-l', "ncpus=1" ) )
            args.extend( ifilter(
                    lambda x: x not in ( '-V', '-d', '-S', '-o', '-l' ),
                    self.getOptionList() ) )

            if len( self.getArguments() ):
                #anArguments = json.loads(self.getArguments()[0][13:].replace("'",'"'))
                args.append( '-F' )
                args.append( '"--parameters=\\\"{}\\\""'.format( self.getArguments()[0][13:].replace('"','\\\\\\\"') ))

            args.append( self.getScriptFileName())
            #args.extend( self.getArguments() )
            #print "CMD: " + ' '.join( args )

            msg = raiseExceptionOnError(
                RuntimeError,
                pollForOutputs( popen2.Popen3( ' '.join( args ), True ) )
                )
            #print "MSG: " + msg
            if msg == None:
                raise RuntimeError, '{} returned no result.'.format( QSUB )
            self.__theTorqueJobID = msg
        finally:
            os.chdir( aCwd )
        return True

    def __cancel( self ):
        #print self.getOwner()
        if self.__theTorqueJobID >= 0:
            # reads the result of qstat
            aCommandLine = "{} {}".format( QSTAT, self.__theTorqueJobID )
            out =  pollForOutputs( popen2.Popen3( aCommandLine, True ))[ 1 ].split( "\n" )
            aStatus = out[ 2 ].split()[ 4 ]
            if aStatus not in ( 'C', 'E' ):
                #print "DEL: {} {}".format( QDEL, self.__theTorqueJobID )
                raiseExceptionOnError( RuntimeError,
                    pollForOutputs(
                        popen2.Popen3( "{} {}".format( QDEL, self.__theTorqueJobID ), True )
                        )
                    )

    def __getStdfile( self, p ):
        if os.path.exists( p ):
            return open( p, 'rb' ).read()
        elif self.getStdoutTimeout() > 0:
            for i in range( 0, self.getStdoutTimeout() ):
                time.sleep( 1.0 )
                if os.path.exists( p ):
                    return open( p, 'rb' ).read()
        else:
            while True:
                if os.path.exists( p ):
                    return open( p, 'rb' ).read()
        
        return None

    def stop(self):
        '''stop the job
        Return None
        '''

        # When this job is running, stop it.
        if self.getStatus() == RUN:
            self.__cancel()

        # set error status
        self.setStatus( ERROR ) 

    def getStdout( self ):
        '''Return stdout(str)
        '''
        return self.__getStdfile( self.getStdoutFilePath() )

    def getStderr( self ):
        '''Return stderr(str)
        '''
        return self.__getStdfile( self.getStderrFilePath() )

class SystemProxy( AbstractSystemProxy ):
    def __init__( self, sessionManager ):
        # Call superclass's constructor.
        AbstractSystemProxy.__init__( self, sessionManager )

        # Check the existance of Torque command.
        # qsub
        for binName in ( QSUB, QSTAT, QHOST ):
            if checkCommandExistence( binName ) == False:
                raise Exception(
                    "\"%s\" is not included in the $PATH environment"\
                                % binName )
        # Initialize attributes.
        self.__theQueueList = None

    def getDefaultConcurrency( self ):
        '''returns default cpus
        Return int : the number of cpus
        The default number of cpu is calculated from the retuslt of qhost
        Here is the sample of standard output of 'pbsnodes -l all'

        k01                  job-exclusive
        k02                  free
        k03                  free
        k04                  free
        k05                  free
        k06                  free
        k07                  free
        k08                  free
        k09                  free
        k10                  free
        k11                  free
        k12                  free
        k13                  free
        k14                  free
        k15                  free
        k16                  free
        k17                  free
        k18                  free
        k19                  free
        k20                  free
        k21                  free
        k22                  free

        In this case, this method returns 22 as a default number of CPUs.
        '''

        # returns the number of cpu
        aCpuNumber = 0 # for the headers to be reduced
        for i in os.popen( "{} -l all".format( QHOST )):
            aCpuNumber = aCpuNumber + 1

        if aCpuNumber < 0:
            aCpuNumber = 0

        return aCpuNumber

    def _createSessionProxy( self ):
        '''creates and returns new SessionProxy instance'''
        return SessionProxy( self, self.getNextJobID() )

    def _updateStatus( self ):
        '''updates status
        Updates status using the result of qstat as below.

        Job ID                    Name             User            Time Use S Queue
        ------------------------- ---------------- --------------- -------- - -----
        3762.king2                STDIN            ynaito          0        R all.q          

        When the state is 'Q(queued)', 'W(waiting)', 'T(transfer)', 'E(exiting)' or 'R(running)', it is set as RUN.
        For SGE, when the state is 'Eqw(error)', the job is killed and its status is set as ERROR.
        In most of latter case, the interpreter can't find remote machine could not be found.
        However, above error does not be written stderr.
        '''

        # initializes a dict whose key is Torque job id and value is status
        aStatusDict = {}

        # reads the result of qstat
        aCommandLine = [ QSTAT ]
        #print "Owner: " + self.getOwner()
        if self.getOwner() is not None:
            aCommandLine.extend( [ '-u', self.getOwner() ] )
        #print "Owner: " + ' '.join( aCommandLine )
        out = raiseExceptionOnError(
            RuntimeError,
            pollForOutputs(
                popen2.Popen3( ' '.join( aCommandLine ), True )
                )
            ).split( "\n" )
        #print out

        # When there are running jobs, gets Torque job id and status
        if self.getOwner() is not None:
            for aLine in out[ 5: -1 ]:
                comps = aLine.split()
                aStatusDict[ comps[ 0 ] ] = comps[ 9 ]  # key = JobID, item = Status
        else:
            for aLine in out[ 2: -1 ]:
                comps = aLine.split()
                aStatusDict[ comps[ 0 ] ] = comps[ 4 ]  # key = JobID, item = Status
                # print "Status({}): {}".format( comps[ 0 ], comps[ 4 ] )

        # checks ths status of each SessionProxy
        for job in self.getSessionProxies():
            # considers only running jobs
            if job.getStatus() == RUN:
                # gets Torgue job id
                aTorqueJobID = job.getToqueJobID()

                # if there is no Torque job id in the result of qstat, the job is
                # considered to be finished
                # else if Status is 'C' or 'E', the job has been finished.
                if not aStatusDict.has_key( aTorqueJobID ):
                    # read standard error file
                    aStderrFile = job.getStderrFilePath()
                    # When something is written in standard error,
                    if os.path.exists( aStderrFile ) and \
                       os.stat( aStderrFile )[ 6 ] > 0:  # stat[6] = st_size
                        job.setStatus( ERROR )
                    else:
                        job.setStatus( FINISHED )
                elif aStatusDict[ aTorqueJobID ] in ('C','E'):  # C:completed; E:exiting
                    #time.sleep(2)  # wait filing
                    job.setStatus( FINISHED )

    def __populateQueueList( self ):
        ''' Get queue list.
        $ qstat -a
        
        king2: 
                                                                                          Req'd       Req'd       Elap
        Job ID                  Username    Queue    Jobname          SessID  NDS   TSK   Memory      Time    S   Time
        ----------------------- ----------- -------- ---------------- ------ ----- ------ --------- --------- - ---------
        3766.king2              ynaito      all.q    STDIN             99932     1     32       --   24:00:00 R  00:46:58
        $
        '''
        if self.__theQueueList != None:
            return

        lines = os.popen( "{} -a".format( QSTAT ))  # os.popen("%s -q" % QHOST) [SGE]
        for i in range( 5 ):  # skip first 5 lines.
            lines.readline()

        hostname = None
        queueList = {}
        for line in lines:
            m = re.match( r'^(\S+?)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$', line )
            queueList[ m.groups( 0 ) ] = [
                m.groups( 1 ), m.groups( 2 ), m.groups( 3 ), m.groups( 4 ), m.groups( 5 ), 
                m.groups( 6 ), m.groups( 7 ), m.groups( 8 ), m.groups( 9 ), m.groups( 10 ) ]
        lines.close()
        self.__theQueueList = queueList

    def _modifyDstScriptFile( self, dstScriptFileName, interpreterPath ):
        '''insert shebang into the script file
        Return True or False
        '''
        if interpreterPath is not None  and \
           os.access( dstScriptFileName, os.R_OK ) and os.access( dstScriptFileName, os.W_OK ):
            theShebang = '#!' +interpreterPath
            f = open( dstScriptFileName, 'r' )
            s = f.readlines()
            f.close()
            if theShebang is not s[ 0 ].rstrip():
                f = open( dstScriptFileName, 'w' )
                f.write( '{}\n\n{}'.format( theShebang, "\n".join( s ) ) )
                f.close()
            #print "Shebang is inserted."
            return True
        else:
            #print "Shebang insertion is failed."
            return False