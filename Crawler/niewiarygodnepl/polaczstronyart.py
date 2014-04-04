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
art_db = shelve.open("wyniki.db")

do_usuniecia = list()

for key1 in art_db.keys():
	key1 = key1.decode("utf-8")
	if (" - Strona " not in key1):
		strona = 2
		work = True
		while (work == True):
			for key2 in art_db.keys():
				key2 = key2.decode("utf-8")
				if ((key1 + " - Strona " + str(strona)) == key2):
					text1 = art_db[key1.encode("utf-8")].decode("utf-8")
					text2 = art_db[key2.encode("utf-8")].decode("utf-8")
					text1 = text1 + '\n'
					text1 = text1 + text2
					art_db[key1.encode("utf-8")] = text1.encode("utf-8")
					strona = strona + 1
					do_usuniecia.append(key2)
					print "Dodano stronę do artykułu: " + key1.encode("utf-8")
				else:
					work = False

for key in do_usuniecia:
	del art_db[key.encode("utf-8")]

art_db.close()