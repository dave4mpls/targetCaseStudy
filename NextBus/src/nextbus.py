#!/usr/bin/env python3
#
#	NextBus.py
#	Response to Target Case Study
#	Candidate: Dave White, dave4mpls@gmail.com, 612-695-3289
#	Position: Guest Reliability Engineer
#	Date Completed: 7-31-2018
#
#	See design questions section below for design decisions that were made
#
#	Purpose: Contacts the Metro Transit XML web service as described at http://svc.metrotransit.org/
#	to retrieve the number of minutes until the next bus, or no return value if there is no further bus.
#
#	Interface: Command-Line
#
#	External dependencies:	requests
#		Install this dependency by using: pip install requests
#	Standard libraries:		time, sys
#
#	Example Command-Line: nextbus.py bus-route bus-stop-name direction
#	
#	bus-route:		should be a unique substring of the name of the bus route you want
#					If you put # followed by a number, it picks a particular Metro Transit route number
#					If you put #any, it lists all the routes in the resulting error message
#	bus-stop-name:	should be a unique substring of the name of the bus stop
#					If you put #any, it lists all the stops for that route in the resulting error message
#	direction:			must be east, north, south, or west (case-insensitive)
#					If you put #any, it lists all the directions for that route in the resulting error message
#
#	Return values are sent to Standard Output
#	Example return value (as requested in design) if bus-route and bus-stop-name are unique matches:
#		2 minutes
#	Return value (as requested by design) if no further buses are coming that day:
#		<no standard output>
#		(See design questions below-- a different output may be clearer if used interactively)
#	Return value if multiple bus-routes or bus-stop-names match: (returns first one that applies)
#		MULTIPLE MATCHES ON ROUTE: <comma-separated list of matching route names>
#		MULTIPLE MATCHES ON STOP: <comma-separated list of matching stop names>
#	Return values if no bus-routes or bus-stop-names match (returns first one that applies):
#		NO MATCH ON ROUTE
#		NO MATCH ON STOP
#	Return value if direction is not valid for route or is not a valid direction:
#		NO MATCH ON DIRECTION
#	Return value for any problem with accessing the network service:
#		NETWORK ERROR
#	Return value for parameter problems on the command line:
#		PARAMETER ERROR: (followed by the help text)
#	Return value if first parameter is /?, --help:
#		help text
#	Return value for any other problem:
#		UNKOWN ERROR
#
#	DESIGN QUESTIONS:
#	These are questions I would ask about the design if this was for production.  I didn't
#	ask them during the case study because you are all busy people, and probably
#	the interview is the best time to discuss design issues relating to the case study, so
#	that you can see that I follow up with the right questions after receiving a design.
#
# 	In a real work environment, I MIGHT ask these questions of the internal customer or
#	my supervisor, but might also infer them from other information I have, if I can
#	make a strong inference (e.g. if I already knew the script would be used interactively
#	only).  I would not assume the answer if I couldn't make a strong inference.
#
#	* Is this going to be used interactively or by a calling script, or both?  I assumed both,
#	   and created responses for edge cases that are both human and computer readable.
#	   (See return values above.)
#	* When there is no further bus that day, the designed result (no output) may confuse
#	   people if it is used interactively; should I return a standard error message like 
#	   NO FURTHER BUSES instead?
#	* When the bus route or bus stop name are not unique, the best interactive result 
#	   would be to list all of the results, but for a calling script, this would confuse the 
#	   calling script.  Should an additional API specification (e.g. JSON results?) be added
#	   for this case?  (The specs of course say that they will be unique, but in production,
#	   you can't guarantee that.)
#	* Users who know the bus system may provide a specific route number (e.g. 5F)
#	   instead of a bus route name; should this be accepted?
#	* Metro Transit returns times in the format "14 Min" if the data indicates the actual
#	   expected amount of wait time based on current bus location, and "10:08" if
#	   the time is just the scheduled time.  Should my app do the same, or indicate
#	   the difference between actual estimated arrival time and scheduled time in any way?

import requests
import time

#-- Global constants
metroTransitServiceUrl = "https://svc.metrotransit.org"

#-- Get a Metro Transit service result as a Python object, given a local path within the service
#-- starting with the slash after the domain name.  Throws an IOError on any error.
def getMetroTransitService(localPath):
	myURL = metroTransitServiceUrl + localPath
	try:
		result = requests.get(myURL, params = {'format': 'json'})
		if (result.ok):
			return result.json()		# on JSON error an exception will be thrown and caught
		else:
			raise IOError		# non-OK HTTP status is thrown as "IOError"
	except:
		raise IOError

