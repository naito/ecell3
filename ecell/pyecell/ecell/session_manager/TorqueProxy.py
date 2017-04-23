#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
#       This file is part of the E-Cell System
#
#       Copyright (C) 1996-2015 Keio University
#       Copyright (C) 2008-2015 RIKEN
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

        try:
            os.chdir( self.getJobDirectory() )

            args = [ QSUB ]
            for key, val in self.getEnvironmentVariables().iteritems():  # EnvironmentVariables: e.g. 'ECELL3_DM_PATH' = dmpath
                args.extend( ( '-v', key + '=' + val ) )                 # -v [variable_list] Expands the list of environment variables that are exported to the job.
            # args.append( '-cwd' )                                        # PBS_O_WORKDIR = The absolute path of the current working directory of the qsub command.
            args.extend( ( '-S', self.getInterpreter()) )                # -S [path_list] Declares the path to the desires shell for this job.
                                                                         #     e.g. qsub script.sh -S /bin/tcsh@node1,/usr/bin/tcsh@node2
            args.extend( ( '-o', self.getStdoutFileName() ) )            # -o [path] Defines the path to be used for the standard output stream of the batch job. 
                                                                         #     The path argument is of the form: [hostname:]path_name
            args.extend( ( '-e', self.getStderrFileName() ) )            # -e [path] Standard Error File
                                                                         #     Defines the path to be used for the standard error stream 
                                                                         #     of the batch job. The path argument is of the form:
            args.extend( ifilter(
                    lambda x: x not in ( '-s' '-v', '-cwd', '-o', '-e' ),
                    self.getOptionList() ) )
            args.append( self.getScriptFileName() )
            args.extend( self.getArguments() )

            msg = raiseExceptionOnError(
                RuntimeError,
                pollForOutputs( popen2.Popen3( args, True ) )
                )
            m = re.match(
                r'^(\d+\.\w+)$', msg
                )
            if m == None:
                raise RuntimeError, '%s returned unexpected result: %s' % (
                        QSUB, msg )
            self.__theTorqueJobID = m.group( 1 )
        finally:
            os.chdir( aCwd )
        return True

    def __cancel( self ):
        if self.__theTorqueJobID >= 0:
            raiseExceptionOnError( RuntimeError,
                pollForOutputs(
                    popen2.Popen3( ( QDEL, self.__theTorqueJobID ), True )
                    )
                )

    def stop(self):
        '''stop the job
        Return None
        '''

        # When this job is running, stop it.
        if self.getStatus() == RUN:
            self.__cancel()

        # set error status
        self.setStatus( ERROR ) 

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
        #if self.getOwner() is not None:
        #    aCommandLine.extend( [ '-u', self.getOwner() ] )
        out = raiseExceptionOnError(
            RuntimeError,
            pollForOutputs(
                popen2.Popen3( aCommandLine, True )
                )
            ).split( "\n" )

        # When there are running jobs, gets Torque job id and status
        for aLine in out[ 2: -1 ]:
            comps = aLine.split()
            aStatusDict[ comps[ 0 ] ] = comps[ 4 ]  # key = JobID, item = Status

        # checks ths status of each SessionProxy
        for job in self.getSessionProxies():
            # considers only running jobs
            if job.getStatus() == RUN:
                # gets Torgue job id
                aTorqueJobID = job.getToqueJobID()

                # there is no Torque job id in the result of qstat, the job is 
                # considered to be finished
                if not aStatusDict.has_key( aTorqueJobID ):
                    # read standard error file
                    aStderrFile = job.getStderrFilePath()
                    # When something is written in standard error,
                    if os.path.exists( aStderrFile ) and \
                       os.stat( aStderrFile )[ 6 ] > 0:
                        job.setStatus( ERROR )
                    else:
                        job.setStatus( FINISHED )
                else:
                    # When job is running,
                    if aStatusDict[ aTorqueJobID ].find( 'E' ) != -1:
                        # When character 'E' is included in the status,
                        job.stop()
                    else:
                        pass

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
