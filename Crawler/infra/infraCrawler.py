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
import difflib
from urllib import urlopen
from bs4 import BeautifulSoup

class infraCrawler(object):

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

    def getend(self,stri):
        wyn = [m.start() for m in re.finditer("/",stri)]
        stri = stri[wyn[-1]+1:len(stri)]
        return stri

    def is_article(self, url):
        if ("http://www.infra.org.pl/" not in url):
            return False
        konc = self.getend(url)
        wyn = [m.start() for m in re.finditer("\d+-",konc)]
        if (len(wyn)==0):
            return False
        if (wyn[0]!=0):
            return False
        return True

    def is_category(self, url):
        if ("http://www.infra.org.pl" not in url):
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

    def similar(self,seq1,seq2):
        return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.75

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
        
        _, params = cgi.parse_header(urlobject.headers.get('Content-Type', ''))
        encoding = params.get('charset', 'utf-8')
        html = urlcontent.decode(encoding,errors='ignore')    
        raw = nltk.clean_html(html) 
            
        h = HTMLParser.HTMLParser()
        raw = h.unescape(raw)
        if (self.is_article(url)==True):
            ####################################################################

            linie = re.split('\n|\t',raw)

            linie[0] = linie[0].replace("?","")
            linie[0] = linie[0].replace("/","")

            title = self.clear_line(linie[0])

            page = 0
            wynik = ""
            for i in range (1,len(linie)):
                wyn = [m.start() for m in re.finditer(".*, \d\d .* \d\d\d\d \d\d:\d\d",linie[i])]
                if (len(wyn)>0):
                    page = i+1
                    break

            if (page==0):
                print "ERROR 1"

            autor = False
            data = False

            for i in range (page,len(linie)-1):
                if (len(linie[i])>10):
                    if ("____________________" in linie[i]):
                        autor = True
                        continue
                    if ("INFRA" in linie[i]):
                        continue
                    if ("Zobacz tak" in linie[i]):
                        break

                    if (autor==True):
                        autor = False
                        continue
                    if (len(linie[i])>=10):
                        if (linie[i][0]=='\t'):
                            continue
                        if ((linie[i][0]!=' ') or (linie[i][0]==' ' and linie[i][1]!=' ') or (linie[i][0]==' ' and linie[i][1]==' ' and linie[i][2]!=' ')):
                            if (wynik==""):
                                if (data==False):
                                    data = True
                                    continue
                                wynik += self.clear_line(linie[i])
                            else:
                                wynik += '\n' + self.clear_line(linie[i])

            if not linie[0].encode("utf-8") in self.art_db:
                if (len(wynik)>0):
                    self.artnum = self.artnum + 1
                    self.art_db[linie[0].encode("utf-8")] = wynik.encode("utf-8")
                    print "Nowy (" + str(self.artnum) + "): " + url + '\n'
                else:
                    print "CHECK! - " + url + "\n"

        ####################################################################
        links = self.get_links(url, html)
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

    def inject_urls(self, start="http://www.infra.org.pl/"):

        if (len(self.link_db.keys())==0):
            self.link_db[start.encode("utf-8")] = 0

        for url in self.tmp_db.keys():
            if not url in self.link_db:
                self.link_db[url] = 0

        self.tmp_db.clear()

    def is_html(self, urlobject):

        return urlobject.info().gettype() == "text/html"

    def get_links(self, page, soup):

        regex = 'href="(.*?)"'
        wyn = re.findall(regex,soup)

        wynik = list()
        for i in range(0,len(wyn)):
            if wyn[i][0:4] == "http":
                wynik.append(wyn[i])
            else:
                wynik.append(urlparse.urljoin("http://www.infra.org.pl",wyn[i]))

        str2 = list()
        for i in range(0,len(wynik)):
            if wynik[i].find('#') != -1:
                wynik[i] = wynik[i][0:wynik[i].find('#')]
            if (self.is_article(wynik[i])==True or self.is_category(wynik[i])==True):
                str2.append(wynik[i])
        
        return set(str2)


if __name__ == '__main__':
    NPL = infraCrawler()
    NPL.inject_urls()
    NPL.crawl(100)