#!/bin/python3
# -*- coding: utf-8 -*-
from PSICT_MultiPulse_tools import delistifyPulseDefs
import numpy as np


def calculateWaveform(self):
    '''
    Generate waveform, selecting sequence based on 'Pulse sequence counter' value
    '''
    ## Skip generation if no waveforms present (eg when starting instrument)
    if self.lPulseSequences == []:
        self._logger.info('No sequences specified; skipping waveform generation...')
        return
    self._logger.info('Generating waveform...')
    ## Get config values
    sampleRate = self.getValue('Sample rate')
    truncRange = self.getValue('Truncation range')
    dFirstPulseDelay = self.getValue('First pulse delay')
    seqCounter = int(self.getValue('Pulse sequence counter'))
    bReversed = self.getValue('Generate from final pulse')
    dFinalPulseTime = self.getValue('Final pulse time')
    if bReversed:
        self._logger.debug('Generating sequence in reverse, with final pulse at {}'.format(dFinalPulseTime))
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
    self.vTime = np.arange(int(self.getValue('Number of points')), dtype=float)/sampleRate
    key_list = ['Use global DRAG', 'Global DRAG coefficient', 'Apply DRAG to square pulses', 'Truncation range', 'Sample rate']
    params_dict = {k:self.getValue(k) for k in key_list}
    ## Get first head time
    if bReversed:
        dHeadTime = dFinalPulseTime
        # iHeadIndex = int(np.round(dFinalPulseTime * sampleRate))
    else:
        dHeadTime = dFirstPulseDelay
        # iHeadIndex = int(np.round(dFirstPulseDelay * sampleRate))
    ## Reverse pulse sequence if generating from the back
    if bReversed:
        pulseSeq = pulseSeq[::-1]
    ## Generate pulse sequence
    self.lWaveforms, self.lQuadratures = gen_pulse_sequence(
        self,
        self.nTrace,
        self.getValue('Number of points'),
        pulseSeq,
        self.vTime,
        dHeadTime,
        self.lPulseDefinitions,
        params_dict,
        bReversed
    )
           
    self._logger.info('Waveform generation completed.')


def gen_pulse_sequence(self, nTrace, num_points, pulseSeq, vTime, dHeadTime, pulseDef, params_dict, bReversed):
    ## Re-create waveforms with correct size
    lWaveforms   = np.zeros((nTrace, int(num_points)), dtype=float)
    lQuadratures = np.zeros((nTrace, int(num_points)), dtype=float)
    for iPulse, iPulseIndex in enumerate(pulseSeq):
        ## Generate pulse
        vNewPulse = self.generatePulse(vTime, dHeadTime, pulseDef[iPulseIndex], params_dict)
        vNewPulseQuad = self.generatePulse(vTime, dHeadTime, pulseDef[iPulseIndex], params_dict, genQuadrature=True)
        ## Add new pulse to waveform at index
        iOutputIndex = int(pulseDef[iPulseIndex]['o']) - 1
        lWaveforms[iOutputIndex][vNewPulse['imin']:vNewPulse['imax']+1] += vNewPulse['pulse']
        lQuadratures[iOutputIndex][vNewPulseQuad['imin']:vNewPulseQuad['imax']+1] += vNewPulseQuad['pulse']
        ## Update head time
        if bReversed:
            ## Don't attempt to fetch 'previous' pulse for 'first' pulse in sequence
            if iPulse < len(pulseSeq) - 1:
                dHeadTime = self.updateHeadTime(dHeadTime, pulseDef[pulseSeq[iPulse+1]], bReversed=True)
            else:
                pass
        else:
            dHeadTime = self.updateHeadTime(dHeadTime, pulseDef[iPulseIndex])

    return lWaveforms, lQuadratures



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


