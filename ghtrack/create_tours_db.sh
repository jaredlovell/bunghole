#!/bin/sh

cd `basename $0`

die(){
	echo $1
	exit 1
}

psql -c "DROP DATABASE ght" -h localhost -U pgsql postgres || echo "no drop, maybe did not exist"
psql -c "CREATE DATABASE ght" -h localhost -U pgsql postgres || die "could not create database"
psql -f ./tours.sql -h localhost -U pgsql ght || die "could not create tables"
