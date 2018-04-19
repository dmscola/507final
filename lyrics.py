import re
import urllib.request
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import json
import sqlite3
import json
import plotly.plotly as py
import requests
import string
import pycountry
import plotly.graph_objs as go

 
DBNAME = 'media1.db'

global word_list 
word_list =[]
apikey = 'f2b78768'
word_input = 'Gump' 


class Movie(object):

	def __init__(self, title = "No Title", IMDB="No score", genre = "No Genre", country = "No Country", BoxOfficeEarnings = "N/A", year = "None", word = "NULL"):
		self.title = title
		self.IMDB = IMDB
		genres = genre.split(",")
		countries = country.split(",")
		self.genre = genres[0]
		self.country = countries[0]
		if self.country == "USA":
			self.country = "United States"
		if self.country == "UK":
			self.country = "United Kingdom"
		self.BoxOfficeEarnings = BoxOfficeEarnings
		self.word = word
		self.year = year





CACHE_FNAME = 'movies.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

CACHE_FNAME1 = 'azlyrics.json'
try:
    cache_file = open(CACHE_FNAME1, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION1 = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION1 = {}


def make_request_using_cache1(artist, song_title):
    #defining anytime a sample is used in songs
    Sample = "[Sample - "
    #artist name
    artist = artist.lower()
    song_title = song_title.lower()
    # remove all except alphanumeric characters from artist and song_title
    artist = re.sub('[^A-Za-z0-9]+', "", artist)
    song_title = re.sub('[^A-Za-z0-9]+', "", song_title)
    if artist.startswith("the"):    # remove starting 'the' from artist e.g. the who -> who
        artist = artist[3:]
    url = "http://azlyrics.com/lyrics/"+artist+"/"+song_title+".html"    

    if url in CACHE_DICTION1:
        return CACHE_DICTION1[url]
    else:
        resp = urllib.request.urlopen(url).read()
        CACHE_DICTION1[url] = resp.decode('utf-8')
        dumped_json_cache = json.dumps(CACHE_DICTION1)
        fw = open(CACHE_FNAME1,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION1[url]


# A helper function that accepts 2 parameters
# and returns a string that uniquely represents the request
# that could be made with this info (url + params)
def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params):
    unique_ident = params_unique_combination(baseurl,params)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:

        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        resp = requests.get(baseurl, params)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

#Code for Part 1:Get Movie
parameters = {}
base_url = "http://www.omdbapi.com/?"
parameters["t"] = word_input
parameters['apikey'] = apikey
parameters['type'] = "movie"




try:
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
except Exception as e:
    print(e)




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


def get_lyrics(artist,song_title):
    Sample = "[Sample - "

    try:
        content = make_request_using_cache1(artist, song_title)
        soup = BeautifulSoup(content, 'html.parser')

        lyrics = str(soup)
        # lyrics lies between up_partition and down_partition
        up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->'
        down_partition = '<!-- MxM banner -->'
        lyrics = lyrics.split(up_partition)[1]
        lyrics = lyrics.split(down_partition)[0]
        lyrics = lyrics.replace('<br>','').replace('</br>','').replace('</div>','').strip()
        lyrics = lyrics.replace('<i>', '').replace('<br/>', '').replace('</i>', '').strip()
        lyrics = lyrics.replace('\n', " ")
        if lyrics.startswith(Sample):

            lyrics = lyrics.replace(Sample, '').strip()

        return lyrics
    except Exception as e:
        return "Exception occurred \n" +str(e)

def frequency(artist, song):
    lyrics = get_lyrics(artist, song)
    if lyrics.startswith("Exception occurred"):
        return lyrics
    lyrics = lyrics.lower()
    tokens = lyrics.split(" ")
    for elem in tokens:
        elem = elem.replace("?", "")
        elem = elem.replace("!", "")
        elem = elem.replace(".", "")
        elem = elem.replace(",", "")


    updated_tokens = []
    for elem in tokens:
        try:
            if elem[0].isalpha() == True:
                updated_tokens.append(elem)
        except:
            pass
    update1 = []
    for elem in updated_tokens:
    	out = "".join(c for c in elem if c not in ('!','.',':',',','(',')'))
    	update1.append(out)


    #remove stop words and elements of a song
    operators = set(('chorus', 'intro', 'outro', "verse"))
    stop = set(stopwords.words('english'))
    stop.update(operators)

    final_tokens = []
    for elem in update1:
        if elem not in stop:
            final_tokens.append(elem)

    for elem in final_tokens:
        if elem in word_list:
            final_tokens.remove(elem)

    fdist = nltk.FreqDist(final_tokens)
    print("The 10 most common words from this song are:")
    words = fdist.most_common(10)

    for elem in words:
        word = elem[0]
        word_list.append(word)
    return words


def insertWords(word):
    cur.execute("INSERT OR IGNORE INTO Words (ArtistName, SongTitle, wordText, wordCount) VALUES (?, ?, ?, ?)", word)
    conn.commit()

def insertMovie(movie, word):
    name = "NULL"
    genre = "NULL"
    country = "NULL"
    imdbRating = "NULL"
    boxoffice = "NULL"
    year = "NULL"

    try:
        name = movie["Title"]
        genre = movie["Genre"]
        country = movie["Country"]
        imdbRating = movie["imdbRating"]
        boxoffice = movie["BoxOffice"]
        year = movie["Year"]
    except:
        pass


    movie = (name, imdbRating, genre, country, boxoffice, year, word)

    cur.execute("INSERT OR IGNORE INTO Movies (MovieTitle, IMDB, Genre, Country, BoxOfficeEarnings, year, searchWord) VALUES (?, ?, ?, ?, ?, ?, ?)", movie)
    conn.commit()

def worldMap(movieList):

	names = []
	countryList = []
	movieList2 = []

	for elem in movieList:
		if elem.country == "N/A":
			pass
		else:
			movieList2.append(elem)

	for elem in movieList2:
		names.append(elem.title)
		countryList.append(elem.country)


	countries = {}
	for country in pycountry.countries:
		countries[country.name] = country.alpha_3

	codes = [countries.get(country) for country in countryList]

	final_codes = []

	for elem in codes:
		if elem == None:
			pass
		else:
			final_codes.append(elem)

	fdist = nltk.FreqDist(final_codes)

	most_common = fdist.most_common(100)
	locations = []
	vals = []
	for elem in most_common:
		locations.append(elem[0])
		vals.append(elem[1])

	data = [ dict(
        type = 'choropleth',
        locations = locations,
        z = vals,

        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(
            autotick = False,
            title = 'Number of Movies made in country'),
      ) ]

	layout = dict(
    	title = 'World Map of Movie Country of Origin',
    	geo = dict(
        	showframe = False,
        	countriescolor = "#444444",
    		showcountries =  True,
        	showcoastlines = False,
        	projection = dict(
            	type = 'Mercator'
        )
    )
	)

	fig = dict( data=data, layout=layout )
	py.plot( fig, validate=False, filename='d3-world-map' )

def pieChart(movieList):
	labels = []
	values = []


	names = []
	genres = []
	movieList2 = []

	for elem in movieList:
		if elem.genre == "N/A":
			pass
		else:
			movieList2.append(elem)

	for elem in movieList2:
		names.append(elem.title)
		genres.append(elem.genre)

	fdist = nltk.FreqDist(genres)

	most_common = fdist.most_common(100)

	for elem in most_common:
		labels.append(elem[0])
		values.append(elem[1])	

	trace = go.Pie(labels=labels, values=values,
		hoverinfo='label+percent', textinfo='percent', 
		textfont=dict(size=14),
		marker=dict(colors='colors', 
			line=dict(color='#000000', width=2)))


	layout = go.Layout(
	title = "Movie Genre Pie Chart"
	)

	data = [trace]

	fig= go.Figure(data=data, layout=layout)

	py.plot(fig, filename='Movie Genre Pie Chart')

def scatterPlot(movieList):
	years = []
	scores = []
	names = []

	movieList2 = []
	print(len(movieList))
	for elem in movieList:
		if elem.IMDB == "N/A":
			pass
		else:
			movieList2.append(elem)

	for elem in movieList2:
		years.append(int(elem.year))
		scores.append(float(elem.IMDB))
		names.append(elem.title)

	print(len(years), len(scores), len(names))

	trace = go.Scatter(
	x = years,
	y = scores,
	text = names,
	textposition = "bottom",
	mode = 'markers')

	layout=go.Layout(
		title='IMDB Scores of Movies',
		hovermode = 'closest',
		xaxis = dict(
			title='Year Released',
			ticklen=5,
			zeroline = False,
			gridwidth =2,),
		yaxis = dict(
			title='IMDB Score',
			ticklen=5,
			gridwidth =2,),
		showlegend = False)

	data = [trace]

	fig= go.Figure(data=data, layout=layout)
	py.plot(fig, filename='Movie Scatter Plot')

def interactive_prompt():
    print("\n")
    print("Welcome. Please enter 10 songs to find their 10 most frequently used words.")
    print("These words will be searched on the Online Movie Database API and the results will be graphed for you")
    print("Enter '--exit' to quit the program at any time")
    print("\n")
    count = 1
    artistname =""
    songtitle = ""
    while (count != 11):

        artistname = input('Enter artist: ')
        if artistname == "--exit":
            break
        songtitle = input('Enter title: ')
        if songtitle == "--exit":
            break

        words = frequency(artistname, songtitle)
        if type(words) == list:
            for elem in words:
                word = (artistname, songtitle, elem[0], elem[1])
                print(word[0], word[1], word[2], word[3])
                insertWords(word)

                parameters["t"] = word[2]
                parameters['apikey'] = apikey

                insertMovie(make_request_using_cache(base_url, parameters),word[2])


                

        
        else:
            print("Unable to find song data for your inputs. Please enter a valid artist and song name")

   
        count = count +1


    try:
    	conn = sqlite3.connect("media.db")
    	cur = conn.cursor()
    except Exception as e:
    	print(e)

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



    print("\n")
    print("1. View scatter slot of Movie IMDB Scores")
    print("2. View pie chart of Movie Genres")
    print("3. View world map of Movie Country of Origin")
    print("4. View bar graph of Movie Box Office Earnings")
    selection = input("Make a selection or enter '--exit' to exit the program: ")
    while(selection!="--exit"):
    	if selection == '1':
    		scatterPlot(movieList)
    	elif selection == '2':
    		pieChart(movieList)
    	elif selection == '3':
    		worldMap(movieList)
    	elif selection == '4':
    		print("put pie chart here")
    	elif selection =="--exit":
    		print("Goodbye")
    	else:
    		print("bad input, make a valid selection or type '--exit' to exit")
    		selection = input("Make a selection or enter '--exit' to exit the program: ")
    	selection = input("Make a selection or enter '--exit' to exit the program: ")
    

if __name__=="__main__":
    interactive_prompt()

