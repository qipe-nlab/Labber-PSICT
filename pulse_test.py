## Playing around with the Pulse and PulseSeq classes for development

from PSICT_UIF._include36.Pulse import Pulse
from PSICT_UIF._include36.PulseSequence import PulseSeq

print("-----------")
new_pulse = Pulse("foo")
print(new_pulse)

pseq = PulseSeq()
# print(pseq)
# print(pseq.pulse_list)

pseq.add_pulse(new_pulse)
# print(pseq.pulse_list)

pseq.add_pulse("bar")
# pseq.add_pulse("foo")
pseq.add_pulse("quux")


print(pseq.pulse_list)
print(pseq.pulse_names)

print(pseq["foo"])
print(pseq[2])
