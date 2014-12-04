/* Code written for PostgreSQL 9.3
   SQL code to create table to store TransLoc data
   that is generally static and only changes periodically
   (e.g. with service changes) */

DROP TABLE routes;
DROP TABLE segments;
DROP TABLE stops;
DROP TABLE agencies;

DROP TYPE route_segments;

/* Route segments type not currently used */

CREATE TYPE route_segments AS (
	segment_id			INTEGER,
	direction			TEXT
); 

CREATE TABLE routes (
	key						SERIAL PRIMARY KEY,
    generated_on			TIMESTAMP WITH TIME ZONE,
	route_id				INTEGER,
	short_name				TEXT,
	long_name				TEXT,
	color					TEXT,
	segments				TEXT[]
);

CREATE TABLE segments (
	key						SERIAL PRIMARY KEY,
    generated_on			TIMESTAMP WITH TIME ZONE,
	segment_id				INTEGER,
	encoded_polyline		TEXT
);



CREATE TABLE stops (
	key						SERIAL PRIMARY KEY,
    generated_on			TIMESTAMP WITH TIME ZONE,
	stop_id					INTEGER,
	stop_code				SMALLINT,
	stop_name				TEXT,
	agencies				TEXT[],
	stop_lat				FLOAT,
	stop_long				FLOAT,
	routes_served			TEXT[]
);
	
CREATE TABLE agencies (
	key						SERIAL PRIMARY KEY,
    generated_on			TIMESTAMP WITH TIME ZONE,
	agency_id				INTEGER,
	long_name				TEXT,
	short_name				TEXT,
	agency_lat				FLOAT,
	agency_long				FLOAT
);
