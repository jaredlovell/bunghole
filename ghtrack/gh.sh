#!/bin/sh

APIKEY=`cat ./apikey.ghtrack`
#curl -i -s -H "Accept:application/xml" -H "X-Api-Key:${APIKEY}" -X GET "$1"
curl -i -s -H "Accept:application/json" -H "X-Api-Key:${APIKEY}" -X GET "$1"
