## Playing around with the Pulse and PulseSeq classes for development

import sys

from PSICT_UIF._include36.Pulse import Pulse
from PSICT_UIF._include36.PulseSequence import PulseSeq, InputPulseSeq
from PSICT_UIF._include36.PulseSeqManager import PulseSeqManager

my_pulse_seq = \
        {
            "first": \
                {
                    "a": 2, "w": 3, "absolute_time": 400,
                },
            "second": \
                {
                    "a": 5, "w": 1, "absolute_time": 200,
                },
            "third": \
                {
                    "a": 5, "w": 1, "absolute_time": 300,
                },
        }

print("***************")

psm = PulseSeqManager(verbose = 1)
psm.set_input_pulse_seq(my_pulse_seq, verbose = 4)

print(psm.inputPulseSeq.pulse_list)

## convert sequence
psm.convert_seq(verbose = 4)

print(psm.outputPulseSeq.pulse_list)
print([pulse["pulse_number"] for pulse in psm.outputPulseSeq])

sys.exit()