def suppressMultipleSpaces(x):
	""" Returns the string X, but with multiple spaces (as found in Metro Transit return values) with single spaces. """
	while x.find("  ") >= 0:
		x = x.replace("  "," ")
	return x

def extractMatches(allItems, matchField, substring):
	"""
	Extracts a list of items that match a substring case-insensitively, within a larger list.
	The match is case-insensitive and matches a single space against any number of spaces,
	since multiple spaces may be found in Metro Transit results.  If the substring starts with "#",
	it finds only matches where the field STARTS with the rest of the substring followed by a space,
	useful for looking up route numbers.  If the entire substring is "#any", it returns the  whole list.
	
	Parameters
	-------------
	allItems : list
		The whole list of items to search.
	matchField : str
		The field within each record to match against the substring.
	substring : str
		The substring to search for.
		
	Returns
	--------
	list
		The records that matched the substring.
	"""
	if (substring.upper()=="#ANY"): return allItems  # special code #ANY returns whole  list
	startMatch = False
	if (substring[0:1] == "#"):
		startMatch = True
		substring = substring[1:]
	matchingItems = [ ]
	for thisItem in allItems:
		if startMatch:
			if suppressMultipleSpaces(thisItem[matchField].upper()).find(suppressMultipleSpaces(substring.upper()+" ")) == 0:
				matchingItems.append(thisItem)
		else:
			if suppressMultipleSpaces(thisItem[matchField].upper()).find(suppressMultipleSpaces(substring.upper())) != -1:
				matchingItems.append(thisItem)
	return matchingItems

def getRouteMatches(busRouteSubstring):
	""" given a substring, return matching routes as a list in Metro Transit format """
	return extractMatches(getMetroTransitService("/NexTrip/Routes"),"Description", busRouteSubstring)

def getDirectionMatches(busRouteNumber, busDirectionSubstring):
	""" given a route number and a direction substring, return matching directions as a list in Metro Transit format """
	return extractMatches(getMetroTransitService("/NexTrip/Directions/" + busRouteNumber), "Text", busDirectionSubstring)

def getStopMatches(busRouteNumber, busDirectionNumber, busStopSubstring):
	""" given a bus route number, direction number, and a substring of the stop name, return matching stops as a list in Metro Transit format """
	return extractMatches(getMetroTransitService("/NexTrip/Stops/" + busRouteNumber + "/" + busDirectionNumber), "Text", busStopSubstring)

def getTimepointDepartures(busRouteNumber, busDirectionNumber, busStopCode):
	""" given a bus route number, bus direction number, and bus stop code, return timepoint departures as a list in Metro Transit format """
	return getMetroTransitService("/NexTrip/" + busRouteNumber + "/" + busDirectionNumber + "/" + busStopCode)

def minutesTillBus(busTimepoint, nowTime = None):
	""" given a bus timepoint record from getTimepointDepartures, return the number of minutes until that bus, as a float.  nowTime is the current time since unix epoch, but leave it out to just use the system time. """
	t = busTimepoint["DepartureTime"]
	if nowTime is None: nowTime = time.time()
	secondsFromNow = float(t[6:-2].split('-')[0])/1000.0 - nowTime
	return secondsFromNow / 60.0

def formatTimepoint(busTimepoint, nowTime = None):
	""" given a single bus timepoint record from getTimepointDepartures, return the formatted output string; supply the current time if you want using nowTime, or leave it out to use the system time (nowTime is seconds since Unix epoch). """
	minutesFromNow = round(minutesTillBus(busTimepoint, nowTime))
	if (minutesFromNow==1):
		return "1 Minute"
	else:
		return "{:.0f} Minutes".format(minutesFromNow)

def getNextBusRecord(busTimepointList):
	""" given a list of bus timepoints from getTimepointDepartures, returns a list with one record (the next bus that hasn't arrived yet) or zero records (no bus is coming) """
	for thisTimepoint in busTimepointList:
		if minutesTillBus(thisTimepoint) > 0:
			return [ thisTimepoint ]
	return [ ]

def commaList(inputList, fieldToUse):
	""" Given an input list and a fieldname of which field to use, return a string that contains all those field items, separated by a comma and a space. """
	outstr = ""
	for thisItem in inputList:
		if outstr != "": outstr += ", "
		outstr += thisItem[fieldToUse]
	return outstr

