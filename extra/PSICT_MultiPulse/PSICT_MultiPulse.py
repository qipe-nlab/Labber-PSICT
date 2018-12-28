#!/usr/bin/env python

import InstrumentDriver
import numpy as np


class Driver(InstrumentDriver.InstrumentWorker):
    """ This class implements the PSICT-MultiPulse pulse generator"""

    def performOpen(self, options = {}):
        '''Open the instrument connection'''

    def performSetValue(self, quant, value, sweepRate = 0.0, options = {}):
        return value

    def performGetValue(self, quant, options = {}):
        ## Potentially have to do something special for vector waveforms
        if quant.isVector():
            vData = self.getWaveformFromMemory(quant)
            dt = 1E-9
            value = quant.getTraceDict(vData, dt=dt)
        else:
            value = quant.getValue()
        return value

    def getWaveformFromMemory(self, quant):
        vData = np.array([], dtype = float)
        return vData

if __name__ == '__main__':
    pass
