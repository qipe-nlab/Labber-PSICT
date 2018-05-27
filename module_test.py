## Testing the functionality of PSICT-UIF as a module

import PSICT_UIF

print("PSICT_UIF appears to have imported successfully.")
print("PSICT_UIF version is", PSICT_UIF.__version__)

## Initialise PSICT-UIF interface object
psictInterface = PSICT_UIF.psictUIFInterface(verbose = 4)

## Set manual Labber executable path
psictInterface.set_labber_exe_path("foo/bar/baz/quux/", verbose = 4)

## Run measurement
psictInterface.perform_measurement(verbose = 4)
