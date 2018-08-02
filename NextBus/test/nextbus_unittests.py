#!/usr/bin/env python3
#
#	NextBus.py
#	UNIT TESTS for Response to Target Case Study
#	Candidate: Dave White, dave4mpls@gmail.com, 612-695-3289
#	Position: Guest Reliability Engineer
#	Date Completed: 7-31-2018
#
#	These tests are rather extensive, but I figure I'm applying for
#	Reliability Engineer so more automated tests is better!
#
#	They do use web-scraping to independently verify that the
#	numbers from my program match what the user would see
#	on the Metro Transit interactive home page.  This would
#	increase the chance that the tests themselves might have
#	to be modified later if Metro Transit changes their interactive
#	home page, so in a real work environment, I'd determine whether
#	that level of independent testing outweighed the desire for
#	low maintenance.
#
#	Dependencies: unittest, json, time, math, requests
#		You may have to install json by using "pip install json"
#		You may have to install requests by uisng "pip install requests"
#		

import time
import nextbus
import unittest
import json
import requests

class TestNextBus(unittest.TestCase):

	def same_json(self, a,b):
		return json.dumps(a) == json.dumps(b)
		
	def mock_time_value(self, testValue, nowTime = None):
		# returns a fake JSON timestamp to help test the timestamp portion
		if nowTime is None: nowTime = time.time()
		return ("/Date(" + "{:.0f}".format(1000.0 * round(nowTime + testValue,3)) + "-0500)/")
	
	def assertAlmostEqualTimes(self, a, b):
		# asserts that the given times (e.g. 6 Min, 3 Min) retrieved from the Metro Transit UI and
		# the nextbus program are the same.  Sometimes a value changes right during the test,
		# between calling Metro Transit's UI and nextbus, so they're a minute off, and we accept that.
		alist = a.split(" ")
		blist = b.split(" ")
		if len(alist) == 2 and len(blist) == 2 and alist[1].upper() == "MIN" and blist[1].upper() == "MIN":
			# if they're both minutes, check for one-off-due-to-data-source-change.
			alist[0] = int(alist[0])
			blist[0] = int(blist[0])
			if (alist[0] + 1 == blist[0]): alist[0] = blist[0]
			elif (blist[0] + 1 == alist[0]): blist[0] = alist[0]
			self.assertEqual(alist[0], blist[0])
		else:
			# if they aren't both minutes, we just do regular assertEqual.
			self.assertEqual(a,b)

	def displayMetroTransitUITime(self, route, direction, stop):
		# some tests use the Metro Transit user-facing website to see if we get the same answer for next bus
		result = requests.get("https://www.metrotransit.org/NexTripBadge.aspx", params = { 'route': route, 'direction': direction, 'stop': stop })
		if not result.ok: raise IOError
		html = result.text
		startTag = '<b class="countdown">'
		findNextBusIndex = html.find(startTag)
		if findNextBusIndex >= 0:
			timeString = html[(findNextBusIndex + len(startTag)):]
			findEndTimeString = timeString.find('</b>')
			if findEndTimeString >= 0:
				timeString = timeString[0:(findEndTimeString)]
				return timeString
			else:
				raise IOError
		else:
			raise IOError
	
	def test_getMetroTransitService(self):
		self.assertTrue(len(nextbus.getMetroTransitService("/NexTrip/Routes")) > 5)
		self.assertTrue(isinstance(nextbus.getMetroTransitService("/NexTrip/Directions/4"), list))
		with self.assertRaises(IOError):
			nextbus.getMetroTransitService("/NexTrip/Unreal/Address")
	
	def test_suppressMultipleSpaces(self):
		self.assertEqual(nextbus.suppressMultipleSpaces("Cat Dog"),  ("Cat Dog"))
		self.assertEqual(nextbus.suppressMultipleSpaces("  Cat Dog"),  (" Cat Dog"))
		self.assertEqual(nextbus.suppressMultipleSpaces("Cat   Dog"),  ("Cat Dog"))
		self.assertEqual(nextbus.suppressMultipleSpaces("Cat  Dog"),  ("Cat Dog"))
		self.assertEqual(nextbus.suppressMultipleSpaces("Cat       Dog"),  ("Cat Dog"))
		self.assertEqual(nextbus.suppressMultipleSpaces("Cat       Dog    Rat"),  ("Cat Dog Rat"))
		self.assertFalse(nextbus.suppressMultipleSpaces(" Cat  Dog") == ("Cat Dog"))
		self.assertFalse(nextbus.suppressMultipleSpaces("Cat  Dog ") == ("Cat Dog"))
		
	def test_extractMatches(self):
		testList = [ { 'name': '4 - Lyndale Bryant', 'value': '3' }, {'name': '14 - Bloomington Lake', 'value': '4'}, {'name': '21 - Lake Marshall', 'value': '7'}, { 'name': '6 - Hennepin to 34th', 'value': '10' } ];
		self.assertEqual(json.dumps(nextbus.extractMatches(testList, 'name', 'Lyndale')).replace(" ",""), '[{"name":"4-LyndaleBryant","value":"3"}]')
		self.assertEqual(json.dumps(nextbus.extractMatches(testList, 'value', '3')).replace(" ",""), '[{"name":"4-LyndaleBryant","value":"3"}]')
		self.assertEqual(json.dumps(nextbus.extractMatches(testList, 'name', '4')).replace(" ",""), '[{"name":"4-LyndaleBryant","value":"3"},{"name":"14-BloomingtonLake","value":"4"},{"name":"6-Hennepinto34th","value":"10"}]')
		self.assertEqual(json.dumps(nextbus.extractMatches(testList, 'name', '#4')).replace(" ",""), '[{"name":"4-LyndaleBryant","value":"3"}]')
		self.assertEqual(json.dumps(nextbus.extractMatches(testList, 'name', '#14')).replace(" ",""), '[{"name":"14-BloomingtonLake","value":"4"}]')
		self.assertEqual(json.dumps(nextbus.extractMatches(testList, 'name', '#any')).replace(" ",""), json.dumps(testList).replace(" ",""))
		self.assertEqual(json.dumps(nextbus.extractMatches(testList, 'name', '#ANY')).replace(" ",""), json.dumps(testList).replace(" ",""))
		self.assertEqual(json.dumps(nextbus.extractMatches(testList, 'name', 'Lake')).replace(" ",""), '[{"name":"14-BloomingtonLake","value":"4"},{"name":"21-LakeMarshall","value":"7"}]')
		
	def test_getRouteMatches(self):
		self.assertTrue(self.same_json(nextbus.getRouteMatches("Plymouth - Annapolis"), [{'Description': '741 - Plymouth - Annapolis - Campus Dr - Station 73', 'ProviderID': '10', 'Route': '741'}]))
		for i in [4,6,10,21,54,14,535]: 
			with self.subTest(i=i):
				self.assertEqual(len(nextbus.getRouteMatches("#"+str(i))),1)
		self.assertEqual(nextbus.getRouteMatches("Bryant")[0]["Route"], "4")
		self.assertEqual(nextbus.getRouteMatches("Central Av - University Av")[0]["Route"], "10")
		self.assertEqual(len(nextbus.getRouteMatches("Squigmire")),0)
	
	def test_getDirectionMatches(self):
		for i in [2,16,46,21,902]: 
			with self.subTest(i=i,group=0):
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"east"), [{'Text': 'EASTBOUND', 'Value': '2'}]))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"EAST"), [{'Text': 'EASTBOUND', 'Value': '2'}]))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"west"), [{'Text': 'WESTBOUND', 'Value': '3'}]))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"WEST"), [{'Text': 'WESTBOUND', 'Value': '3'}]))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"NORTH"), []))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"SOUTH"), []))
		for i in [4,6,10,14,84]: 
			with self.subTest(i=i,group=1):
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"north"), [{'Text': 'NORTHBOUND', 'Value': '4'}]))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"NORTH"), [{'Text': 'NORTHBOUND', 'Value': '4'}]))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"south"), [{'Text': 'SOUTHBOUND', 'Value': '1'}]))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"SOUTH"), [{'Text': 'SOUTHBOUND', 'Value': '1'}]))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"WEST"), []))
				self.assertTrue(self.same_json(nextbus.getDirectionMatches(str(i),"EAST"), []))

	def test_getStopMatches(self):
		self.assertEqual(5, len(nextbus.getStopMatches("4","1","Lyndale")))
		self.assertEqual(5, len(nextbus.getStopMatches("4","1","LYNDALE")))
		self.assertEqual("FRLY", nextbus.getStopMatches("4","1","Franklin")[0]["Value"])
		self.assertEqual("UNSN", nextbus.getStopMatches("21","3","Snelling")[0]["Value"])
		self.assertEqual(0, len(nextbus.getStopMatches("21","4","Snelling")))
		self.assertEqual(0, len(nextbus.getStopMatches("21","3","Squidmore")))
		with self.assertRaises(IOError):
			nextbus.getStopMatches("21","SQUID","Snelling")[0]["Value"]			
	
	def test_getTimepointDepartures(self):
		for testArray in [["21","2","UPLV"], ["4","1","FRLY"], ["21","3", "UNSN"], ["535", "1", "MA4S"], ["535", "4", "7S2A"]]:
			with self.subTest(testArray=testArray):
				programResultArray = nextbus.getTimepointDepartures(*testArray)
				if len(programResultArray)==0:
					# no busses returned from our program, so metro transit website routine should throw exception.
					with self.assertRaises(IOError):
						self.displayMetroTransitUITime(*testArray)
				else:
					programResult = programResultArray[0]["DepartureText"]
					if programResult.upper() == "DUE": continue
					uiTestResult = self.displayMetroTransitUITime(*testArray)
					if uiTestResult.upper() == "DUE": continue    # ignore UI results of "due" meaning a bus is due
					self.assertAlmostEqualTimes(programResult, uiTestResult)

	def test_minutesTillBus(self):
		nowTime = round(time.time(),3)    # only millisecond accuracy exists in json time format, so don't test for greater accuracy
		for testValue in [0, 30, 60, 71, 90, 120, 240]:
			with self.subTest(testValue=testValue):
				self.assertAlmostEqual(nextbus.minutesTillBus({'DepartureTime': self.mock_time_value(testValue, nowTime) }, nowTime), testValue/60.0, 4)
	
	def test_formatTimepoint(self):
		nowTime = round(time.time(),3)    # only millisecond accuracy exists in json time format, so don't test for greater accuracy
		for testValue in [0, 30, 60, 71, 90, 120, 240]:
			with self.subTest(testValue=testValue):
				minNumber = int(round(testValue / 60))
				if minNumber == 1:
					minText = "1 Minute"
				else:
					minText = str(minNumber) + " Minutes"
				self.assertEqual(nextbus.formatTimepoint({'DepartureTime': self.mock_time_value(testValue, nowTime) }, nowTime), minText)
	
	def test_getNextBusRecord(self):
		testArray1 = [{'DepartureTime': self.mock_time_value(-30), 'Field': 37}, {'DepartureTime': self.mock_time_value(240), 'Field': 64}]
		self.assertEqual(nextbus.getNextBusRecord(testArray1)[0]['Field'], 64)
		testArray2 = [{'DepartureTime': self.mock_time_value(10), 'Field': 37}, {'DepartureTime': self.mock_time_value(240), 'Field': 64}]
		self.assertEqual(nextbus.getNextBusRecord(testArray2)[0]['Field'], 37)
		testArray3 = [{'DepartureTime': self.mock_time_value(-30), 'Field': 37}, {'DepartureTime': self.mock_time_value(-20), 'Field': 64}]
		self.assertEqual(len(nextbus.getNextBusRecord(testArray3)), 0)

	def test_commaList(self):
		testList = [ { 'name': '4 - Lyndale Bryant', 'value': '3' }, {'name': '14 - Bloomington Lake', 'value': '4'}, {'name': '21 - Lake Marshall', 'value': '7'}, { 'name': '6 - Hennepin to 34th', 'value': '10' } ];
		self.assertEqual(nextbus.commaList(testList, 'name'), "4 - Lyndale Bryant, 14 - Bloomington Lake, 21 - Lake Marshall, 6 - Hennepin to 34th")
		self.assertEqual(nextbus.commaList(testList, 'value'), "3, 4, 7, 10")
		self.assertEqual(nextbus.commaList([ ], 'value'), "")
	
	def test_nextbus(self):
		print("")
		testList = [ ["21", "Snelling", "West", "*MULTIPLE MATCHES ON ROUTE:" ], \
			["21 - Uptown", "Snelling", "East", "!",  ["21", "2", "SNUN"]], ["#21", "Snelling", "East", "!", ["21", "2", "SNUN"]],\
			["927","Marquette","East", "@NO MATCH ON ROUTE" ], \
			["#21","54th St", "West", "@NO MATCH ON STOP" ], \
			["#21","Snelling", "North", "@NO MATCH ON DIRECTION" ], \
			["#21","Snelling", "t", "@MULTIPLE MATCHES ON DIRECTION: EASTBOUND, WESTBOUND" ],\
			["#21","Snelling", "#any", "@MULTIPLE MATCHES ON DIRECTION: EASTBOUND, WESTBOUND" ],\
			["Bryant", "Lake", "south", "*MULTIPLE MATCHES ON STOP:" ], \
			["Bryant", "Lake St", "south", "!", ["4", "1", "LALY"]], \
			["#5", "46th", "north", "!", ["5", "4", "46CH"]], \
			["#84", "Randolph", "north", "!", ["84", "4", "RASN"]], \
			["535", "Marquette Ave and 4th", "south", "!", ["535", "1", "MA4S"]], \
			["Express - Target - Hwy 252 and 73rd Av P&R - Mpls", "Target North Campus Building F", "south", "!", ["765", "1", "TGBF"]] ]
		for thisTest in testList:
			with self.subTest(thisTest=thisTest):
				print ("Testing full program with route: " + str(thisTest[0]) + ", stops: " + str(thisTest[1]) + ", direction: " + str(thisTest[2]))
				nextBusResult = nextbus.nextBus(thisTest[0],thisTest[1],thisTest[2], True)
				print ("Result: " + nextBusResult)
				if thisTest[3] == "!":
					# this test should produce a number of minutes
					if nextBusResult == "":  # esp testing the target bus after 5, it returns no buses, and website raises exception due to missing "next bus" text.
						with self.assertRaises(IOError):
							uiTestResult = self.displayMetroTransitUITime(*thisTest[4])
					else:
						print ("Comparing with result from Metro Transit web page")
						uiTestResult = self.displayMetroTransitUITime(*thisTest[4])
						print ("Web page result: " + uiTestResult)
						if uiTestResult.upper() == "DUE": continue    # ignore UI results of "due" meaning a bus is due
						if nextBusResult.upper() == "DUE": continue
						self.assertAlmostEqualTimes(nextBusResult, uiTestResult)
				elif thisTest[3][0] == "*":
					# this test should return a result with the given prefix
					self.assertEqual(nextBusResult[0:(len(thisTest[3])-1)], thisTest[3][1:])
				elif thisTest[3][0] == "@":
					# this test should return an exact result
					self.assertEqual(nextBusResult, thisTest[3][1:])
				else:
					# other values cause a test failure
					self.fail("test type was not valid")

if __name__ == "__main__":
	print ("------------------------------------------------------------")
	print ("NextBus Unit Tests:")
	print ("These tests use realtime data and web scraping to ")
	print ("ensure that NextBus matches Metro Transit's NextTrip website.")
	print ("If you get an error, it may be that the test suite needs to be ")
	print ("modified to match changes in the Metro Transit public website.")
	print ("------------------------------------------------------------")
	unittest.main(verbosity=2)
