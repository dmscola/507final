Dominic Scola SI 507 Final Project AZ Lyrics scraper and Open Movie Database

Project Description: This project is a web scraper that asks the user to input 10 different songs and artists and then scrapes song lyrics from the website https://www.azlyrics.com/ and finds the 10 most common words from each song. Then, for each of these words, the program searches the Open Movie Database API and retrieve the first search result of each search term. Finally, the program uses Plotly to graph information related to all 100 movies including: country, box office earnings, IMDB score, and genre.

Data Sources Used: Lyric scraper: https://www.azlyrics.com/lyrics/<>/<>.html example: https://www.azlyrics.com/lyrics/johnnycash/hurt.html How it is used: Scraping HTML content using beautiful soup, programs scrapes the lyrics from the page and uses NLTK to find the most common words from the page, and eventually forms the records for the Words table. Requirements to use this data source: Beautiful soup

Open Movie Database API: http://www.omdbapi.com/ example: http://www.omdbapi.com/?t=Real&type=movie&apikey=<> How it is used: Search terms are placed in the "t" parameter of the call and the API responds with 1 movie instance from the API that matches the search term. This API response is used to form the Movie Class and eventually forms the records for the Movies table. Requirements to use this data sources: OMDB API key. API key is needed in order to access API results, see http://www.omdbapi.com/apikey.aspx to request a key. API Key must be placed in a file called "secrets.py" with the contents of the file being: api_key = 'XXXXXXXX' where XXXXXXXX is your API Key.

***Note there is a 1,000 call limit to the Free API key on the site. Running the program for new queries repeatedly will eventually reach this limit, but with caching the program never comes close. If there are any issues with the limit being reached, I have purchased the upgraded key for $1 on patreon that allows for 100,000 calls per day. If an instructor has an issue while grading this project please notify me and I will provide my updgraded key. ***

Other information needed to run program: plotly must be installed see https://plot.ly/python/getting-started/ for assistance for installing and configuring plotly. Other required libraries or packages needed are specified in requirements.txt

Description of code: Important Functions:

interactive_prompt() - handles the flow of control of the program including prompting user to input each of the songs and artists and prompting the user for presentation options.
make_request_using_cache() - Cache for Open Movie Database API calls
make_request_using_cache1() - Cache for azlyrics scraping
get_lyrics() - Takes a song title and artist name and access the corresponding page on azlyrics.com. Scrapes the page using beautiful soup to just the part of the page that contains the song lyrics. Strips the lyrics of extra HTML tags and extra info from lyrics including whether or not this song samples another song. Calls make_request_using_cache1()
frequency() - takes the lyrics from get_lyrics() and tokenizes using NLTK. Removes stopwords and punctuation and returns a list of the 10 most common words and their frequency distribution.
insertWords() || insertMovie() - inserts words/movies into media database
worldMap() || scatterPLot() || pieChart() || barGrapH() - plots data from Movie class objects constructed from media database
Important data structures:

movieList - list of instances of Movie class. Used as parameter for calling presentation options.
words - list of tuplies; return of frequency() function. Used to display word frequency distribution and used as basis for inserting records into Word table.
Classes: Movie: class used to handle returns from the Movie Table of Media Database. Used to form movieList for calling presentation options and to strip extra characters or modify values from the database so that plotly can handle the input data.

Data Processing: Data processing for presentation is largely done through frequency distribution. Frequency distribution is run on all songs in order to find the 10 most common words from each song. Frequency distribution is also used to calculate percentages of each genre for movie genre pie chart and for world map of movie country of origin. This processing is completed through lists of tuples to represent the data object label and its value. This processing occurs inside the function that calls the presentation option (pieChart() and worldMap()). Additionally, data processing also occurs in presentation options for Bar Graph and Scatter Plot. Inside their presentation function, the program calculates the average IMDB score and average Box office earnings respectively. These averages are displayed alongside the output in the plotly graphs.

User Guide: Downloading and keeping the cache files for this project are strongly encouraged. This program must make 100 calls to the OMDB API (one for each word) if it completely starts over without a cache. This process can take a long time.

Run 'lyrics.py' file from terminal. Program will welcome the user and the prompt the user to input 10 artist names and song titles. For each song, the program will prompt for artist name then song title. If the song cannot be located on azlyrics, the user will receive an error message and will be asked to enter a valid song. Once a valid song is found, the program will find the 10 most common words from the song, and for each word print to the terminal the artist name, song title, word, and how many times the word appeared in the lyrics. Typing '--exit' at any time will end the program. Once 10 songs have been input, the program will prompt the user with 4 display options:

1. View scatter plot of Movie IMDB Scores
2. View pie chart of Movie Genres
3. View world map of Movie Country of Origin
4. View bar graph of Movie Box Office Earnings
Inputting a number (1-4) will graph the results of the 100 words when the are searched on the Open Movie Database API. Below is a description of each of the presentation options and what they include:

1. a scatter plot to display the IMDB score of each movie vs. the year is was released
2. a pie chart to display what percentage of the movies belong to each genre (i.e. drama, comedy, action etc.)
3. a world map to display which country each of the movies comes from
4. a bar graph to display each movie side by side and display the total box office earnings

NOTE Presentation option 4 will usually not graph 100 data points. This is because the OMDB API does not box office earnings listed for all movies (especially movies from earlier decades). The program will inform the user how many movies it was able to find box office earnings data for while creating the plotly graph

  
  
