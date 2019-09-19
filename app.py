#!/usr/bin/python
from lxml import etree as et
import argparse
import sqlite3
import datetime as d


class Book:
    connection = sqlite3.connect("booksLIb.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    def __init__(self, title, autor, read):
        self.title = title
        self.autor = autor
        self.read = read
        self.date = d.datetime.now().strftime("%y-%m-%d %H:%M:S")

    def store(self):
        self.cursor.execute('INSERT INTO BOOKS VALUES(?, ?, ?, ?, NULL)',
                            (self.title, self.autor, 0, self.date))
        print("Book(title = %s, autor = %s, read = %s was stored!)" % (self.title, self.autor, self.read))
        self.connection.commit()

    def update(self):
        row = self.cursor.execute('SELECT rowid, title, autor, isRead FROM BOOKS WHERE title = ? and autor = ?',
                                  (self.title, self.autor)).fetchone()
        rowid = tuple(row)[0]
        self.cursor.execute('UPDATE BOOKS SET isRead = ?, updated = ? where rowid = ?', (self.read, self.date, rowid))
        print("Book with title = \'%s\' and autor = \'%s\' was updated!" % (self.title, self.autor))
        self.connection.commit()

    @staticmethod
    def close():
        Book.connection.close()


parser = argparse.ArgumentParser()
parser.add_argument("--add", help="add books to library. Should point to xml file's location with books", type=str)
parser.add_argument("--update", help="update books in the library. Should point to xml file's location with books", type=str)
parser.add_argument("--print", help="get all stored books", nargs='?', const=True, type=bool)
parser.add_argument("--unload", help="unload all stored books", nargs='?', const=True, type=bool)
parser.add_argument("--read", help="get all stored books that were read", nargs='?', type=bool, const=True)
parser.add_argument("--unread", help="get all stored books that were unread", nargs='?', type=bool, const=True)
args = parser.parse_args()
conn = sqlite3.connect("booksLIb.db")


def readfromfile(location):
    books = []
    tree = et.parse(location)
    for elem in tree.getroot():
        title = elem.find('title').text
        autor = elem.find('autor').text
        read = int(elem.find('read').text) if (elem.find('read') is not None) else 0
        books.append(Book(title, autor, read))
    return books


def storeindb(books):
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    for book in books:
        c.execute("CREATE TABLE IF NOT EXISTS BOOKS (title text, autor text, isRead int, created text, updated text)")
        row = c.execute('SELECT rowid, title, autor, isRead FROM BOOKS WHERE title = ? and autor = ?',
                        (book.title, book.autor)).fetchone()
        if row is None:
            book.store()
        else:
            print('Book with title = \'%s\' and autor = \'%s\' already exists!' % (book.title, book.autor))
    Book.close()


def getallbooks():
    c = conn.cursor()
    for row in c.execute("SELECT rowid, * FROM BOOKS"):
        print(row)


def search(read):
    conn.row_factory = sqlite3.Row
    row = conn.execute("select title, autor from books where isRead = %s order by title" % read)
    for r in row.fetchall():
        print("\ttitle = %s, autor = %s" % (tuple(r)[0], tuple(r)[1]))


def unload():
    root = et.Element("books")
    c = conn.cursor()
    for row in c.execute("select title, autor, isRead from books order by title"):
        elem = tuple(row)
        bookElem = et.SubElement(root, "book")
        book = Book(elem[0], elem[1], elem[2])
        et.SubElement(bookElem, "title").text = book.title
        et.SubElement(bookElem, "autor").text = book.autor
        et.SubElement(bookElem, "read").text = str(book.read)
    tree = et.ElementTree(root)
    tree.write("storedBooks.xml", pretty_print=True, encoding='UTF-8')


if args.add:
    books = readfromfile(args.add)
    storeindb(books)
elif args.update:
    books = readfromfile(args.update)
    for book in books:
        book.update()
elif args.print:
    getallbooks()
elif args.read:
    search(1)
elif args.unread:
    search(0)
elif args.unload:
    unload()
