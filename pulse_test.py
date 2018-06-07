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
            "AAA": \
                {
                    "a": 2, "w": 20, "v": 0,
                    "time_offset": 450, "time_reference": "previous", "relative_to": "second", "pulse_number": 2, "relative_marker": "start",
                },
            "BBB": \
                {
                    "a": 5, "w": 95, "v": 0,
                    "time_offset": 650, "time_reference": "relative", "relative_to": "CCC", "relative_marker": "end",
                },
            "CCC": \
                {
                    "a": 5, "w": 30, "v": 0,
                    "time_offset": 20, "time_reference": "absolute", "relative_to": "AAA", "pulse_number": 1,
                },
        }

print("********************************")

psm = PulseSeqManager(verbose = 1)
psm.set_input_pulse_seq(my_pulse_seq, verbose = 1)

print(psm.inputPulseSeq.pulse_list)

print("==============")
psm.inputPulseSeq.pulse_pre_conversion(verbose = 1)
# psm.inputPulseSeq.print_info(pulse_params = True)

## convert sequence
psm.convert_seq(verbose = 1)

# ## verify that main parameters were transferred correctly
# print(psm.outputPulseSeq.main_params)
# ## verify that pulse sequence was transferred correctly
# print(psm.outputPulseSeq.pulse_list)
# print([pulse["pulse_number"] for pulse in psm.outputPulseSeq])

psm.outputPulseSeq.print_info(pulse_params = True)



sys.exit()
