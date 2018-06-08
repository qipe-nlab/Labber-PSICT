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

print(psictInterface.labberExporter)
sys.exit()

## Manually set Labber executable path
# psictInterface.set_labber_exe_path("foo/bar/baz/quux/", verbose = 1)

## Set template and output hdf5 files
template_dir = "~/Google-Drive/Tokyo_research/labber_scripts/2018/05/Data_0501"
template_file = "K2018-04-21_222"
psictInterface.set_template_file(template_dir, template_file, verbose = 1)
output_dir = "~/Google-Drive/Tokyo_research/labber_scripts/2018/05/Data_0501"
output_file = "K2018-04-21_226"
psictInterface.set_output_file(output_dir, output_file, verbose = 1)

#### Instrument settings
## Point values
point_values = {
        "SQPG":
            {
                "main": {       # parameters for overall pulse sequence - general SGPQ parameters
                        "control_freq": 7850, "Truncation range": 2,
                    },
                "inverted": {   # physical parameters that will be applied to all inverted pulses - the inverted pulse entries should not specify these, otherwise they will be overwritten
                        "a": 200, "w": 100,
                    },
                "AAA": \
                    {
                        "a": 2, "v": 1200,
                        "time_offset": 450, "time_reference": "previous", "relative_to": "second", "pulse_number": 2, "relative_marker": "start",
                        "is_inverted": True,
                    },
                "BBB": \
                    {
                        "a": 5, "w": 95,
                        "time_offset": 650, "time_reference": "relative", "relative_to": "CCC", "relative_marker": "end",
                    },
                "CCC": \
                    {
                        "a": 5,
                        "time_offset": 400, "time_reference": "absolute", "relative_to": "AAA", "pulse_number": 1,
                    },
            } # end SQPG

    } # end point values

## Set input pulse sequence
psictInterface.set_point_values(point_values, verbose = 0)

# Set up Labber MeasurementObject in case we would like to explicitly access it
psictInterface.init_MeasurementObject(verbose = 1)
## explicit access to MeasurementObject
print(psictInterface.MeasurementObject)

## Run measurement
psictInterface.perform_measurement(dry_run = True, verbose = 1)
