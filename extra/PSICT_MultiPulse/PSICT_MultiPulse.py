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
        return 0

if __name__ == '__main__':
    pass
