## A "clean" copy of uif_script_sample.py, showing maximal visual compression
##      of specifications etc. with all comments removed
## Author: Sam Wolski

## module imports - all deps in the PSICT will be imported anyway
import os
import Labber
from Labber import ScriptTools

ScriptTools.setExePath(os.path.normpath("C:/Program Files (x86)/Labber/Program"))

template_path = os.path.normpath("C:/Users/qcpi/...")  # path to template hdf5 config file
template_file = "template_01"        # file name of template hdf5 config file
output_path = os.path.normpath("C:/Users/qcpi/Labber/Data/...")  # path to desired output hdf5 data file
output_file = "uif_out_001"          # file name of output hdf5 data file

input_point_values = \
    { "Single-Qubit Pulse Generator": \
            {   0: \
                    {"sr": 1e9, "dead": 1000, "delay": 100, "trim": 0, ...
                    },
                1: \
                    {"a": 100e-3, "w": 200, "v": 100, ...,
                    "pulse_type": "qubit"
                    },
                2: \
                    {"a": 150e-3, ...,
                    "pulse_type": "resonance"
                    }
                ...
                "readout": \
                    {
                        "readout_spec_1": 100, ...
                    }
            },
        "Manual": \
            {
                "Re": 100e-3, "Im": 200e-3, ...
            },
        "AWG thingy thing": \
            {
                "p1": 100, "p2": 26, ...
            }
    }

input_iteration_values = \
    {
        # [channel, start, stop, n_pts, instrument, pulse (optional)]
        ["a", 0, 150e-3, 15, "SQPG", 3], # Amplitude #3
        ["dead", 0, 400, 20, "SQPG", 0], # Dead time
        ["Im", -750e-3, 750e-3, "Manual"], # Im quadrature component
        ...
    }

input_relation_channels = \
    {
        ## [short name/label, [instrument, instrument channel name, pulse (optional)]]
        ['a1', ["SQPG", 'a', 1]],
        ['dead', ["SQPG", 'dead', 0]],
        ['Re', ["Manual", 'Re']],
        ['AWG_sfreq', ["AWG", 'Signal frequency']],
        ...
    }

input_channel_relations = \
    {
        "Single-Qubit Pulse Generator": \
            {   0: \
                    {
                        ## [[instrument name, channel name, pulse (optional)],
                        ##      relation_string, [symbol_1, symbol_2, ...]]
                        [["SQPG", 'a', 2], "a1 + a3", ['a1', 'a3']],
                        ...
                    }
            }
    }


exec(open("psict_uif_v0_1.py").read())
psictMgr = psictUIFManager(copy_script = True)
psictMgr.init_MeasurementObject(template_path, template_file, output_path, output_file)
psictMgr.set_rcfile("uif_rc_sample.py")   # set resource file (dicts, post-processing, etc
psictMgr.set_point_values(input_point_values)
psictMgr.set_iteration_values(input_iteration_values)
psictMgr.set_relation_channels(input_relation_channels)
psictMgr.set_channel_relations(input_channel_relations)

## access Labber MeasurementObject directly if needed
psictMgr.MeasurementObject.do_something(foo, bar)

## Run measurement, get output
psictMgr.performMeasurement(save_data = True)
data = psictMgr.output_data

## Can do data analysis and stuff here...