def generatePulse(self, vTimes, dAbsTime, oPulseDef, params_dict, genQuadrature=False):
    '''
    Generate a pulse with the given definition

    NB times are specified relative to the start point (ie the leading-edge FWHM point), and so can be negative!
    '''
    ## Get definition params
    dWidth = oPulseDef['w']
    dPlateau = oPulseDef['v']
    dAmp = oPulseDef['a']
    ## Use global DRAG if required, otherwise take from pulse definition
    bUseGlobalDrag = params_dict['Use global DRAG']
    if bUseGlobalDrag:
        dDragScaling = params_dict['Global DRAG coefficient']
    else:
        dDragScaling = oPulseDef['DRAG']
    dStd = dWidth / np.sqrt(2 * np.pi)
    ## Get other params
    truncRange = params_dict['Truncation range']
    ## Apply DRAG if not square pulse
    bApplyDragToSquare = params_dict['Apply DRAG to square pulses']

    #vShiftedTimes = vRelTimes
    vShiftedTimes = vTimes # - dAbsTime
    deltaT = 1/self.getValue("Sample rate") #vShiftedTimes[1]-vShiftedTimes[0]
    t0 = vShiftedTimes[0] - dAbsTime
    # There's still a small difference here for square enveloppes. Maybe due to the comparisons with floats?
    tmin = (-(dPlateau) - truncRange*dWidth + dWidth + dPlateau )/2 - t0
    tmax = ( (dPlateau) + truncRange*dWidth + dWidth + dPlateau )/2 - t0
    imin = int(np.round(tmin/deltaT)) 
    imax = int(np.round(tmax/deltaT))

    # We bleed outside of the truncation range to compute the Drag term accurately
    if (dStd > 0 or bApplyDragToSquare) and (dDragScaling!=0):
        # The extra points will be padded to 0 after the Drag term is computed
        bleed_idx = 3   # I think 1 would be sufficient, nonetheless 3 is safer and not much slower
        imin -= bleed_idx
        imax += bleed_idx

    vShiftedTimes = vShiftedTimes[imin:imax+1] - (dWidth + dPlateau) / 2 - dAbsTime
    vRelTimes = vShiftedTimes + (dWidth + dPlateau) / 2

    # Trying to correct time errors by rounding to sample points
    vShiftedTimes = np.round(vShiftedTimes/deltaT)*deltaT
    vRelTimes = np.round(vRelTimes/deltaT)*deltaT

    ## Generate envelope; algorithm copied from SQPG driver
    if dPlateau > 0:
        ## Start with plateau
        vPulse = np.zeros(vShiftedTimes.shape)
        if len(vPulse) or len(vShiftedTimes):
            vPulse[int(np.round((-vShiftedTimes[0]-dPlateau/2)/deltaT)):int(np.round((-vShiftedTimes[0]+dPlateau/2)/deltaT))] = 1
        ## Add rise and fall before and after plateau if applicable
        if dStd > 0:
            ## Leading edge
            lead_idx = int(round((-vShiftedTimes[0]-dPlateau/2)/deltaT))
            vPulse[:lead_idx] += (np.exp(-(vShiftedTimes[:lead_idx] + dPlateau/2)**2/(2*dStd**2)))
            ## Trailing edge
            tail_idx = int(round((-vShiftedTimes[0]+dPlateau/2)/deltaT))
            vPulse[tail_idx:] += (np.exp(-(vShiftedTimes[tail_idx:] - dPlateau/2)**2/(2*dStd**2)))
    else:
        ## No plateau - only gaussian
        if dStd > 0:
            vPulse = np.exp(-vShiftedTimes**2 / (2*dStd**2))
        else:
            vPulse = np.zeros(vShiftedTimes.shape)
    ## Scale by amplitude
    vPulse = vPulse * dAmp
    if (dStd > 0 or bApplyDragToSquare) and (dDragScaling!=0):
        # The Drag term will bleed outside of the truncation range, but the calculation will be accurate within it
        vDrag = dDragScaling * np.gradient(vPulse) * self.getValue('Sample rate')
        # We now respect the truncation range after the Drag term is computed
        vPulse = vPulse[bleed_idx:-bleed_idx]
        vDrag = vDrag[bleed_idx:-bleed_idx]
        vRelTimes = vRelTimes[bleed_idx:-bleed_idx]
        imin += bleed_idx
        imax -= bleed_idx
    else:
        vDrag = np.zeros(vPulse.shape)

    ## Get modulation parameters
    freq = 2 * np.pi * oPulseDef['f']
    phase = oPulseDef['p'] * np.pi/180
    ## Apply modulation - check for fixed phase
    function = np.cos if not genQuadrature else np.sin
    if genQuadrature:
        vPulse *= oPulseDef['r']
        phase += oPulseDef['d']* np.pi/180
    if oPulseDef['fix_phase']:
        vPulseMod = vPulse * (function(freq*vRelTimes - phase)) - vDrag * (function(freq*vRelTimes - phase + np.pi/2))
    else:
        vPulseMod = vPulse * (function(freq*(vRelTimes+dAbsTime) - phase)) - vDrag * (function(freq*(vRelTimes+dAbsTime) - phase + np.pi/2))
    ## Return value
    return dict(imin=imin, imax=imax, pulse=vPulseMod)


