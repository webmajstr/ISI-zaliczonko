# -*- coding: utf-8 -*-

"""
Skrypt tworzący plik XML na podstawie treści
artykułów...
"""
import os
import codecs
import re
import glob
from lxml import etree
from collections import OrderedDict

page = etree.Element("add")
#doc = etree.ElementTree(page)

#str = 'Today is 2012-MAY-31'
#date = re.search(r'\d\d\d\d-[A-Z][A-Z][A-Z]-\d\d', lines)

j = 1
for filename in glob.iglob(os.path.join(u'*.txt')):
    with open(filename) as f:
        print f.name
        j = j + 1
j = 1

for filename in glob.iglob(os.path.join(u'*.txt')):
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        lines = f.read()
        doc = etree.SubElement(page, 'doc')
    
        field1 = etree.SubElement(doc, 'field', name='id')
        field1.text = u'{0}'.format(j)
    
        field2 = etree.SubElement(doc, 'field', name='title')
        filename = os.path.splitext(f.name)[0]
        field2.text = u'{0}'.format(filename)
    
        field3 = etree.SubElement(doc, 'field', name='datawydarzenia')
        date = re.findall(r'roku?\s\d{4}|\d{4}\s?r|\d{1,2}\sstycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia\s', lines)
        removeduplicates = list(OrderedDict.fromkeys(date))
        printdate = ', '.join(removeduplicates)
        field3.text = '{0}'.format(printdate)
    
        field4 = etree.SubElement(doc, 'field', name='miejsce')
        field4.text = ''
    
        field5 = etree.SubElement(doc, 'field', name='description')
        clearedtxt = lines.replace('\r', '')
        field5.text = '%s' % re.sub('\t+', ' ', clearedtxt)
        
        f.close()
        j = j + 1

#Zapis do pliku
outFile = open('baza.xml', 'w')
outFile.write(etree.tostring(
    page, pretty_print=True, xml_declaration=True, encoding='utf-8')
              )
outFile.close()
print u"Zakończono..."

