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

    def __init__(self, dbname):
        self.dict = {}
        self.link_db = shelve.Shelf(self.dict, protocol=None, writeback=True)
        self.link_db = shelve.open(dbname)
        self.art_db = shelve.Shelf(self.dict, protocol=None, writeback=True)
        self.art_db = shelve.open("wyniki.db")
        self.artnum = 0

    def __del__(self):
        print "Zapisywanie wyników"
        print "Poprawnie dodano " + str(self.artnum) + " nowych artykułów do bazy"
        self.link_db.close()
        self.art_db.close()

    def is_article(self, url):
        if ("http://niewiarygodne.pl/kat," not in url):
            return False
        if (",title," not in url):
            return False
        if (",wiadomosc.html" not in url):
            return False
        if (",opage," in url):
            return False
        return True

    def crawl_one_page(self, url):
        try:
            urlobject = urllib2.urlopen(url, timeout=5)
            if not self.is_html(urlobject):
                self.link_db[url.encode("utf-8")] = 2
                return set()
            urlcontent = urlobject.read()
        except KeyboardInterrupt:
            exit()
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
            print "Nowy art: " + url + '\n'
            ####################################################################
            r = urllib2.urlopen(url)
            _, params = cgi.parse_header(r.headers.get('Content-Type', ''))
            encoding = params.get('charset', 'utf-8')
            html = urlopen(url).read().decode(encoding)    
            raw = nltk.clean_html(html) 

            path = os.path.realpath(__file__)
            path = path[0:len(path)-7]
            path += "//wynik"
            
            linie = raw.split('\n')

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
                    if (linie[i][0]!='\t' and linie[i][0]!=' '):
                        wynik += linie[i]

            while (wynik[0]==" " or wynik[0]=="\t"):
                wynik = wynik[1:len(wynik)]
                if (len(wynik)==0):
                    break

            if (len(wynik)>0):
                wynik = wynik[0:len(wynik)-1]

                linie[0] = linie[0].replace(" - Niewiarygodne.pl ","")
                linie[0] = linie[0].replace("?","")
                linie[0] = linie[0].replace("&amp;#8222;","")
                linie[0] = linie[0].replace("&quot;","")
                linie[0] = linie[0].replace("&amp;#8221;","")
                linie[0] = linie[0].replace(" - Media","")
                linie[0] = linie[0].replace("/","")

                if not linie[0].encode("utf-8") in self.art_db:
                    self.art_db[linie[0].encode("utf-8")] = wynik.encode("utf-8")
                    self.artnum = self.artnum + 1
                else:
                    print "Ten artykul juz istnieje (Kilka url do tego samego artykulu)" + '\n'

                '''
                if not os.path.exists(path):
                    os.makedirs(path)
                #filename = str(url[24:len(url)-5]) + ".txt"
                filename = linie[0] + ".txt"
                with codecs.open(os.path.join(path, filename), 'wb', "utf-8") as temp_file:
                    temp_file.write(wynik)
                '''
            else:
                print "CHECK! - " + url + "\n"

        ####################################################################
        links = self.get_links(url, soup)
        self.link_db[url.encode("utf-8")] = 1
        return links

    def crawl_one_level(self):

        wyn2 = list()
        for key in self.link_db.keys():
            key = key.decode("utf-8")
            if self.link_db[key.encode("utf-8")] == 0:
                wyn = self.crawl_one_page(key)
                for i in wyn:
                    wyn2.append(i)
        return set(wyn2)

    def crawl(self, depth):

        for i in range(0,depth):
            print "---- Crawl level: " + str(i+1) + " ----" + '\n'
            self.inject_urls(self.crawl_one_level())

    def inject_urls(self, urls):

        for url in urls:
            if not url.encode("utf-8") in self.link_db:
                self.link_db[url.encode("utf-8")] = 0

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
            if ("http://niewiarygodne.pl" in stri[i]):
                str2.append(stri[i])

        '''
        stri = list()
        for strona in soup.findAll('a'):
            if strona.has_attr('href'):
                if ("title" in strona['href']):
                    if strona['href'][0:4] == "http":
                        if ("http://niewiarygodne.pl" in strona['href']):
                            if ("wiadomosc" in strona['href']):
                                if ("title" in strona['href']):
                                    stri.append(strona['href'])
                    else:
                        if ("wiadomosc" in strona['href']):
                            if ("title" in strona['href']):
                                stri.append(urlparse.urljoin(page, strona['href']))

        str2 = list()
        for i in range(0,len(stri)):
            if stri[i].find('#') != -1:
                stri[i] = stri[i][0:stri[i].find('#')]
            if ("http://niewiarygodne.pl/kat" in stri[i]):
                if (",opage," not in stri[i]):
                    str2.append(stri[i])
       
                	if ("http://niewiarygodne.pl" in strona['href']):
                		if ("wiadomosc" in strona['href']):
    		                if strona['href'][0:4] == "http":
    		                    stri.append(strona['href'])
    		                else:
    		                    if urlparse.urljoin(page, strona['href'])[0:4] == "http":
    		                        stri.append(urlparse.urljoin(page, strona['href']))
                    else:
                        if ("/kat" in strona['href']):
                            if ("wiadomosc.html" in strona['href']):
                                if urlparse.urljoin(page, strona['href'])[0:4] == "http":
                                    stri.append(urlparse.urljoin(page, strona['href']))
        str2 = list()
        for strona in stri:
            if strona.find('\'') == -1:
                if strona.find('#') != -1:
                    strona = strona[0:strona.find('#')]
                str2.append(strona)
        '''
        return set(str2)


if __name__ == '__main__':
    NPL = niewiarygodneplCrawler("crawler.db")
    NPL.inject_urls(["http://niewiarygodne.pl"])
    NPL.crawl(100)