# Legacy kept explicitly as-is for comparison testing
def calculateWaveform_legacy(self):
    '''
    Generate waveform, selecting sequence based on 'Pulse sequence counter' value
    '''
    self._logger.debug('Using legacy calculateWaveform method')
    ## Skip generation if no waveforms present (eg when starting instrument)
    if self.lPulseSequences == []:
        self._logger.info('No sequences specified; skipping waveform generation...')
        return
    self._logger.info('Generating waveform...')
    ## Get config values
    sampleRate = self.getValue('Sample rate')
    truncRange = self.getValue('Truncation range')
    dFirstPulseDelay = self.getValue('First pulse delay')
    seqCounter = int(self.getValue('Pulse sequence counter'))
    bReversed = self.getValue('Generate from final pulse')
    dFinalPulseTime = self.getValue('Final pulse time')
    if bReversed:
        self._logger.debug('Generating sequence in reverse, with final pulse at {}'.format(dFinalPulseTime))
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
    self.vTime = np.arange(int(self.getValue('Number of points')), dtype=float)/sampleRate
    ## Re-create waveforms with correct size
    self.lWaveforms = [np.zeros((int(self.getValue('Number of points'))), dtype=float)] \
                            * self.nTrace
    self.lQuadratures = [np.zeros((int(self.getValue('Number of points'))), dtype=float)] \
                            * self.nTrace
    ## Get first head time
    if bReversed:
        dHeadTime = dFinalPulseTime
        # iHeadIndex = int(np.round(dFinalPulseTime * sampleRate))
    else:
        dHeadTime = dFirstPulseDelay
        # iHeadIndex = int(np.round(dFirstPulseDelay * sampleRate))
    ## Reverse pulse sequence if generating from the back
    if bReversed:
        pulseSeq = pulseSeq[::-1]
    ## Generate pulse sequence
    for iPulse, iPulseIndex in enumerate(pulseSeq):
        ## Head time already set
        # ## Get time corresponding to head index from master time vector
        # dHeadTime = self.vTime[iHeadIndex]
        ## Get master times relative to head time
        vRelTimeMaster = self.vTime - dHeadTime
        ## Generate pulse
        vNewPulse = self.generatePulse(vRelTimeMaster, dHeadTime, \
                                       self.lPulseDefinitions[iPulseIndex])
        vNewPulseQuad = self.generatePulse(vRelTimeMaster, dHeadTime, \
                                       self.lPulseDefinitions[iPulseIndex], genQuadrature=True)
        ## Add new pulse to waveform at index
        iOutputIndex = int(self.lPulseDefinitions[iPulseIndex]['o']) - 1
        self.lWaveforms[iOutputIndex] = self.lWaveforms[iOutputIndex] + vNewPulse
        self.lQuadratures[iOutputIndex] = self.lQuadratures[iOutputIndex] + vNewPulseQuad
        ## Update head time
        if bReversed:
            ## Don't attempt to fetch 'previous' pulse for 'first' pulse in sequence
            if iPulse < len(pulseSeq) - 1:
                dHeadTime = self.updateHeadTime(dHeadTime, \
                              self.lPulseDefinitions[pulseSeq[iPulse+1]], bReversed=True)
            else:
                pass
        else:
            dHeadTime = self.updateHeadTime(dHeadTime, \
                                            self.lPulseDefinitions[iPulseIndex])
    ##
    self._logger.info('Waveform generation completed.')



# Legacy kept explicitely as-is for comparison testing
def generatePulse_legacy(self, vRelTimes, dAbsTime, oPulseDef, genQuadrature=False):
    '''
    Generate a pulse with the given definition

    NB times are specified relative to the start point (ie the leading-edge FWHM point), and so can be negative!
    '''
    ## Get definition params
    dWidth = oPulseDef['w']
    dPlateau = oPulseDef['v']
    dAmp = oPulseDef['a']
    ## Use global DRAG if required, otherwise take from pulse definition
    bUseGlobalDrag = self.getValue('Use global DRAG')
    if bUseGlobalDrag:
        dDragScaling = self.getValue('Global DRAG coefficient')
    else:
        dDragScaling = oPulseDef['DRAG']
    dStd = dWidth / np.sqrt(2 * np.pi)
    ## Get other params
    truncRange = self.getValue('Truncation range')
    ## Shift times such that 0 is in the middle of the pulse
    vShiftedTimes = vRelTimes - (dWidth + dPlateau) / 2
### ROUNDING ADDDED FOR TESTING, NOT ORIGINAL LEGACY, LIKELY LEAD TO SOME MORE NUMERICAL ERRORS ###
    # Trying to correct time errors by rounding to sample points
    deltaT = 1/self.getValue("Sample rate")
    vShiftedTimes = np.round(vShiftedTimes/deltaT)*deltaT
    vRelTimes = np.round(vRelTimes/deltaT)*deltaT
