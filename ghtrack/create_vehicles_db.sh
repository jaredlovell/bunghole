#!/bin/sh

cd `basename $0`

die(){
	echo $1
	exit 1
}

psql -c "DROP DATABASE ghv" -h localhost -U pgsql kepler || echo "no drop, maybe did not exist"
psql -c "CREATE DATABASE ghv" -h localhost -U pgsql kepler || die "could not create database"
psql -f ./tours.sql -h localhost -U kepler ghv || die "could not create tables"
