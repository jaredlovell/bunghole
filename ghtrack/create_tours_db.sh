#!/bin/sh

cd `dirname $0`

die(){
	echo $1
	exit 1
}

psql -c "DROP DATABASE ght" -h localhost postgres || echo "no drop, maybe did not exist"
psql -c "CREATE DATABASE ght" -h localhost postgres || die "could not create database"
psql -f ./tours.sql -h localhost ght || die "could not create tables"