### END ROUNDING SECTION ###
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
    ## Apply DRAG if not square pulse
    bApplyDragToSquare = self.getValue('Apply DRAG to square pulses')
    if dStd > 0 or bApplyDragToSquare:
        vDrag = dDragScaling * np.gradient(vPulse) * self.getValue('Sample rate')
    else:
        vDrag = np.zeros_like(vPulse)

    ## Get modulation parameters
    freq = 2 * np.pi * oPulseDef['f']
    phase = oPulseDef['p'] * np.pi/180
    ## Apply modulation - check for fixed phase
    function = np.cos if not genQuadrature else np.sin
    if genQuadrature:
        vPulse *= oPulseDef['r']
        phase += oPulseDef['d']* np.pi/180
    if oPulseDef['fix_phase']:
        vPulseMod = vPulse * (function(freq*vRelTimes - phase)) \
                    -vDrag * (function(freq*vRelTimes - phase + np.pi/2))
    else:
        vPulseMod = vPulse * (function(freq*(vRelTimes+dAbsTime) - phase)) \
                    -vDrag * (function(freq*(vRelTimes+dAbsTime) - phase + np.pi/2))
    ## Return value
    return vPulseMod


def updateHeadTime(self, dOldHeadTime, oPulseDef, bReversed = False):
    ## Get edge-to-edge length of pulse (including spacing)
    dPulseLength = oPulseDef['w'] + oPulseDef['v'] + oPulseDef['s']
    ## Increment head time and return new value
    if bReversed:
        dNewHeadTime = dOldHeadTime - dPulseLength
    else:
        dNewHeadTime = dOldHeadTime + dPulseLength
    return dNewHeadTime

# **************************************************************** #
#
#   Follows testing code without any Labber dependencies
#
# **************************************************************** #


class dummy_logger():
    def __getattr__(self, attr):
        return lambda *args, **kwargs: print('{:s}:\t'.format(attr), *args, kwargs if kwargs else '')

class test_self():
    def __init__(self, *args, **kwargs):
        self._logger = dummy_logger()
        self.nTrace = kwargs.get('nTrace', 4)
        
        with open('waveforms_sequences.txt', 'r') as psfile:
            self.lPulseSequences = [[int(yy) for yy in xx.strip().split(',')] for xx in psfile.readlines()]
        with open('waveforms_definitions.txt', 'r') as pdfile:
            self.lDefKeyOrder = pdfile.readline().strip().split(',')
            lRawPulseDefinitions = [[float(yy) for yy in xx.strip().split(',')] for xx in pdfile.readlines()]
            self.lPulseDefinitions = delistifyPulseDefs(lRawPulseDefinitions, self.lDefKeyOrder)

        self.values_dict = {
                'Pulse sequence counter': 40,   # Odd ones are too simple
                'Sample rate': 1e9,
                'Truncation range': 3,
                'First pulse delay': 1e-6,
                'Generate from final pulse': True,
                'Final pulse time': 199e-6,
                'Use fixed number of points': True,
                'Use global DRAG': True,
                'Global DRAG coefficient': 1e-9,
                'Apply DRAG to square pulses': 0,
                'MultiPulse_sequence_duration': 200e-6,
                }
        self.values_dict['Number of points'] = self.values_dict['MultiPulse_sequence_duration']*self.values_dict['Sample rate']

    def getValue(self, key):
        return self.values_dict[key]

    def setValue(self, key, val):
        self.values_dict[key] = val

    # Methods from above
    calculateWaveform = calculateWaveform
    calculateTotalSeqTime = calculateTotalSeqTime
    generatePulse = generatePulse
    updateHeadTime = updateHeadTime


class legacy_self(test_self):
    def __init__(self, *args, **kwargs):
        test_self.__init__(self, *args, **kwargs)
    generatePulse = generatePulse_legacy
    calculateWaveform = calculateWaveform_legacy


def test():
    print("\nRunning TESTS!\n")
    
    print("\nTEST: Creating test and legacy objects\n")
    test = test_self()
    legacy = legacy_self()

    from timeit import timeit
    print("\nTEST: Calculating Waveforms on test\n")
    test_time = timeit(test.calculateWaveform, number=1)
    print("\nTEST: Calculating Waveforms on legacy\n")
    legacy_time = timeit(legacy.calculateWaveform, number=1)

    failed = (test.lWaveforms-legacy.lWaveforms).any() and (test.lQuadratures-legacy.lQuadratures).any()

    
    print("\nTest results:")
    print("  test object time:     {:11.6f} s".format(test_time))
    print("  legacy object time:   {:11.6f} s".format(legacy_time))
    print("  Speed increase:       {:11.6f} x".format(legacy_time/test_time - 1))
    print("  Identical results:        ", not failed)

    errs_max = [(abs(test.lWaveforms-legacy.lWaveforms)).max(),(abs(test.lQuadratures-legacy.lQuadratures)).max()]
    if failed:
        print("  Signal Max Abs difference:          {:11.6g}".format(errs_max[0]))
        print("  Quadra Max Abs diffirence:          {:11.6g}".format(errs_max[1]))
    
    return test, legacy


def run_from_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False


if __name__ == "__main__":
    if not run_from_ipython():
        test()
