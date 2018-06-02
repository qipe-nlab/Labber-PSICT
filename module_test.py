## Testing the functionality of PSICT-UIF as a module

import PSICT_UIF

print("------------------------------------------------")
print("PSICT_UIF appears to have imported successfully.")
print("PSICT_UIF version is", PSICT_UIF.__version__)

## Initialise PSICT-UIF interface object
psictInterface = PSICT_UIF.psictUIFInterface(verbose = 4)

## Manually set Labber executable path
psictInterface.set_labber_exe_path("foo/bar/baz/quux/", verbose = 1)

## Set template and output hdf5 files
template_dir = "~/Google-Drive/Tokyo_research/labber_scripts/2018/05/Data_0501"
template_file = "K2018-04-21_222"
psictInterface.set_template_file(template_dir, template_file, verbose = 4)
psictInterface.fileManager.copy_reference_file()
output_dir = "~/Google-Drive/Tokyo_research/labber_scripts/2018/05/Data_0501"
output_file = "K2018_test_001"
psictInterface.set_output_file(output_dir, output_file, verbose = 4)

## Set input pulse sequence
psictInterface.set_pulse_seq_params(verbose = 1)

## Run measurement
psictInterface.perform_measurement(verbose = 1)
