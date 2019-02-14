## The PSICT-UIF pulse-sequence manager class
##  Stores input (specified by user) and output
##  (used to set Labber parameters) pulse sequences.

import logging

from PSICT_UIF._include36.PulseSequence import InputPulseSeq, OutputPulseSeq
from PSICT_UIF._include36.ParameterSpec import IterationSpec
import PSICT_UIF._include36._LogLevels as LogLevels

class PulseSeqManager:
    '''
    A container for two pulse sequences (an InputPulseSeq and OutputPulseSeq) which provides methods for importing an input sequence from user input, converting an input sequence to an output sequence, and getting the output sequence ready for export to Labber.
    '''

    ## constructor
    def __init__(self, *, parent_logger_name = None):
        ## Logging
        if parent_logger_name is not None:
            logger_name = '.'.join([parent_logger_name, 'PulseSeqManager'])
        else:
            logger_name = 'PulseSeqManager'
        self.logger = logging.getLogger(logger_name)
        ## init input and output pulse sequence containers
        self.inputPulseSeq = InputPulseSeq(parent_logger_name = logger_name)
        self.outputPulseSeq = OutputPulseSeq(parent_logger_name = logger_name)
        ## flags
        self.is_input_seq_populated = False
        self.is_output_seq_populated = False
        ## debug message
        self.logger.log(LogLevels.TRACE, 'Instance initialized.')

    ## destructor
    def __del__(self):
        ## delete object attributes
        del self.inputPulseSeq
        del self.outputPulseSeq
        ## Status message
        self.logger.log(LogLevels.TRACE, 'Instance deleted.')

    def assign_script_rcmodule(self, rcmodule, rcpath):
        '''
        Assign the passed script rcmodule (already-imported rcfile) to the PulseSeqManager object, as well as its constituent PulseSeq objects.
        '''
        ## Assign to self
        self._script_rc = rcmodule
        self._script_rcpath = rcpath
        ## Assign to constituents
        self.inputPulseSeq.assign_script_rcmodule(rcmodule, rcpath)
        self.outputPulseSeq.assign_script_rcmodule(rcmodule, rcpath)
        ## Status message
        self.logger.debug('Script rcmodule and rcpath assigned.')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Input pulse sequence

    def set_input_pulse_seq(self, pulse_seq_dict):
        '''
        Set the input pulse sequence from a dict of user specifications.

        This is passed directly to the InputPulseSeq.
        '''
        self.logger.debug("Adding parameter specifications for SQPG...")
        self.inputPulseSeq.set_pulse_seq(pulse_seq_dict)
        ## set flag
        self.is_input_seq_populated = True

    def set_iteration_spec(self, iteration_spec_dict):
        '''
        Set iteration specifications, potentially overriding point values.
        '''
        self.logger.debug("Setting iteration specifications for SQPG...")
        for pulse_name, iter_params in iteration_spec_dict.items():
            for param_name, param_spec in iter_params.items():
                ## Convert to IterationSpec object
                iter_obj = IterationSpec({"start_value": param_spec[0],
                                          "stop_value": param_spec[1],
                                          "n_pts": param_spec[2],
                                        })
                ## Set parameter using IterationSpec object
                self.inputPulseSeq.set_pulse_parameter(pulse_name, param_name, iter_obj)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Channel relations methods

    def add_channel_defs(self, channel_defs_dict):
        '''
        Process SQPG channel definitions, and return a format-compliant dict.
        '''
        ## status message
        self.inputPulseSeq.add_channel_defs(channel_defs_dict)

    def add_channel_relations(self, channel_relations_dict):
        '''
        Process SQPG channel relations, and return a generic-format-compliant dict.
        '''
        self.inputPulseSeq.add_channel_relations(channel_relations_dict)

    def get_channel_defs(self):
        '''
        Get SQPG channel key definitions (for channel relations), in the format required by the LabberExporter.
        '''
        return self.outputPulseSeq.get_channel_defs()

    def get_channel_relations(self):
        '''
        Get SQPG channel relations in the format required by the LabberExporter.
        '''
        return self.outputPulseSeq.get_channel_relations()


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Conversion methods

    def convert_seq(self):
        '''
        Convert the input sequence (specified by the user) into an output sequence (suitable for input into Labber).

        Note that the input sequence must have already been imported using the set_input_pulse_seq method.
        '''
        ## debug message
        self.logger.debug("Converting input sequence to output sequence...")
        ## Assert input sequence is populated
        if not self.is_input_seq_populated:
            raise RuntimeError("Input sequence is not populated!")
        #### Pulse sequence conversion
        ## Transfer main parameters
        self.logger.debug("Transferring main parameters...")
        self.outputPulseSeq.set_main_params(self.inputPulseSeq.export_main_params())
        ## Get list of pulses from inputPulseSeq (sorted by absolute_time)
        ##  and set the outputPulseSeq to this list
        self.logger.debug("Sorting pulses...")
        sorted_pulses = self.inputPulseSeq.get_sorted_list()
        self.outputPulseSeq.set_pulse_seq(sorted_pulses)
        ## Transfer channel relations data
        self.logger.debug("Transferring channel relations data...")
        self.outputPulseSeq.add_channel_defs(self.inputPulseSeq.get_channel_defs())
        self.outputPulseSeq.add_channel_relations(self.inputPulseSeq.get_channel_relations())
        ####
        ## Set flag
        self.is_output_seq_populated = True
        ## debug message
        self.logger.debug("Conversion to output sequence completed.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Output sequence export

    def get_main_params(self):
        '''
        Get 'main' parameters of the stored pulse sequence (those associated with the SQPG instrument as a whole).
        '''
        return self.outputPulseSeq.main_params

    def export_output(self):
        '''
        Export the output pulse sequence, in a form that can be parsed by the LabberExporter and applied to the Labber API.
        '''
        ## debug message
        self.logger.debug("Exporting output pulse sequence...")
        return self.outputPulseSeq.export()

    def export_relations(self):
        '''
        Export the definitions and relations which define relations between the channels in a format ready to be received by a LabberExporter instance.
        '''
        ## status message
        self.logger.debug("Exporting pulse definitions and relations...")
        SQPG_defs = {"SQPG": self.outputPulseSeq.get_channel_defs()}
        SQPG_rels = {"SQPG": self.outputPulseSeq.get_channel_relations()}
        return SQPG_defs, SQPG_rels

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Misc

    def convert_iter_order_pulses(self, iter_order):
        '''
        IN PROGRESS; convert pulse names to numbers.
        '''
        ## status message
        self.logger.debug("Converting pulse names to numbers in iteration order...")
        new_iter_order = []
        return new_iter_order
