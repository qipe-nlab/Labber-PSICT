#!/usr/bin/env python

import InstrumentDriver
import numpy as np

import os
import logging
from datetime import datetime

from PSICT_MultiPulse_tools import pulseDefList2DictList

class Driver(InstrumentDriver.InstrumentWorker):
    """ This class implements the PSICT-MultiPulse pulse generator"""

    def performOpen(self, options = {}):
        '''Open the instrument connection'''
        ## Start logging object
        self.initLogger()
        ## Number of traces - corresponds to number of outputs
        self.nTrace = 4
        ## Waveform and time containers
        self.lWaveforms = [np.array([], dtype=float)] * self.nTrace
        self.vTime = np.array([], dtype=float)
        ## Pulse definition and sequence containers
        self.lDefKeyOrder = []
        self.lPulseDefinitions = []
        self.lPulseSequences = []
        ## Log completion of opening operation
        self._logger.info('Instrument opened successfully.')

    def initLogger(self):
        ## Dir and file setup
        log_dir = os.path.expanduser('~/MultiPulse_logs/')
        log_file = 'MultiPulse_{:%y%m%d_%H%M%S}'.format(datetime.now())+'.log'
        ## Create log dir if it does not exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_path = os.path.join(log_dir, log_file)
        ## logger object config and init
        logging.basicConfig(filename = log_path, filemode = 'a', \
                            level = logging.DEBUG,\
                            format = '%(asctime)s %(name)-8s: %(message)s', \
                            datefmt = '%y-%m-%d %H:%M:%S')
        self._logger = logging.getLogger('MultiPulse')
        self._logger.info('Logging initialized to {}'.format(log_path))

    def performSetValue(self, quant, value, sweepRate = 0.0, options = {}):
        '''
        Set the specified quantity to the given value

        Should return the actual value set by the instrument.
        '''
        self._logger.debug('SetValue: {} {} {}'.format(quant.name, value, type(value)))
        ## If the value is a pulse definitions or sequences file path, pull the contents of the file
        if quant.name == 'Pulse definitions file':
            ## Only fetch if input string is not empty
            if value is not '':
                self._logger.debug('Pulling pulse definitions from file: {}'.format(value))
                ## Get pulse definitions from file
                with open(value, 'r') as pdfile:
                    self.lDefKeyOrder = pdfile.readline().strip().split(',')
                    lRawPulseDefinitions = [[float(yy) for yy in xx.strip().split(',')] \
                                               for xx in pdfile.readlines()]
                ## Parse raw pulse definitions
                self.lPulseDefinitions = pulseDefList2DictList(lRawPulseDefinitions, self.lDefKeyOrder)
                self._logger.debug('Pulse definitions: {}'.format(self.lPulseDefinitions))
        elif quant.name == 'Pulse sequences file':
            ## Only fetch if input string is not empty
            if value is not '':
                self._logger.debug('Pulling pulse sequences from file: {}'.format(value))
                ## Get pulse definitions from file
                with open(value, 'r') as psfile:
                    self.lPulseSequences = [[int(yy) for yy in xx.strip().split(',')] \
                                                 for xx in psfile.readlines()]
                self._logger.debug('Imported pulse sequences: {}'.format(self.lPulseSequences))
        ## Return value, regardless of quant
        return value

    def performGetValue(self, quant, options = {}):
        '''
        Get the value of the specified quantity from the instrument
        '''
        ## Ensure that vector waveforms are updated before returning value
        if quant.isVector():
            ## Recalculate waveform if necessary
            if self.isConfigUpdated():
                self.calculateWaveform()
            vData = self.getWaveformFromMemory(quant)
            dt = 1/self.getValue('Sample rate')
            value = quant.getTraceDict(vData, dt=dt)
        else:
            ## All other values can be returned as-is
            value = quant.getValue()
        ## Log GetValue operation
        self._logger.debug('GetValue: {} {} {}'.format(quant.name, value, type(value)))
        return value

    def getWaveformFromMemory(self, quant):
        '''Return data from calculated waveforms'''
        vData = np.zeros((self.getValue('Number of points')))
        if quant.name == 'Trace 1':
            vData[2000:4000] = -0.1
        elif quant.name[-1] == '1':
            vData[100:2000] = 0.7
        elif quant.name[-1] == '2':
            vData[1500:2500] = 1.0
        else:
            pass
        return vData

    def calculateWaveform(self):
        '''Generate waveform'''
        self._logger.info('Generating waveform...')

        ## Verify stored values for pulse definition and sequence paths
        pPulseDefFile = self.getValue('Pulse definitions file')
        self._logger.debug('## Pulse definitions file: {}'.format(pPulseDefFile))
        self._logger.debug('Does this file exist? {}'.format(os.path.exists(pPulseDefFile)))
        pPulseSeqFile = self.getValue('Pulse sequences file')
        self._logger.debug('## Pulse sequences file: {}'.format(pPulseSeqFile))
        self._logger.debug('Does this file exist? {}'.format(os.path.exists(pPulseSeqFile)))

        ## Get config values
        sampleRate = self.getValue('Sample rate')

        ##TODO Calculate pulse blocks from stored parameters


        ##TODO Calculate total number of points

        ## Allocate time vector
        self.vTime = np.arange(self.getValue('Number of points'), dtype=float)/sampleRate
        ##
        self._logger.info('Waveform generation completed.')

if __name__ == '__main__':
    pass
