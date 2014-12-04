/* Code written for PostgreSQL 9.3
   SQL code to create table to store real-time vehicle information */

CREATE TABLE loclog (
    generated_on			TIMESTAMP WITH TIME ZONE,
	last_updated_on			TIMESTAMP WITH TIME ZONE,
	vehicle_id				INTEGER,
	call_name				TEXT,
	segment_id				INTEGER,
	route_id				INTEGER,
	vehicle_speed			FLOAT,
	vehicle_lat				FLOAT,
	vehicle_long			FLOAT,
	next_arrival_time		TIMESTAMP WITH TIME ZONE,
	next_stop_ID			INTEGER			
);
