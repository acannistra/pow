# POW!
*In active development*.

This is a small hobby project to create an in-home display to communicate
whether a specified region of interest has received a considerable amount of snowfall (**POW**) within the recent time.

It's comprised of Raspberry Pi Zero hardware running a server on a local network. The server is responsible for periodically checking for snowfall reports, illumating the display accordingly via a Rpi-controlled relay, and allowing a user on the network to change the location being tracked.

## Setup

To setup the pi, after installation (TBD):

* Run `build-nwac-stations.bash` to get NWAC stations with snow depth data into JSON.
* run `python db/config.py <db-file-name> --file stations.json` to initialize sqlite database.
* run `python server/pow-daemon.py` to initialize config web server
