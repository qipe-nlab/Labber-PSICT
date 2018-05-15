## Sample script for top-down development of the Unified Interface Framework (UIF) of the Pulse Sequence Instrument Tool (PSICT)
##      This script is intended as a "sample" of the future structure
##      of the UIF in terms of user interface and scripting.
##      Should be compared to other "external" scripts such as
##      parser_example.py and CW_SSB_mixer....py
## Author: Sam Wolski

## module imports - all deps in the PSICT will be imported anyway
import os
import Labber
from Labber import ScriptTools

## set path to Labber executables
ScriptTools.setExePath(os.path.normpath("C:/Program Files (x86)/Labber/Program"))

## specify reference file paths
template_path = os.path.normpath("C:/Users/qcpi/...")  # path to template hdf5 config file
template_file = "template_01"        # file name of template hdf5 config file
output_path = os.path.normpath("C:/Users/qcpi/Labber/Data/...")  # path to desired output hdf5 data file
output_file = "uif_out_001"          # file name of output hdf5 data file

## Set parameters which will be fixes at point values
##      Not all point values have to be specified; if a specification is
##      not present, it will simply be taken from the template file.
####
## NB: The pulse definitions in this section are quite important as they
##     define the pulse types; this will determine a whole bunch of pre-
##     calculations such as pulse inversion etc.
input_point_values = \
    {
        "Single-Qubit Pulse Generator": \
        ## SQPG spec is a dict for each pulse number
        ##      (pulse 0 for main parameters)
            {
                ## a good text editor will let you collapse the spec dicts
                0: \
                    {\
                        ## parameters can be formatted as a long dict;
                        ##    a good text editor will let you collapse it!
                        "sr": 1e9,
                        "dead": 1000,  # comment for units
                        "delay": 100,  # ns
                        "trim": 0,     # on-off
                        ...
                    },
                1: \
                    {
                        ## spec can also be formatted in one line:
                        "a": 100e-3, "w": 200, "v": 100,
                        ...
                        "pulse_type": "qubit", # specifies whether or not pulse should be inverted etc.
                    },
                2: \
                    {
                        "a": 150e-3,
                        ...
                        "pulse_type": "resonance",
                    }
                ...
                "readout": \
                ## can handle readout pulse completely separately! (with different parameters as well)
                    {
                        "readout_spec_1": 100,
                        ...
                    }
            },
        "Manual": \
        ## Manual spec can potentially use custom names from the beginning; these can be implictly converted self-consistently.
            {
                "Re": 100e-3,
                "Im": 200e-3,
                ...
            },
        "AWG thingy thing": \
        ## other instrument specifications occur directly
                {
                    "p1": 100, "p2": 26, ...
                }
    }
##

## Set parameters which are to be iterated
#### potentially the same as for point values, but then makes
##   specifying the order in which variables are to be iterated more complex
input_iteration_values = \
    {
        "Single-Qubit Pulse Generator": \
            {
                0: {
                    # [channel name, start, stop, n_pts]
                    ["dead", 0, 400, 20],
                    ...
                },
                1: {
                    ["a", 0, 150e-3, 15],
                    ...
                }
            },
        "Manual": \
            {
                ["Re", ]
            }
    }
#### ALTERNATIVELY
##      Add the instrument (and optional pulse) spec to each individual entry
##      This will make the order of iteration far more intuitive,
##      which may be more effective.
input_iteration_values = \
    {
        # [channel, start, stop, n_pts, instrument, pulse (optional)]
        ["a", 0, 150e-3, 15, "SQPG", 3], # Amplitude #3
        ["dead", 0, 400, 20, "SQPG", 0], # Dead time
        ["Im", -750e-3, 750e-3, "Manual"], # Im quadrature component
        ...
        ## Iteration will be carried out from top to bottom
        ##      ie the same way as in the Step viewer of the Labber interface
    }

## Add channel specifications
input_relation_channels = \
    {
        ## [short name/label, [instrument, instrument channel name, pulse (optional)]]
        ['a1', ["SQPG", 'a', 1]],
        ['dead', ["SQPG", 'dead', 0]],
        ['Re', ["Manual", 'Re']],
        ['AWG_sfreq', ["AWG", 'Signal frequency']],
        ...
    }

## Set channel relations
##      Can potentially be done per-instrument, but can also be done in bulk
input_channel_relations = \
    {
        "Single-Qubit Pulse Generator": \
            {
                0: \
                    {
                        ## [[instrument name, channel name, pulse (optional)],
                        ##      relation_string, [symbol_1, symbol_2, ...]]
                        [["SQPG", 'a', 2], "a1 + a3", ['a1', 'a3']],
                        ...
                    }
            }
    }




## run script file (can be converted to a module at some point)
exec(open("psict_uif_v0_1.py").read())

## initialise PSICT instance
##      Will initialise Labber MO (which can later be accessed),
##      as well as all file paths, at some point?
psictMgr = psictUIFManager(copy_script = True)
psictMgr.init_MeasurementObject(template_path, template_file, output_path, output_file)
psictMgr.set_rcfile("uif_rc_sample.py")   # set resource file (dicts, post-processing, etc)

## Input all parameter specifications
psictMgr.set_point_values(input_point_values)
psictMgr.set_iteration_values(input_iteration_values)
psictMgr.set_relation_channels(input_relation_channels)
psictMgr.set_channel_relations(input_channel_relations)

## access Labber MeasurementObject directly if needed
psictMgr.MeasurementObject.do_something(foo, bar)

## Run measurement, get output
psictMgr.performMeasurement(save_data = True)
data = psictMgr.output_data

## "Cleaning up" will be taken care of by the psictMgr destructor
##

## Can do data analysis and stuff here...
