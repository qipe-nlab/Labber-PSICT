## Resource file for FileManager and related classes

## Default Labber executable paths (os-sensitive)
_FILEMGR_LABBER_EXE_PATH_MAC_DEFAULT = "/Applications/Labber/Measurement.app"
_FILEMGR_LABBER_EXE_PATH_WIN_DEFAULT = "C:/Program Files (x86)/Labber/Program"

## Dataset file defaults
_FILEMGR_DEFAULTS_FILE_EXTENSION = "hdf5"  # file extension of Labber database files
_FILEMGR_DEFAULTS_COPY_POSTFIX = "__copy"  # postfixed to filename of temporary reference file

## Output filename incrementation defaults
_FILEMGR_DEFAULTS_USER_INCREMENT = True    # prompt user before incrementing the filename (overrules _FILEMGR_DEFAULTS_AUTO_INCREMENT)
_FILEMGR_DEFAULTS_AUTO_INCREMENT = False   # automatically increment the filename (overruled by _FILEMGR_DEFAULTS_USER_INCREMENT)
_FILEMGR_DEFAULTS_MAX_INCREMENTATION_ATTEMPTS = 1000   # emergency break out of incrementation loop
