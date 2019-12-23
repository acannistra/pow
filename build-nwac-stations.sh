#!/bin/bash

curl "https://api.snowobs.com/v1/station/timeseries?token=71ad26d7aaf410e39efe91bd414d32e1db5d&stid=$(echo {1..100} | tr ' ' ,)" | jq '.station_timeseries | .STATION | sort_by(.NAME)[] | select(.OBSERVATIONS.snow_depth) | {name: .NAME, lat: .LATITUDE, lon: .LONGITUDE, elevation: .ELEVATION, nwac_id: .STID, url: @uri "https://api.snowobs.com/v1/station/timeseries?token=71ad26d7aaf410e39efe91bd414d32e1db5d&stid=\(.STID)&source=nwac"}' | jq '.' -s  > stations.json
