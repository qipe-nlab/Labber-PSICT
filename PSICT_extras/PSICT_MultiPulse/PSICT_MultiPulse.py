#!/usr/bin/env python

import InstrumentDriver
import numpy as np

import os
import logging
from datetime import datetime

from PSICT_MultiPulse_tools import delistifyPulseDefs
from waveforms_handling import generatePulse, calculateWaveform, gen_pulse_sequence


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
        self.lQuadratures = [np.array([], dtype=float)] * self.nTrace
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
                self.lPulseDefinitions = delistifyPulseDefs(lRawPulseDefinitions, self.lDefKeyOrder)
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
        if quant.name[:5] == 'Trace':
            ## Recalculate waveform if necessary
            if self.isConfigUpdated():
                self.calculateWaveform()
            vData = self.getWaveformFromMemory(quant)
            dt = 1/self.getValue('Sample rate')
            value = quant.getTraceDict(vData, dt=dt)
        elif quant.name[:10] == 'Quadrature':
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
        if quant.name[:5] == 'Trace':
            iDataIndex = int(quant.name[-1]) - 1
            self._logger.debug('Fetching waveform for output {}'.format(iDataIndex))
            vData = self.lWaveforms[iDataIndex]
        elif quant.name[:10] == 'Quadrature':
            iDataIndex = int(quant.name[-1]) - 1
            self._logger.debug('Fetching waveform for output {}'.format(iDataIndex))
            vData = self.lQuadratures[iDataIndex]
        else:
            raise RuntimeError('Invalid specification for getting waveform: {}'.format(quant.name))
        return vData

    def calculateTotalSeqTime(self, pulseSeq, truncRange):
        '''
        Calculate the total time required for the specified pulse sequence with the given truncation range
        '''
        ## Get pulse definitions
        lPulseDefs = self.lPulseDefinitions
        ## Calculate total time
        totalTime = 0.0
        for pulseIndex in pulseSeq:
            oPulseDef = lPulseDefs[pulseIndex]
            totalTime += oPulseDef['w'] + oPulseDef['v'] + oPulseDef['s']
        ## Add decay time for last pulse in sequence
        totalTime += lPulseDefs[pulseSeq[-1]]['w'] * (truncRange - 1)/2
        ## Return final value
        return totalTime

    def updateHeadTime(self, dOldHeadTime, oPulseDef, bReversed = False):
        ## Get edge-to-edge length of pulse (including spacing)
        dPulseLength = oPulseDef['w'] + oPulseDef['v'] + oPulseDef['s']
        ## Increment head time and return new value
        if bReversed:
            dNewHeadTime = dOldHeadTime - dPulseLength
        else:
            dNewHeadTime = dOldHeadTime + dPulseLength
        return dNewHeadTime

    calculateWaveform = calculateWaveform
    generatePulse = generatePulse
    gen_pulse_sequence = gen_pulse_sequence

if __name__ == '__main__':
    pass
