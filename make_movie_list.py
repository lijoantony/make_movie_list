#!/usr/bin/python

# get_movie_list: create a movie list sorted by imdb rating from a movie collection
# Copyright (C) 2013 Lijo Antony

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


import os
import sys
import re
import imdb # Import the imdb package.
from subprocess import call
from subprocess import Popen
import subprocess
import urllib as ul

#extensions for movie files
file_types = ['avi', 'mp4', 'mkv', 'VOB', 'm4v']

#common regex patterns to be stripped from the file names
patters_to_strip = [
    '\[.*\]',
    '\(.*\)',
    '{.*}',
    '[1|2][9|0]\d{2}',
    'dvd\.?rip',
    'xvid',
    'CD\d+',
    '-axxo',
    'mp3',
    'hdtv',
    'divx',
    'sharkboy',
    '\d{0,2}fps',
    '\d{0,3}kbps',
    'hddvd',
    'x264',
    'torr?ent.',
    'extended',
    'WunSeeDee',
    '\d{3,4}p',
    'Part\d',
    '-',
    '\.\.+'
    ]

def is_movie(filename):

    ftype = filename.split('.')[-1]
    if ftype in file_types:
        return True


def get_movie_name(filename):

    end = filename.rfind('.')
    movie_name = filename[0:end]
    movie_name = strip_patterns(movie_name)
    movie_name = movie_name.replace('.', ' ')
    movie_name = movie_name.strip()

    return movie_name

def strip_patterns(movie_name):

    for p in patters_to_strip:
        regex = re.compile(p, re.IGNORECASE)
        movie_name = regex.sub("", movie_name)

    return movie_name


def get_movie_info(movie_id):

    i = imdb.IMDb()

    try:
        # Get a Movie object with the data about the movie identified by
        # the given movieID.
        movie = i.get_movie(movie_id)
    except imdb.IMDbError, e:
        print "Probably you're not connected to Internet.  Complete error report:"
        print e
        sys.exit(3)


    if not movie:
        print 'It seems that there\'s no movie with movieID "%s"' % movie_id
        sys.exit(4)

    #print movie.summary()

    rating = movie.get('rating')

    if not rating:
        rating = 0.0

    return rating



def get_imdb_id(movie):

    #IMDB's search is crap
    #So, use the best search engine to find out the imdb id of a movie
    #use command line browser lynx to fool google
    #lynx -dump http://www.google.com/search?q=TheMatrix

    movie_encoded = ul.quote_plus(movie)
    p1 = Popen(["lynx","-dump", "http://www.google.com/search?q=" + movie_encoded],
                    stdout=subprocess.PIPE)
    p2 = Popen(["grep", "www.imdb.com/title/"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    tokens = output.split('/')

    try:
        i = tokens.index('title')
        movie_id = tokens[i+1]

        if movie_id[:2] == 'tt':
            movie_id = movie_id[2:]
    except ValueError:
        print 'No title for %s', movie
        movie_id = None

    return movie_id



###### START #######

if len(sys.argv) != 2:  # the program name and the path to search
    sys.exit("Usage: " + sys.argv[0] + " <path>")

path = sys.argv[1]
movie_set = set()


#scan the path for movies
for (path, dirs, files) in os.walk(path):
    for f in files:
        if is_movie(f) == True:
            f = get_movie_name(f)
            #print f
            movie_set.add(f)


movie_list = list(movie_set)
movie_list.sort()

#put this movie list into a temp file
file_name = 'movies.temp'
file_out = open(file_name, "w")
file_out.write('\n'.join(movie_list))
file_out.close()

#give a chance to user, to edit/correct/cleanup the movie names
call(["vim", file_name])

#now go back to work
file_in = open(file_name)
file_content = ""

while 1:
    line = file_in.readline()
    if not line:
        break
    file_content += line

movies = file_content.split('\n')
ratings = {}

for movie in movies:
    if movie:
        print movie
        movie_id = get_imdb_id(movie)

        if movie_id:
            rating = get_movie_info(movie_id)
            ratings[movie] = rating
        else:
            ratings[movie] = '0.0'


#store the result in a file
rating_file = open("movies.rating", "w")

for movie in sorted(ratings, key=ratings.get, reverse=True):
    rating_file.write(str(ratings[movie]))
    rating_file.write('\t')
    rating_file.write(movie)
    rating_file.write('\n')

rating_file.close()

#done
sys.exit(0)
