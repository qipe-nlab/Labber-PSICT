#!/usr/bin/env python

import InstrumentDriver
import numpy as np

import os
import logging
from datetime import datetime

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
        ## Do nothing, just return value
        return value

    def performGetValue(self, quant, options = {}):
        '''
        Get the value of the specified quantity from the instrument
        '''
        ## Potentially have to do something special for vector waveforms
        if quant.isVector():
            ## Recalculate waveform if necessary
            if self.isConfigUpdated():
                self.calculateWaveform()
            vData = self.getWaveformFromMemory(quant)
            dt = 1/self.getValue('Sample rate')
            value = quant.getTraceDict(vData, dt=dt)
        else:
            value = quant.getValue()
        return value

    def getWaveformFromMemory(self, quant):
        '''Return data from calculated waveforms'''
        vData = np.zeros((self.getValue('Number of points')))
        if quant.name[-1] == '1':
            vData[100:2000] = 0.7
        elif quant.name[-1] == '2':
            vData[1500:2500] = 1.0
        else:
            pass
        return vData

    def calculateWaveform(self):
        '''Generate waveform'''

        ## Get config values
        sampleRate = self.getValue('Sample rate')

        ##TODO Calculate pulse blocks from stored parameters


        ##TODO Calculate total number of points

        ## Allocate time vector
        self.vTime = np.arange(self.getValue('Number of points'), dtype=float)/sampleRate

if __name__ == '__main__':
    pass
