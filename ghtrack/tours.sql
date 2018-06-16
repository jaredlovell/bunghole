CREATE TABLE tours
(
	id			varchar		NOT NULL,
	vehicles_name		varchar,
	status			varchar,
   	missing_vehicle_data	varchar, 
   	license_plate		varchar, 	 
   	planned_begin		timestamp,
   	planned_end		timestamp,
	completion_time		timestamp,
   	haulier			varchar,
   	transport_company	varchar, 
   	customer		varchar, 
	vehicle_owner_code 	varchar,	
	PRIMARY KEY (id)
);

CREATE TABLE stops
(
	id			varchar	NOT NULL,
	tours_id		varchar NOT NULL,
	type			varchar,
	status			varchar,
   	time_window_begin	timestamp,
   	time_window_end		timestamp,
   	rta			timestamp,
   	location_id		varchar		NOT NULL, 
   	company			varchar, 
   	country			varchar, 
   	city			varchar, 
   	zipcode			varchar, 
   	street			varchar, 
   	score			int, 
   	latitude		float, 
   	longitude		float, 
	PRIMARY KEY (id, tours_id)
);

CREATE TABLE vehicles
(
	name 	varchar,	
   	timestamp	timestamp,
	license_plate 	varchar,	
	data_gate_open 	varchar,	
   	latitude	float, 
   	longitude	float, 
	speed 	float,	
	PRIMARY KEY (name, timestamp)
);

--CREATE TABLE tours_vehicles
--(
--	tours_id 	varchar NOT NULL,
--	vehicles_name 	varchar NOT NULL,
--	PRIMARY KEY (tours_id, vehicles_name)
--);
