#!/bin/sh

GD=`which gdate`
if [ -z "$GD" ]; then
	GD="date"
fi

APIKEY=`cat ./apikey.ghtrack`
URL="https://amazon.ghtrack.com/api/v1/tour/status/workingset"

xdate=$($GD -u -Im  -d '15 minutes ago'| cut -c 1-16 | awk '{print $1":00"}')
now=$($GD -u -Im | cut -c 1-16 | awk '{print $1":00"}')
last_run=$($GD -u -Im -d '5 minutes ago'| cut -c 1-16 | awk '{print $1":00"}')

#curl -s -H "Accept:application/xml" -H "X-Api-Key:${APIKEY_VEHICLES}" -H "from_ts:${xdate}"
curl --compressed -s -H "Accept:application/json" -H "X-Api-Key:${APIKEY}" -H "max_samples:10000"  -H "from_ts:${xdate}" -X GET "$URL"
