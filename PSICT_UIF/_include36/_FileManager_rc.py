## Resource file for FileManager and related classes

## Default Labber executable paths (os-sensitive)
EXE_PATH_MAC = "/Applications/Labber/Measurement.app"
EXE_PATH_WIN = "C:/Program Files (x86)/Labber/Program"

## Dataset file defaults
FILE_DATABASE_EXT = "hdf5"  # file extension of Labber database files
SCRIPT_COPY_POSTFIX = "__copy"  # postfixed to filename of temporary reference file
SCRIPT_COPY_EXTENSION = "py"  # script file extension - should be .py

## Output filename incrementation defaults
INCREMENT_ASK_USER = True    # prompt user before incrementing the filename (overrules _FILEMGR_DEFAULTS_AUTO_INCREMENT)
INCREMENT_AUTO = False   # automatically increment the filename (overruled by _FILEMGR_DEFAULTS_USER_INCREMENT)
INCREMENT_MAX_ATTEMPTS = 1000   # emergency break out of incrementation loop
