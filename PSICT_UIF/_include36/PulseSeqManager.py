## The PSICT-UIF pulse-sequence manager class
##  Stores input (specified by user) and output
##  (used to set Labber parameters) pulse sequences.

from PSICT_UIF._include36.PulseSequence import InputPulseSeq, OutputPulseSeq

class PulseSeqManager:
    '''
    A container for two pulse sequences (an InputPulseSeq and OutputPulseSeq) which provides methods for importing an input sequence from user input, converting an input sequence to an output sequence, and getting the output sequence ready for export to Labber.
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

    def set_input_pulse_seq(self, pulse_seq_dict, *, verbose = 0):
        '''
        Set the input pulse sequence from a dict of user specifications.

        This is passed directly to the InputPulseSeq.
        '''
        if verbose >= 1:
            print("Importing point value specifications for SQPG...")
        self.inputPulseSeq.set_pulse_seq(pulse_seq_dict, verbose = verbose)
        ## set flag
        self.is_input_seq_populated = True


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Conversion methods

    def convert_seq(self, *, verbose = 0):
        '''
        Convert the input sequence (specified by the user) into an output sequence (suitable for input into Labber).

        Note that the input sequence must have already been imported using the set_input_pulse_seq method.
        '''
        ## debug message
        if verbose >= 2:
            print("Converting input sequence to output sequence...")
        ## Assert input sequence is populated
        if not self.is_input_seq_populated:
            raise RuntimeError("Input sequence is not populated!")
        #### Pulse sequence conversion
        ## Transfer main parameters
        if verbose >= 3:
            print("Transferring main parameters...")
        self.outputPulseSeq.set_main_params(self.inputPulseSeq.export_main_params())
        ## Get list of pulses from inputPulseSeq (sorted by absolute_time)
        ##  and set the outputPulseSeq to this list
        sorted_pulses = self.inputPulseSeq.get_sorted_list(verbose = verbose)
        self.outputPulseSeq.set_pulse_seq(sorted_pulses, verbose = verbose)
        ####
        ## Set flag
        self.is_output_seq_populated = True
        ## debug message
        if verbose >= 2:
            print("Conversion to output sequence completed.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Output sequence export

    def export(self, *, verbose = 0):
        '''
        Export the output pulse sequence, in a form that can be parsed by the LabberExporter and applied to the Labber API.
        '''
        ## debug message
        if verbose >= 2:
            print("Exporting output pulse sequence...")
        return self.outputPulseSeq.export(verbose = verbose)
