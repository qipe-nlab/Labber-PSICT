## Playing around with the Pulse and PulseSeq classes for development

from PSICT_UIF._include36.Pulse import Pulse
from PSICT_UIF._include36.PulseSequence import PulseSeq, InputPulseSeq

print("-----------")
new_pulse = Pulse("foo")
print(new_pulse)

new_pulse.set_attributes({
            "name": "test1",
            "a": 14,
            "w": 26.5,
            "pulse_number": 3,
            "absolute_time": 400,
            "is_inverted": False,
            }, verbose = 4)

pseq = InputPulseSeq()
print(pseq)
print(pseq.pulse_list)

pseq.add_pulse(new_pulse)
print(pseq.pulse_list)

pseq.add_pulse("bar", {"absolute_time": 100}, verbose = 4)
pseq.add_pulse("xyzyy", {"absolute_time": 500}, verbose = 4)
pseq.add_pulse("quux", {"absolute_time": 50}, verbose = 4)

print(pseq.pulse_list)
print(pseq.pulse_names)

sorted_list = pseq.get_sorted_list(verbose = 4)
print(sorted_list)
