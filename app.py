import xml.etree.ElementTree as eT

tree = eT.parse('books.xml')
for elem in tree.getroot():
    for subElem in elem:
        print(subElem.tag, subElem.text)
