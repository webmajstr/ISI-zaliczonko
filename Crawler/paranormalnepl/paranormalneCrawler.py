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
import HTMLParser
from urllib import urlopen
from bs4 import BeautifulSoup

class paranormalneCrawler(object):

    def __init__(self):

        if not os.path.exists("./dane/"):
            os.makedirs("./dane/")

        self.dict = {}
        self.link_db = shelve.Shelf(self.dict, protocol=None, writeback=True)
        self.link_db = shelve.open("./dane/dbname.db")
        self.art_db = shelve.Shelf(self.dict, protocol=None, writeback=True)
        self.art_db = shelve.open("./dane/wyniki.db")
        self.tmp_db = shelve.Shelf(self.dict, protocol=None, writeback=True)
        self.tmp_db = shelve.open("./dane/tmp.db")
        self.artnum = len(self.art_db)

    def __del__(self):
        print "Poprawnie dodano " + str(self.artnum) + " nowych artykułów do bazy"
        self.link_db.close()
        self.art_db.close()
        self.tmp_db.close()

    def is_article(self, url):
        if ("http://www.paranormalne.pl/tutorials/article/" not in url):
            return False
        if ("/?k=" in url):
            return False
        if ("setlanguage=" in url):
            return False
        if ("langid=" in url):
            return False
        if ("module=messaging" in url):
            return False
        return True

    def is_category(self, url):
        if ("http://www.paranormalne.pl/tutorials/" not in url):
            return False
        if ("/?k=" in url):
            return False
        if ("setlanguage=" in url):
            return False
        if ("langid=" in url):
            return False
        if ("module=messaging" in url):
            return False
        return True

    def clear_line(self,line):

        while (len(line)>0):
            if (line[-1] == '\t' or line[-1] == '\n' or line[-1] == ' ' or line[-1] == '\r'):
                line = line[0:len(line)-1]
            elif (line[0] == '\t' or line[0] == '\n' or line[0] == ' ' or line[-1] == '\r'):
                line = line[1:len(line)]
            else:
                break

        return line

    def crawl_one_page(self, url):
        try:
            urlobject = urllib2.urlopen(url, timeout=120)
            if not self.is_html(urlobject):
                self.link_db[url.encode("utf-8")] = 2
                return set()
            urlcontent = urlobject.read()
        except KeyboardInterrupt:
            exit()
        except urllib2.HTTPError, e:
            urlobject = e
            urlcontent = urlobject.read()
        except:
            self.link_db[url.encode("utf-8")] = 3
            return set()
        try:
            soup = BeautifulSoup(urlcontent)
        except KeyboardInterrupt:
            exit()
        except:
            self.link_db[url.encode("utf-8")] = 4
            return set()
        if (self.is_article(url)==True):
            ####################################################################
            _, params = cgi.parse_header(urlobject.headers.get('Content-Type', ''))
            encoding = params.get('charset', 'utf-8')
            html = urlcontent.decode(encoding)    
            raw = nltk.clean_html(html) 
            
            h = HTMLParser.HTMLParser()
            raw = h.unescape(raw)

            linie = re.split('\n|\t',raw)

            linie[0] = linie[0].replace("?","")
            linie[0] = linie[0].replace("/","")

            if not linie[0].encode("utf-8") in self.art_db:

                linia = 1
                for i in range(0,len(linie)-1):
                    if ("Napisane przez" in linie[i]):
                        for j in range(i,len(linie)-1):
                            if ("dnia" in linie[j]):
                                linia = j+1
                                break;

                if (linia==1):
                    print "ERROR 1"

                regexp = re.compile(r'\w')

                wynik = ""

                for i in range(linia,len(linie)-1):
                    if regexp.search(linie[i]) is not None:
                        linie[i] = self.clear_line(linie[i])
                        if (len(linie[i])>1):
                            wynik += linie[i]
                            linia = i+1
                        break

                for i in range(linia,len(linie)-1):
                    if ("\t\t\t\t\t\t\t0" in linie[i]):
                        break
                    if ("Reklama w internecie" in linie[i]):
                        break
                    if (len(linie[i])>0):
                        if (linie[i][0]!='\t' and linie[i][0]!=' ' and linie[i][0]!='\n'):
                            linie[i] = self.clear_line(linie[i])
                            if (len(linie[i])>1):
                                linie[i] = '\n' + linie[i]
                                wynik += linie[i]
                        elif (linie[i][0]==' ' and len(linie[i])>3 and linie[i][1]!=' ' and linie[i][1]!='\t'):
                            linie[i] = self.clear_line(linie[i])
                            if (len(linie[i])>1):
                                linie[i] = '\n' + linie[i]
                                wynik += linie[i]

                while (wynik[0]==" " or wynik[0]=="\t" or wynik[0]=="\n"):
                    wynik = wynik[1:len(wynik)]
                    if (len(wynik)==0):
                        break

                while (wynik[-1]==" " or wynik[-1]=="\t" or wynik[-1]=="\n"):
                    wynik = wynik[:-1]
                    if (len(wynik)==0):
                        break

                if (len(wynik)>3):
                    self.artnum = self.artnum + 1
                    self.art_db[linie[0].encode("utf-8")] = wynik.encode("utf-8")
                    print "Nowy (" + str(self.artnum) + "): " + url + '\n'
                else:
                    print "CHECK! - " + url + "\n"

        ####################################################################
        links = self.get_links(url, soup)
        self.link_db[url.encode("utf-8")] = 1
        return links

    def crawl_one_level(self):

        for key in self.link_db.keys():
            key = key.decode("utf-8")
            if self.link_db[key.encode("utf-8")] == 0:
                wyn = self.crawl_one_page(key)
                wyn = set(wyn)
                for i in wyn:
                    if i.encode("utf-8") not in self.tmp_db:
                        self.tmp_db[i.encode("utf-8")] = 0

                self.link_db.sync()
                self.art_db.sync()
                self.tmp_db.sync()

    def crawl(self, depth):

        for i in range(0,depth):
            print "---- Crawl level: " + str(i+1) + " ----" + '\n'
            self.crawl_one_level()
            self.inject_urls()

    def inject_urls(self, start="http://www.paranormalne.pl/tutorials/"):

        if (len(self.link_db.keys())==0):
            self.link_db[start.encode("utf-8")] = 0

        for url in self.tmp_db.keys():
            if not url in self.link_db:
                self.link_db[url] = 0

        self.tmp_db.clear()

    def is_html(self, urlobject):

        return urlobject.info().gettype() == "text/html"

    def get_links(self, page, soup):

        stri = list()
        for strona in soup.findAll('a'):
            if strona.has_attr('href'):
                if strona['href'][0:4] == "http":
                    stri.append(strona['href'])
                else:
                    stri.append(urlparse.urljoin(page, strona['href']))

        str2 = list()
        for i in range(0,len(stri)):
            if stri[i].find('#') != -1:
                stri[i] = stri[i][0:stri[i].find('#')]
            if (self.is_article(stri[i])==True or self.is_category(stri[i])==True):
                str2.append(stri[i])

        return set(str2)


if __name__ == '__main__':
    NPL = paranormalneCrawler()
    NPL.inject_urls()
    NPL.crawl(100)