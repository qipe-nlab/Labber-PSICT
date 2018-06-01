## Testing the functionality of PSICT-UIF as a module

import PSICT_UIF

print("PSICT_UIF appears to have imported successfully.")
print("PSICT_UIF version is", PSICT_UIF.__version__)

## Initialise PSICT-UIF interface object
psictInterface = PSICT_UIF.psictUIFInterface(verbose = 1)

## Manually set Labber executable path
psictInterface.set_labber_exe_path("foo/bar/baz/quux/", verbose = 1)

## Set template and output hdf5 files
template_dir = "foo/foo/foo"
template_file = "template_01"
psictInterface.set_template_file(template_dir, template_file, verbose = 4)
output_dir = "bar/bar/bar"
output_file = "output_001"
psictInterface.set_output_file(output_dir, output_file, verbose = 4)

## Set input pulse sequence
psictInterface.set_pulse_seq_params(verbose = 1)

## Run measurement
psictInterface.perform_measurement(verbose = 1)
