#!/usr/bin/python
import xml.etree.ElementTree as eT
import argparse
import sqlite3
import datetime as d
import logging


class Book:
    def __init__(self, title, autor, read):
        self.title = title
        self.autor = autor
        self.read = read


parser = argparse.ArgumentParser()
parser.add_argument("--add", help="add books to library. Should point to xml file's location with books", type=str)
parser.add_argument("--getAll", help="get all stored books", type=bool)
parser.add_argument("--getRead", help="get all stored books that were reading", type=str)
args = parser.parse_args()
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
conn = sqlite3.connect("booksLIb.db")


def readfromfile(location):
    books = []
    tree = eT.parse(location)
    for elem in tree.getroot():
        title = elem.find('title').text
        autor = elem.find('autor').text
        read = int(elem.find('read').text) if (elem.find('read') is not None) else 0
        books.append(Book(title, autor, read))
    storeindb(books)


def storeindb(books):
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    for book in books:
        date = d.datetime.now().strftime("%y-%m-%d %H:%M:S")
        c.execute("CREATE TABLE IF NOT EXISTS BOOKS (title text, autor text, isRead int, created text, updated text)")
        row = c.execute('SELECT rowid, title, autor, isRead FROM BOOKS WHERE title = ? and autor = ?',
                        (book.title, book.autor)).fetchone()
        if len(row) > 0:
            result = tuple(row)
            if result[3] == book.read:
                print('Book with title = \'%s\' and autor = \'%s\' and isRead = %s already exists!' % (book.title, book.autor, book.read))
            else:
                c.execute('UPDATE BOOKS SET isRead = ? where rowid = ?', (book.read, result[0]))
                print("Book with title = \'%s\' and autor = \'%s\' was updated!" % (book.title, book.autor))
        else:
            c.execute('INSERT INTO BOOKS VALUES(?, ?, ?, ?, NULL)',
                      (book.title, book.autor, 0, date))
            print("Book(title = %s, autor = %s, read = %s was stored!)" % (book.title, book.autor, book.read))
    conn.commit()
    conn.close()


def getallbooks():
    c = conn.cursor()
    for row in c.execute("SELECT rowid, * FROM BOOKS"):
        logger.debug(row)
        print(row)


def search(read):
    conn.row_factory = sqlite3.Row
    row = conn.execute("select title, autor from books where isRead = %s" % read)
    for r in row.fetchall():
        print("\ttitle = %s, autor = %s" % (tuple(r)[0], tuple(r)[1]))


if args.add:
    readfromfile(args.add)
if args.getAll:
    getallbooks()
if args.getRead:
    if args.getRead == 'true':
        search(1)
    elif args.getRead == 'false':
        search(0)
