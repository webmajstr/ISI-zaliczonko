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

class niewiarygodneplCrawler(object):

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
        if ("http://niewiarygodne.pl/kat," not in url):
            return False
        if (",title," not in url):
            return False
        if (",wiadomosc.html" not in url):
            return False
        if (",opage," in url):
            return False
        if (",sort," in url):
            return False
        return True

    def is_category(self,url):
        if ("http://niewiarygodne.pl/kat," not in url):
            return False
        if (",title," not in url):
            return False
        if (",opage," in url):
            return False
        if (",sort," in url):
            return False
        return True

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

            tmp = url
            tmp = tmp[24:len(tmp)-5]
            ####################################################################
            _, params = cgi.parse_header(urlobject.headers.get('Content-Type', ''))
            encoding = params.get('charset', 'utf-8')
            html = urlcontent.decode(encoding)    
            raw = nltk.clean_html(html) 
            
            linie = raw.split('\n')

            linie[0] = linie[0].replace(" - Niewiarygodne.pl ","")
            linie[0] = linie[0].replace("?","")
            linie[0] = linie[0].replace("&amp;#8222;","")
            linie[0] = linie[0].replace("&quot;","")
            linie[0] = linie[0].replace("&amp;#8221;","")
            linie[0] = linie[0].replace(" - Media","")
            linie[0] = linie[0].replace(" - Filmy","")
            linie[0] = linie[0].replace("/","")

            if not linie[0].encode("utf-8") in self.art_db:

                licznik = 0
                linia = 1
                for i in range(0,len(linie)-1):
                    if ("\t\t\t\t A " in linie[i]):
                        licznik = licznik + 1
                        if (licznik == 3):
                            linia = i+1
                            break

                regexp = re.compile(r'\w')

                for i in range(linia,len(linie)-1):
                    if regexp.search(linie[i]) is not None:
                        wynik = linie[i]
                        linia = i+1
                        break

                for i in range(linia,len(linie)-1):
                    if ("Polub niewiarygodne.pl na Facebooku" in linie[i]):
                        break
                    if (len(linie[i])>0):
                        if (linie[i][0]!='\t' and linie[i][0]!=' ' and linie[i][0]!='\n'):
                            wynik += linie[i]

                while (wynik[0]==" " or wynik[0]=="\t"):
                    wynik = wynik[1:len(wynik)]
                    if (len(wynik)==0):
                        break

                if (len(wynik)>0):
                    wynik = wynik[0:len(wynik)-1]
                    self.art_db[linie[0].encode("utf-8")] = wynik.encode("utf-8")
                    self.artnum = self.artnum + 1
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
            if not self.link_db[key.encode("utf-8")] == 1:
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

    def inject_urls(self, start="http://niewiarygodne.pl/"):

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
    NPL = niewiarygodneplCrawler()
    NPL.inject_urls()
    NPL.crawl(100)