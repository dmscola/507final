from lyrics import *
import unittest


#You must write unit tests to show that the data access, storage, and processing components of your project are working correctly. You must create at least 3 test cases and use at least 15 assertions or calls to ‘fail( )’. Your tests should show that you are able to access data from all of your sources, that your database is correctly constructed and can satisfy queries that are necessary for your program, and that your data processing produces the results and data structures you need for presentation.

class azLyricsAccess(unittest.TestCase):
	def testvalidAZ(self):
		artistname = "John Mayer"
		songtitle = "Gravity"
		self.words = frequency(artistname, songtitle)
		#Valid song and artist return a list of tuples in format (string, number)
		self.assertEqual(type(self.words), list)
		self.assertEqual(type(self.words[0]), tuple)
		self.assertEqual(type(self.words[0][0]), str)
		self.assertEqual(type(self.words[0][1]), int)

		#Testing that scraper is able to find the word 'keep' as the most common word from John Mayer "Gravity" with 7 appearances.
		self.assertEqual(self.words[0][0], "keep")
		self.assertEqual(self.words[0][1], 7)


	def testbadAZ(self):
		artistname = "BADINPUT"
		songtitle = "BADINPUT"
		self.words = frequency(artistname, songtitle)

		# Invalid song and artist returns a string saying an exception has occurred when attempting to scrape AZ lyrics

		self.assertEqual(type(self.words), str)
		self.assertEqual(self.words, "Exception occurred \nHTTP Error 404: Not Found")

class OMDB_Access(unittest.TestCase):
	def testvalidSearch(self):
		parameters["t"] = "amazing"
		parameters['apikey'] = apikey
		base_url = "http://www.omdbapi.com/?"
		parameters['type'] = "movie"


		self.response = make_request_using_cache(base_url, parameters)

		#Search parameter that is valid returns a movie object with a title, Search "Amazing" and get back "The Amazing Spider-Man". Valid search also returns a "Response" value of "True"
		self.assertEqual(self.response['Response'], "True")
		self.assertEqual(self.response['Title'], "The Amazing Spider-Man")

	def testinValidSearch(self):
		parameters["t"] = "sussudio"
		parameters['apikey'] = apikey
		base_url = "http://www.omdbapi.com/?"
		parameters['type'] = "movie"

		#Search paramter that is invalid (Phil Collins made up word 'sussudio') returns "Response" value of false

		self.response = make_request_using_cache(base_url, parameters)
		self.assertEqual(self.response['Response'], "False")

class Database(unittest.TestCase):
	def testLength(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		#*************************

		#Dropping database and starting over to test for length
		statement = '''
		    DROP TABLE IF EXISTS 'Words';
		'''
		cur.execute(statement)

		statement = '''
		    DROP TABLE IF EXISTS 'Movies';
		'''
		cur.execute(statement)
		conn.commit()

		statement = '''

		CREATE TABLE `Words` (
		    `Id`        INTEGER PRIMARY KEY AUTOINCREMENT,
		    `ArtistName`  Text ,
		    `SongTitle` Text ,
		    `wordText`  TEXT ,
		    'wordCount' INTEGER 

		);'''

		cur.execute(statement)
		conn.commit()


		statement = '''


		CREATE TABLE `Movies` (
		    `Id`        INTEGER PRIMARY KEY AUTOINCREMENT,
		    `MovieTitle`  Text ,
		    'IMDB' REAl, 
		    `Genre` Text ,
		    `Country`  TEXT ,
		    'BoxOfficeEarnings' REAL,
		    'year' TEXT,
		    'searchWord' TEXT,
		     FOREIGN KEY(searchWord) REFERENCES Words(wordText)

		);'''


		cur.execute(statement)
		conn.commit()

		#*************************

		parameters["t"] = "walk"
		parameters['apikey'] = apikey
		base_url = "http://www.omdbapi.com/?"
		parameters['type'] = "movie"

		#Test insertion of movie into database. Because each record in the database requires a api call to populate the database, these tests only test whether or not the database is populated when 1 is called and if we can select columns from the database.
		insertMovie(make_request_using_cache(base_url, parameters), "walk")

		sql = 'SELECT MovieTitle FROM Movies'
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(('Walk the Line',), result_list)
		self.assertEqual(len(result_list), 1)

		sql = 'SELECT year, BoxOfficeEarnings FROM Movies'
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(('2005'), result_list[0])
		self.assertEqual(len(result_list), 1)


class Presentation(unittest.TestCase):
	def testinit(self):

		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		parameters["t"] = "walk"
		parameters['apikey'] = apikey
		base_url = "http://www.omdbapi.com/?"
		parameters['type'] = "movie"

		insertMovie(make_request_using_cache(base_url, parameters), "walk")	

		parameters["t"] = "amazing"
		parameters['apikey'] = apikey
		base_url = "http://www.omdbapi.com/?"
		parameters['type'] = "movie"

		insertMovie(make_request_using_cache(base_url, parameters), "amazing")

		statement = '''INSERT OR IGNORE INTO Words 
		(ArtistName, SongTitle, wordText, wordCount) 
		VALUES ("Johhny Cash", "Walk the Line", "walk", 10)'''
		cur.execute(statement)
		conn.commit()

		statement = '''INSERT OR IGNORE INTO Words 
		(ArtistName, SongTitle, wordText, wordCount) 
		VALUES ("Kanye West", "Amazing", "amazing", 27)'''
		cur.execute(statement)
		conn.commit()


		statement = '''Select Distinct MovieTitle, IMDB, Genre, Country, BoxOfficeEarnings, year, Words.wordText
		From Movies
		Join Words on Movies.searchWord = Words.wordText'''

		cur.execute(statement)
		conn.commit()

		returnlist= []

		for row in cur:
		    returntup = (row[0], row[1], row[2], row[3], row[4], row[5], row[6])
		    returnlist.append(returntup)

		movieList= []

		for elem in returnlist:
			movieList.append(Movie(title=elem[0], IMDB = elem[1], genre= elem[2], country= elem[3], BoxOfficeEarnings = elem[4], year = elem[5], word = elem[6]))


	# we can't test to see if the graphs look correct, but we can test that functions don't return an error and that graphs are created
		try:
			worldMap(movieList)
		except:
			self.fail()

		try:
			barGraph(movieList)
		except:
			self.fail()

		try:
			pieChart(movieList)
		except:
			self.fail()

		try:
			scatterPlot(movieList)
		except:
			self.fail()



unittest.main()