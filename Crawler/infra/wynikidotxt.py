# -*- coding: utf-8 -*-

import urllib2
import urlparse
import shelve
import nltk   
import codecs
import cgi
import string
import re
import os
from urllib import urlopen
from bs4 import BeautifulSoup

dict = {}
art_db = shelve.Shelf(dict, protocol=None, writeback=True)
art_db = shelve.open("./dane/wyniki.db")

for key in art_db.keys():
	key = key.decode("utf-8")
	path = os.path.realpath(__file__)
	path = path[0:len(path)-14]
	path += "/infra"
	if not os.path.exists(path):
		os.makedirs(path)
	filename = key + ".txt"

	f = open("./infra/" + filename, 'w')
	print "Zapis: " + filename
	f.write(art_db[key.encode("utf-8")])
	f.close