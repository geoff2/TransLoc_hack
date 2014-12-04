#!/usr/bin/python3

#############
# Populate tables v1
#
# Populates 4 Postgresql 9.x tables with non-real-time data relating to transit providers
# - Agency data, including agency number, name, and abbreviation
# - Route segments, including segment_id and encoded polyline geometry
# - Route data, including route name (long and short), color, and list of segments
# - Stop data, including agencies served, routes served, name, locaiton, and GoTriangle
#   stop id #
#
# Uses psycopg2 database adapater
# Written for Python 3.4.0
#

# To access TransLoc API, need to get a Mashape API key at http://mashape.com
key = {'X-Mashape-Key': '#######'}


import requests, json, time, pprint, psycopg2, psycopg2.extras, logging
from dateutil.parser import *
from dateutil.tz import *

#### Agencies to examine
# 8: Chapel Hill Transit (CHT)
# 12: Triangle Transit (TTA)
# 16: NCSU Wolfline
# 20: Capital Area Transit (CAT)
# 24: Durham Area Transit Authority (DATA)
# 176: Duke University Transit

agencies = ['8','12','16', '20','24','176']

agenciesURL = "https://transloc-api-1-2.p.mashape.com/agencies.json"
routesURL = "https://transloc-api-1-2.p.mashape.com/routes.json"
stopsURL = "https://transloc-api-1-2.p.mashape.com/stops.json"
segmentsURL = "https://transloc-api-1-2.p.mashape.com/segments.json"

getAgencies = True
getRoutes = True
getStops = True
getSegments = True

agencyParam = {'agencies':','.join(agencies)}
callbackParam = {'callback':'call'}

parameters = {}

# for d in (agencyParam, geoParam, callbackParam):
for d in (agencyParam, callbackParam):
	parameters.update(d)

# Connect to database
# Insert your dbname and dbuser here ->

conn = psycopg2.connect("dbname=##### user=######")
cur = conn.cursor()

# Logging
logging.basicConfig(filename='populatelog.log',format='%(levelname)s:%(asctime)s:%(message)s',level=logging.WARNING)


# 1. Populate agency database

if getAgencies == True:
	r = requests.get(agenciesURL,params=parameters,headers=key)
#	print(r.url)
	result = r.json()
#	print(r.text)
	generated_on = result['generated_on']
	for entry in result['data']: # result is a list of dictionaries for each agency
		agency_id = entry['agency_id']
		long_name = entry['long_name']
		short_name = entry['short_name']
		agency_lat = entry['position']['lat']
		agency_long = entry['position']['lng']
		# print(str(generated_on) + ' -- ' + long_name + ' -- ' + short_name + ' -- ' + str(agency_lat) + ' -- ' + str(agency_long))
		
		SQL = 'INSERT INTO agencies (generated_on, agency_id, long_name, short_name, agency_lat, agency_long) VALUES (%s, %s, %s, %s, %s, %s)'
		data = (generated_on, agency_id, long_name, short_name, agency_lat, agency_long)
		
		cur.execute(SQL, data)
		
	conn.commit()
	
	
# 2. Populate routes database

if getRoutes == True:
	r = requests.get(routesURL,params=parameters,headers=key)
#	print(r.url)
	result = r.json()
#	print(r.text)
	generated_on = result['generated_on']
	segments = []
	segments_for_SQL = {}
	t = 0
	psycopg2.extras.register_composite('segments', cur.connection)
	for agency in agencies:
		for entry in result['data'][agency]:
			route_id = entry['route_id']
			short_name = entry['short_name']
			long_name = entry['long_name']
			route_color = entry['color']
			segments.clear()
			for list in entry['segments']:
				segments.append([list[0],list[1]])
			
#			print(str(generated_on) + ' -- ' + str(route_id) + ' -- ' + str(short_name) + ' -- ' + str(long_name) + ' -- ' + str(route_color) + ' -- ' + str(segments_for_SQL[t]) + "\n\n\n\n\n")
		
			SQL = 'INSERT INTO routes (generated_on, route_id, short_name, long_name, color, segments) VALUES (%s, %s, %s, %s, %s, %s)'
			data = (generated_on, route_id, short_name, long_name, route_color, segments)
		
			cur.execute(SQL, data)
		
	conn.commit()						


# 3. Populate stops database

if getStops == True:
	routes_served = []
	stop_agencies = []
	r = requests.get(stopsURL,params=parameters,headers=key)
#	print(r.url)
	result = r.json()
#	print(r.text)
	generated_on = result['generated_on']
	for entry in result['data']: # result is a list of stops
		stop_id = entry['stop_id']
		stop_code = entry['code']
		stop_name = entry['name']
		stop_lat = entry['location']['lat']
		stop_long = entry['location']['lng']
		stop_agencies.clear()
		for id in entry['agency_ids']:
			stop_agencies.append(int(id))
		stop_agencies = entry['agency_ids']
		routes_served.clear()
		for rt in entry['routes']:
			routes_served.append(int(rt))
		routes_served = entry['routes']
		

		# print(str(generated_on) + ' -- ' + long_name + ' -- ' + short_name + ' -- ' + str(agency_lat) + ' -- ' + str(agency_long))
		
		SQL = 'INSERT INTO stops (generated_on, stop_id, stop_code, stop_name, stop_lat, stop_long, agencies, routes_served) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
		data = (generated_on, stop_id, stop_code, stop_name, stop_lat, stop_long, stop_agencies, routes_served)
		
		cur.execute(SQL, data)
		
	conn.commit()

# 4. Populate segments database

if getSegments == True:
	r = requests.get(segmentsURL,params=parameters,headers=key)
#	print(r.url)
	result = r.json()
#	print(r.text)
	generated_on = result['generated_on']
	for segment_id,encoded_polyline in result['data'].items():
		SQL = 'INSERT INTO segments (generated_on, segment_id, encoded_polyline) VALUES (%s, %s, %s)'
		data = (generated_on, segment_id, encoded_polyline)		
		cur.execute(SQL, data)
		
	conn.commit()
