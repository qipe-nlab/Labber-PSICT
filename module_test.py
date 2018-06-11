## Testing the functionality of PSICT-UIF as a module

import sys

import PSICT_UIF

print("------------------------------------------------")
print("PSICT_UIF appears to have imported successfully.")
print("PSICT_UIF version is", PSICT_UIF.__version__)

## Initialise PSICT-UIF interface object
psictInterface = PSICT_UIF.psictUIFInterface(verbose = 1)
## Set script rcfile
psictInterface.load_script_rcfile("uif_script_rc_sample.py", verbose = 1)
# psictInterface.set_cwd(os.path.abspath(__file__))


## Manually set Labber executable path
# psictInterface.set_labber_exe_path("foo/bar/baz/quux/", verbose = 1)

## Set template and output hdf5 files
template_dir = "~/Google-Drive/Tokyo_research/labber_scripts/2018/06/Data_0604"
template_file = "K2018-06-04_001"
psictInterface.set_template_file(template_dir, template_file, verbose = 1)
output_dir = "~/Google-Drive/Tokyo_research/labber_scripts/2018/05/Data_0501"
output_file = "K2018-06-04_001"
psictInterface.set_output_file(output_dir, output_file, verbose = 1)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#### Instrument settings
## Point values
point_values = {
        "SQPG":
            {
                "main": {       # parameters for overall pulse sequence - general SGPQ parameters
                        "Truncation range": 5, "Sample rate": 1e9,
                    },
                "inverted": {   # physical parameters that will be applied to all inverted pulses - the inverted pulse entries should not specify these, otherwise they will be overwritten
                        "a": 200, "w": 100e-9,
                    },
                "AAA": \
                    {
                        "a": 2, "v": 200e-9,
                        "time_offset": 450e-9, "time_reference": "previous", "relative_to": "second", "pulse_number": 2, "relative_marker": "start",
                        "is_inverted": True,
                    },
                "BBB": \
                    {
                        "a": 5, "w": 95e-9,
                        "time_offset": 650e-9, "time_reference": "relative", "relative_to": "CCC", "relative_marker": "end",
                    },
                "CCC": \
                    {
                        "a": 5,
                        "time_offset": 400e-9, "time_reference": "absolute", "relative_to": "AAA", "pulse_number": 1,
                    },
                "dead": \
                    {
                        "a": 0, "w": 0, "v": 1e-6,
                        "time_offset": 200e-9, "time_reference": "previous",
                        "pulse_number": 99,
                    },
            }, # end SQPG
        "Signal demodulation":
            {
                "Skip start": 145e-9,
            },
    } # end point values

## Iteration values
# iteration_values = [
#         ["Digitizer", "Number of samples", [1e3, 1.5e3, 6]],
#         ["SQPG", ("BBB", "Amplitude"), [0, 1e3, 3]],
#     ]
iteration_values = {
        "SQPG":
            {
                "CCC": {
                        "w": [500e-9, 1500e-9, 3],
                       }
            },
        "Digitizer":
            {
                "Number of samples": [100, 200, 3],
            },
        "Manual":
            {
                "Value 1": [2, 3, 2],
            },
    } # end iteration values

iteration_order = [
        ("Manual", "Value 1"),
        ("SQPG", ("CCC", "Width")),
        ("Digitizer", "Number of samples"),
    ] # end iteration order

## Channel relations - set available quantities (could be outsourced to rcfile?)
channel_defs = {
        "SQPG":
            {
                "main":
                    {
                        "delay": "First pulse delay",
                    },
                "CCC":
                    {
                        "a_CCC": "Amplitude",
                    },
            }, # end SQPG
        "Digitizer":
            {
                "Digitizer_n_avgs": "Number of averages",
            }, # end AWG_A
        "Manual":
            {
                'Re': "Value 1",
                'Im': "Value 2",
            },
    } # end relation channels

## Channel relations - set relation strings
channel_relations = {
        "SQPG":
            {
                "CCC": {
                    'Amplitude': ["Re - Im", ['Re', 'Im']],
                },
            }, # end SQPG
        "Digitizer": {
            'Number of averages': ["Re + Im", ['Re', 'Im']],
        },
        "Manual": {
            'Value 2': ["Re * np.pi", ['Re']],
        },
    } # end channel relations

## End instrument parameter settings
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

## Set input pulse sequence
psictInterface.set_point_values(point_values, verbose = 0)
psictInterface.set_iteration_values(iteration_values, iteration_order, verbose = 0)
psictInterface.set_channel_relations(channel_defs, channel_relations, verbose = 0)

# Set up Labber MeasurementObject in case we would like to explicitly access it
psictInterface.init_MeasurementObject(verbose = 0)
## explicit access to MeasurementObject
print(psictInterface.MeasurementObject)

## Run measurement
psictInterface.perform_measurement(dry_run = True, verbose = 0)

# sys.exit()
