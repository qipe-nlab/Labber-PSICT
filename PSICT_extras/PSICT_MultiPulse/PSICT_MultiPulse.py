#!/usr/bin/env python

import InstrumentDriver
import numpy as np

import os
import logging
from datetime import datetime

from PSICT_MultiPulse_tools import delistifyPulseDefs

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
        else:
            raise RuntimeError('Invalid specification for getting waveform: {}'.format(quant.name))
        return vData

    def calculateWaveform(self):
        '''
        Generate waveform, selecting sequence based on 'Pulse sequence counter' value
        '''
        self._logger.info('Generating waveform...')
        ## Get config values
        sampleRate = self.getValue('Sample rate')
        truncRange = self.getValue('Truncation range')
        seqCounter = int(self.getValue('Pulse sequence counter'))
        ## Fetch pulse sequence list based on counter
        pulseSeq = self.lPulseSequences[seqCounter]
        self._logger.debug('Fetched pulse sequence at index {}: {}'.format(pulseSeq, seqCounter))
        ## Calculate or use existing number of points
        if self.getValue('Use fixed number of points'):
            pass
        else:
            ## Get total time for pulse sequence
            totalTime = self.calculateTotalSeqTime(pulseSeq, truncRange)
            self._logger.debug('Total time calculated: {}'.format(totalTime))
            ## Get total number of points
            totalNPoints = int(np.round(totalTime * sampleRate))
            self._logger.debug('Total number of points: {}'.format(totalNPoints))
            self.setValue('Number of points', totalNPoints)
        ## Allocate master time vector
        self.vTime = np.arange(self.getValue('Number of points'), dtype=float)/sampleRate
        ## Re-create waveforms with correct size
        self.lWaveforms = [np.zeros((self.getValue('Number of points')), dtype=float)] \
                                * self.nTrace
        ## Generate pulse sequence
        iHeadIndex = 0 # TODO: allow specification of custom start point?
        for iPulseIndex in pulseSeq:
            ## Get time corresponding to head index from master time vector
            dHeadTime = self.vTime[iHeadIndex]
            ## Get master times relative to head time
            vRelTimeMaster = self.vTime - dHeadTime
            ## Generate pulse
            vNewPulse = self.generatePulse(vRelTimeMaster, dHeadTime, \
                                           self.lPulseDefinitions[iPulseIndex])
            ## Add new pulse to waveform at index
            iOutputIndex = int(self.lPulseDefinitions[iPulseIndex]['o']) - 1
            self.lWaveforms[iOutputIndex] = self.lWaveforms[iOutputIndex] + vNewPulse
            ## Update head index
            iHeadIndex = self.updateHeadIndex(iHeadIndex, self.lPulseDefinitions[iPulseIndex])
        ##
        self._logger.info('Waveform generation completed.')

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

    def generatePulse(self, vRelTimes, dAbsTime, oPulseDef):
        '''
        Generate a pulse with the given definition

        NB times are specified relative to the start point (ie the leading-edge FWHM point), and so can be negative!
        '''
        ## Get definition params
        dWidth = oPulseDef['w']
        dPlateau = oPulseDef['v']
        dAmp = oPulseDef['a']
        dStd = dWidth / np.sqrt(2 * np.pi)
        ## Get other params
        truncRange = self.getValue('Truncation range')
        ## Shift times such that 0 is in the middle of the pulse
        vShiftedTimes = vRelTimes - (dWidth + dPlateau) / 2
        ## Generate envelope; algorithm copied from SQPG driver
        if dPlateau > 0:
            ## Start with plateau
            vPulse = (vShiftedTimes >= -dPlateau/2) & (vShiftedTimes < dPlateau/2)
            ## Add rise and fall before and after plateau if applicable
            if dStd > 0:
                ## Leading edge
                vPulse = vPulse + (vShiftedTimes < -dPlateau/2) * \
                    (np.exp(-(vShiftedTimes + dPlateau/2)**2/(2*dStd**2)))
                ## Trailing edge
                vPulse = vPulse + (vShiftedTimes >= dPlateau/2) * \
                    (np.exp(-(vShiftedTimes - dPlateau/2)**2/(2*dStd**2)))
        else:
            ## No plateau - only gaussian
            if dStd > 0:
                vPulse = np.exp(-vShiftedTimes**2 / (2*dStd**2))
            else:
                vPulse = np.zeros_like(vShiftedTimes)
        ## Apply truncation range
        vPulse[vShiftedTimes < -(dPlateau/2)-(truncRange/2)*dWidth] = 0.0
        vPulse[vShiftedTimes > (dPlateau/2)+(truncRange/2)*dWidth] = 0.0
        ## Scale by amplitude
        vPulse = vPulse * dAmp
        ## Get modulation parameters
        freq = 2 * np.pi * oPulseDef['f']
        phase = oPulseDef['p']
        ## Apply modulation
        vPulseMod = vPulse * (np.cos(freq*(vRelTimes+dAbsTime) - phase))
        ## Return value
        return vPulseMod

    def updateHeadIndex(self, iOldHeadIndex, oPulseDef):
        ## Get edge-to-edge length of pulse (including spacing)
        dPulseLength = oPulseDef['w'] + oPulseDef['v'] + oPulseDef['s']
        ## Convert to indices using sample rate
        iIndexDelta = int(np.round(dPulseLength * self.getValue('Sample rate')))
        ## Increment head index and return new value
        iNewHeadIndex = iOldHeadIndex + iIndexDelta
        return iNewHeadIndex

if __name__ == '__main__':
    pass
