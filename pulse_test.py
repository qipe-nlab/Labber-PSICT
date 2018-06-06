## Playing around with the Pulse and PulseSeq classes for development

import sys

from PSICT_UIF._include36.Pulse import Pulse
from PSICT_UIF._include36.PulseSequence import PulseSeq, InputPulseSeq
from PSICT_UIF._include36.PulseSeqManager import PulseSeqManager

my_pulse_seq = \
        {
            "main": {
                    "control_freq": 7850,
                },
            "first": \
                {
                    "a": 2, "w": 3, "time_offset": 5, "time_reference": "relative", "relative_to": "second",
                },
            "second": \
                {
                    "a": 5, "w": 1, "time_offset": 200, "time_reference": "previous", "pulse_number": 2,
                },
            "third": \
                {
                    "a": 5, "w": 1, "time_offset": 10, "time_reference": "absolute", "pulse_number": 1,
                },
        }

print("***************")

psm = PulseSeqManager(verbose = 1)
psm.set_input_pulse_seq(my_pulse_seq, verbose = 4)

print(psm.inputPulseSeq.pulse_list)

print("==============")
psm.inputPulseSeq.pulse_pre_conversion(verbose = 4)
psm.inputPulseSeq.print_info(pulse_params = True)

## convert sequence
psm.convert_seq(verbose = 4)

print([pulse.valid_abs_time for pulse in psm.inputPulseSeq.pulse_list])

# ## verify that main parameters were transferred correctly
# print(psm.outputPulseSeq.main_params)
# ## verify that pulse sequence was transferred correctly
# print(psm.outputPulseSeq.pulse_list)
# print([pulse["pulse_number"] for pulse in psm.outputPulseSeq])

psm.outputPulseSeq.print_info(pulse_params = True)



sys.exit()
