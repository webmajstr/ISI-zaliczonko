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

j = 1
for filename in glob.iglob(os.path.join('*.txt')):
    with open(filename) as f:
        #print (f.name)
        j = j + 1
j = 1

for filename in glob.iglob(os.path.join('*.txt')):
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        lines = f.read()
        doc = etree.SubElement(page, 'doc')
    
        field1 = etree.SubElement(doc, 'field', name='id')
        field1.text = '{0}'.format(j)
    
        field2 = etree.SubElement(doc, 'field', name='title')
        filename = os.path.splitext(f.name)[0]
        field2.text = '{0}'.format(filename)
    
        field3 = etree.SubElement(doc, 'field', name='datawydarzenia')
        date = re.findall(r'\b(?:w|roku|przed|po)\s\d{4}|\d{4}\s?r|\d{1,2}\s(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)', lines)
        removeduplicates = list(OrderedDict.fromkeys(date))
        printdate = ', '.join(removeduplicates)
        field3.text = '{0}'.format(printdate)
    
        field4 = etree.SubElement(doc, 'field', name='miejsce')
        place = re.findall(r'\s(?:w|obok|przed|na\sterenie|na|w\spółnocnej|w\społudniowej|W|Obok|Przed|Na\sterenie|W\spółnocnej|W\społudniowej|do)\s[A-ZĄĘŚĆŻŹŁÓĆŃ][a-ząęśćżźłóćń]+(?:\s[A-ZĄĘŚĆŻŹŁÓĆŃ][a-ząęśćżźłóćń]+)?', lines)
        removeduplicates1 = list(OrderedDict.fromkeys(place))
        printplace = ','.join(removeduplicates1)
        clearspaces = printplace.strip()
        field4.text = '{0}'.format(clearspaces)
    
        field5 = etree.SubElement(doc, 'field', name='description')
        clearedtxt = lines.replace('\r', '')
        removech = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', clearedtxt)
        field5.text = '%s' % re.sub('\t+', ' ', removech)
        
        f.close()
        j = j + 1

#Zapis do pliku
outFile = open('baza.xml', 'wb')
outFile.write(etree.tostring(
    page, pretty_print=True, xml_declaration=True, encoding='utf-8')
                )
outFile.close()
print ('Zakończono')
