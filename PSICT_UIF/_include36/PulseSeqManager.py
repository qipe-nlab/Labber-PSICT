## The PSICT-UIF pulse-sequence manager class
##  Stores input (specified by user) and output
##  (used to set Labber parameters) pulse sequences.

from PSICT_UIF._include36.PulseSequence import InputPulseSeq, OutputPulseSeq

class PulseSeqManager:
    '''
    Docstring for PulseSeqManager.
    '''

    ## constructor
    def __init__(self, *, verbose = 0):
        ## set log level
        self.verbose = verbose
        ## init input and output pulse sequence containers
        self.inputPulseSeq = InputPulseSeq(verbose = self.verbose)
        self.outputPulseSeq = OutputPulseSeq(verbose = self.verbose)
        ## flags
        self.is_input_seq_populated = False
        self.is_output_seq_populated = False
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeqManager constructor.")

    ## destructor
    def __del__(self):
        ## delete object attributes
        del self.inputPulseSeq
        del self.outputPulseSeq
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeqManager destructor.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Input pulse sequence

    def set_input_pulse_seq(self, pulse_seq_param_dict, *, verbose = 0):
        '''
        Set input parameters for the pulse sequence.

        These are the human-input parameters which will later be converted to a Labber-readable pulse sequence.

        Note that this method must receive *only* the SQPG pulse-sequence specifications!
        '''
        ## debug message
        if verbose >= 2:
            print("Setting input pulse sequence parameters...")
        ####
        ## Set parameters
        self.inputPulseSeq.set_seq_params(pulse_seq_param_dict, verbose = verbose)
        ## set flag
        self.is_input_seq_populated = True
        ## debug message
        if verbose >= 2:
            print("Input pulse sequence parameters set.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## conversion methods

    def convert_seq(self, *, verbose = 0):
        '''
        Convert the input sequence (specified by the user) into an output sequence (suitable for input into Labber).
        '''
        ## debug message
        if verbose >= 3:
            print("Converting input sequence to output sequence...")
        ## check if input sequence is populated
        if not self.is_input_seq_populated:
            raise RuntimeError("Input sequence is not populated!")
        #### do conversion
        ## Get list of pulses from inputPulseSeq (sorted by absolute_time)
        ##  and set the outputPulseSeq to this list
        sorted_pulses = self.inputPulseSeq.get_sorted_list()
        self.outputPulseSeq.set_pulse_seq(sorted_pulses)
        ####
        ## set flag
        self.is_output_seq_populated = True
        ## debug message
        if verbose >= 3:
            print("Conversion to output sequence completed.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
