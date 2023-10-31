# Installation

## Firmware

* There is currently a bug with firmware upgrade. The provisioning port is stripped from the
  provisioning server URL by the firmware. If you want to upgrade the firmware, please go to the
  web interface of the base station and input the port number after the IP address or hostname used
  for provisioning and press on `Save/start upgrade`.
* After upgrading to version 450BXX or higher the rollback to version 410BXX or previous is not
  possible.
* After uprading to version 500BXX or higher you need to update also any M5 Repeater you would like
  to use at least to 480B5.
* A direct update of the base station from V450BXX to V510B1 or higher is not possible, an
  intermediate update to V500B1 or V501B1 is required first.

## Handset authentication code

In order for the handsets to associate with the DECT base station, it is necessary to enter a PIN in
the register menu on the handset. The authentication code for a device in autoprov mode is `0000`.
For all subsequent handsets, the code is the last four digits of the line position (e.g. if you
have the line at position 1, the code will be `0001`).
