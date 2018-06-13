CREATE TABLE tours
(
	id			varchar		NOT NULL,
	status			varchar,
   	missing_vehicle_data	varchar, 
   	license_plate		varchar, 	 
   	planned_begin		timestamp,
   	planned_end		timestamp,
   	haulier			varchar,
   	transport_company	varchar, 
   	customer		varchar, 
	vehicle_owner_code 	varchar,	
	PRIMARY KEY (id)
);

CREATE TABLE stops
(
	id		varchar	NOT NULL,
	type		varchar,
   	time_window_begin		timestamp,
   	time_window_end			timestamp,
   	rta				timestamp,
	tours_id		varchar,
	PRIMARY KEY (id)
);

CREATE TABLE address
(
   	location_id	varchar		NOT NULL, 
   	company	varchar, 
   	country	varchar, 
   	city	varchar, 
   	zipcode	varchar, 
   	street	varchar, 
   	score	int, 
   	latitude	float, 
   	longitude	float, 
	PRIMARY KEY (location_id)
);

#CREATE TABLE stops_address
#(
#	gid		bigserial,
#	stops_id	varchar		NOT NULL,	
#	address_location_id	varchar,	
#	PRIMARY KEY (gid)
#);

CREATE TABLE stops_address
(
	stops_id	varchar		NOT NULL,	
	address_location_id	varchar,	
	PRIMARY KEY (stops_id, address_location_id)
);


CREATE TABLE vehicle
(
	uuid 	varchar,	
	data_gate_open 	varchar,	
   	latitude	float, 
   	longitude	float, 
   	timestamp	timestamp,
	license_plate 	varchar,	
	name 	varchar,	
	PRIMARY KEY (uuid)
);



#### vehicles.xml tables


CREATE TABLE coupling

CREATE TABLE ignition

CREATE TABLE motion

CREATE TABLE status

CREATE TABLE vehicle_base
 





