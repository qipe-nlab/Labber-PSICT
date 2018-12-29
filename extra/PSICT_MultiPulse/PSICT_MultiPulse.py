#!/usr/bin/env python

import InstrumentDriver
import numpy as np


class Driver(InstrumentDriver.InstrumentWorker):
    """ This class implements the PSICT-MultiPulse pulse generator"""

    def performOpen(self, options = {}):
        '''Open the instrument connection'''
        ## Number of traces - corresponds to number of outputs
        self.nTrace = 4
        ## Waveform and time containers
        self.lWaveforms = [np.array([], dtype=float)] * self.nTrace
        self.vTime = np.array([], dtype=float)

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
