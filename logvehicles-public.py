#!/usr/bin/python3

#############
# Logvehicles v2
#
# Collects real-time data from selected transit providers and stores them in
# PostgreSQL database
#
# Data collected can be easily modified but includes:
#  - vehicle ID (TransLoc) and vehicle call name/number
#  - segment ID
#  - route ID
#  - Speed (in km/hr per TransLoc API docs)
#  - Location (Lat/Long)
#
# Uses psycopg2 database adapater
# Be sure to insert database connection credentials
#
# Written for Python 3.4.0

import requests, json, time, pprint, psycopg2, logging
from dateutil.parser import *
from dateutil.tz import *

############ CONFIGURATION
agencies = ['12'] # Triangle Transit
key = {'X-Mashape-Key': '#####'} # Insert Mashape key from http://mashape.com
cycle = 60 # Frequency of updates, in seconds
numberOfCycles = 3600 # Number of cycles
############

vehiclesURL = "https://transloc-api-1-2.p.mashape.com/vehicles.json"
agencyParam = {'agencies':agencies}
# geoParam used for debugging to simulate no service
geoParam = {'geo_area':'35.80176,-78.64347|35.80177,-78.64348'}
callbackParam = {'callback':'call'}

parameters = {}

# for d in (agencyParam, geoParam, callbackParam):
for d in (agencyParam, callbackParam):
	parameters.update(d)

# Connect to database

conn = psycopg2.connect("dbname=##### user=#####")
cur = conn.cursor()
i = 0

# Logging
logging.basicConfig(filename='vehicleslog.log',format='%(levelname)s:%(asctime)s:%(message)s',level=logging.WARNING)

while i < numberOfCycles:
	r = requests.get(vehiclesURL,params=parameters,headers=key)
	result = r.json()
#	print(r.text)
	generated_on = result['generated_on']
	for agency in agencies:
		try: 
			for entry in result['data'][agency]:
				last_updated_on = entry['last_updated_on']
				vehicle_id = entry['vehicle_id']
				call_name = entry['call_name']
				segment_id = entry['segment_id']
				route_id = entry['route_id']
				speed = entry['speed']
				LAT = entry['location']['lat']
				LONG = entry['location']['lng']
				try:
					next_arrival_time = entry['arrival_estimates'][0]['arrival_at']
					next_stop_id = entry['arrival_estimates'][0]['stop_id']
				except:
					next_arrival_time = '1990-01-01 00:01:00+00'
					next_stop_id = '99'
			
				SQL = 'INSERT INTO loclog (generated_on, last_updated_on, vehicle_id, call_name, segment_id, route_id, vehicle_speed, vehicle_lat, vehicle_long, next_arrival_time, next_stop_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
				data = (generated_on, last_updated_on, vehicle_id, call_name, segment_id, route_id, speed, LAT, LONG, next_arrival_time, next_stop_id)
		
				cur.execute(SQL, data)					
				# print(str(last_updated_on) + "--" + str(vehicle_id) + "--" + str(call_name) + "--" + str(segment_id) + "--" + str(route_id) + "--" + str(LAT) + "--" + str(LONG) + "--" + str(next_arrival_time) + "--" + str(next_stop_id) )
		except KeyError:
			logging.warning('No data, cycle %s',str(i+1))
		except:
			logging.error('Fatal error')
	i = i + 1
#	print('Cycle' + str(i))
	
	conn.commit()
	logging.warning('Data committed, cycle %s',str(i))

	time.sleep(cycle)
