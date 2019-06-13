## 1.2rc1 [ongoing] (2019/06/13)

Features:

* Added MIT license under `LICENSE.md`

Bugfixes:

* Modify MultiPulse pulse generation algorithm to remove rounding errors for generating sequences with timing parameters
  with values below the sample rate.

## 1.2rc0 (2019/04/05)

Features:

* Add DRAG as a per-pulse option in the PSICT MultiPulse driver.
* Include sample worker-script in `sample` folder.
* Add compatibility with per-pulse DRAG SQPG driver (cf https://github.com/SamWolski/Drivers).
* Elements of channel relation strings are now parsed from the string itself, and do not need to be supplied separately. [#4]
* Add WorkerScriptManager as a higher-level automation module for the PSICT_UIF.
* Implement logging framework for PSICT_UIF and WorkerScriptManager. [#3]
* Add this file (changelog).

Bugfixes:

* Updated hdf5 dataset reference method due to upcoming deprecation. [#9]


## 1.1.1 (2019/02/10)

Features:

* Add PSICT MultiPulse driver to generate long sequences of repeated pulses.
* Add functionality to set parameters through InstrumentClient interface (cf http://labber.org/online-doc/api/InstrumentClient.html#sec-instrumentclient-class).

Bugfixes:

* Fix PSICT not functioning if not using SQPG (eg if using MultiPulse instead).
* Set default server to 'localhost'. Previously, there was no default set, and so an error would be raised if the user did not explicitly set a default. [#2]


## 1.1.0 (2018/10/15)

Features:

* Clean up printing of messages for normal operation.
* Remove script-rcfile. Overall config is now provided by the `PSICT_config` file.

Bugfixes:

* Move script copying to before measurement actually occurs, enabling editing of script while measurement is running.


## Prior versions

Here be dragons... Please see the commit history. Good luck!