def nextBus(busRouteSubstring, busStopSubstring, directionSubstring, returnDepartureText = False):
	"""
	Returns the response for the whole program, giving the formatted time for the next bus
	when provided with a bus route substring, a bus stop substring, and a direction substring.
	Handles all errors as described in the comment for the whole program.  All substring
	searches are case-insensitive.
	
	Parameters
	------------
	busRouteSubstring : str
		The substring to look for to find a unique route.
	busStopSubstring : str
		The substring to look for in the route's stop list, to find a unique stop.
	directionSubstring : str
		The substring to look for in the route's direction list, to find a unique direction.
	returnDepartureText : boolean
		(Optional, defaults to False): If true, return the Metro Transit departure text instead of 
		the # of minutes.  Used for testing.
	
	Returns
	--------
	str
		The output for the program, either "x minute(s)" if the bus is coming, a null string
		if no bus is coming, or an error message.  Errors include: 
		MULTIPLE MATCHES ON ROUTE: <comma-separated list of matching route names>
		MULTIPLE MATCHES ON STOP: <comma-separated list of matching stop names>
		NO MATCH ON ROUTE
		NO MATCH ON STOP
		NO MATCH ON DIRECTION
		NETWORK ERROR
		UNKOWN ERROR
	"""
	try:
		# Get the information from Metro Transit.  Return appropriate errors if
		# no matches are found or multiple matches are found.
		# routes
		noBusReturnValue = ""	# return value for when no busses are coming
		matchingRoutes = getRouteMatches(busRouteSubstring)
		if (len(matchingRoutes) == 0): return "NO MATCH ON ROUTE"
		if (len(matchingRoutes) > 1): return "MULTIPLE MATCHES ON ROUTE: " + commaList(matchingRoutes, "Description")
		thisBusNumber = matchingRoutes[0]["Route"]
		# directions
		matchingDirections = getDirectionMatches(thisBusNumber, directionSubstring)
		if (len(matchingDirections) == 0): return "NO MATCH ON DIRECTION"
		if (len(matchingDirections) > 1): return "MULTIPLE MATCHES ON DIRECTION: " + commaList(matchingDirections, "Text")
		thisDirectionNumber = matchingDirections[0]["Value"]
		# stops
		matchingStops = getStopMatches(thisBusNumber, thisDirectionNumber, busStopSubstring)
		if (len(matchingStops) == 0): return "NO MATCH ON STOP"
		if (len(matchingStops) > 1): return "MULTIPLE MATCHES ON STOP: " + commaList(matchingStops, "Text")
		thisStopCode = matchingStops[0]["Value"]
		# Now, look up the bus schedule for the given location, and return the appropriate time,
		# or, return "" if there are no buses coming.
		departures = getTimepointDepartures(thisBusNumber, thisDirectionNumber, thisStopCode)
		nextDepartureRecordList = getNextBusRecord(departures)
		if (len(nextDepartureRecordList) == 0): return noBusReturnValue
		if returnDepartureText:
			return nextDepartureRecordList[0]["DepartureText"]
		else:
			return formatTimepoint(nextDepartureRecordList[0])
	except IOError:
		return "NETWORK ERROR"
	except:
		return "UNKNOWN ERROR"

#
#	Main program, for when the program is used independently on the command-line
#
if __name__ == "__main__":
	import sys
	helpText = """
	Example Command-Line: nextbus.py "bus-route" "bus-stop-name" "direction"
	
	bus-route:
		should be a unique substring of the name of the bus route you want
		If you put # followed by a number, it picks a particular Metro Transit
		route number.
		If you put #any, it lists all the routes in the resulting error message
	bus-stop-name:	
		should be a unique substring of the name of the bus stop
		If you put #any, it lists all the stops for that route in the 
		resulting error message
	direction:
		must be east, north, south, or west (case-insensitive)
		If you put #any, it lists all the directions for that route in the 
		resulting error message
	"""
	if (len(sys.argv)<2):
		# Special Case: Some web-based python viewers don't have 
		# command lines, so we just prompt for the parameters.
		while True:
			print("NextBus")
			print("To exit, press Enter without typing anything.")
			route = input("Enter part of the route's name, or type # for a route number (e.g. #21): ")
			if (route==""): exit(0)
			stop = input("Enter part of the stop's name, or type #any to see all of them: ")
			if (stop==""): exit(0)
			direction = input("Enter the direction (north, south, east, west): ")
			if (direction==""): exit(0)
			print ("")
			print (nextBus(route, stop, direction))
			print ("")
	elif sys.argv[1] == "/?" or sys.argv[1].upper()[0:3] == "--H" or sys.argv[1].upper()[0:2] == "/H":
		print(helpText)
		exit(0)
	elif len(sys.argv) != 4:
		print("PARAMETER ERROR: " + helpText)
		exit(1)
	else:
		print(nextBus(sys.argv[1],sys.argv[2],sys.argv[3]))
		exit(0)
