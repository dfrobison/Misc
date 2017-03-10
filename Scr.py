import urllib.request
import urllib.error
import re
import datetime
import decimal
import sys
from bs4 import BeautifulSoup
import json

class Verse:
    def __init__(self, number, text):
        self.number = number
        self.text = text

    def __str__(self):
        return (repr(self.number) + "  " + self.text)

class Chapter:
    def __init__(self, number, numberOfVerses, link):
        self.number = number
        self.numberOfVerses = 0
        self.link = link
        self.verses = []

    def __str__(self):
        return (repr(self.number) + "  " + self.link)

class Book:
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.chapters = []

    def __str__(self):
        return (self.name + "  " + self.link)


class Scripture:
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.books = []

    def download(self):
        request = urllib.request.Request(self.link)
        request.add_header(
            'User-Agent',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        )

        data = urllib.request.urlopen(request)
        soup = BeautifulSoup(data.read().decode('utf-8'), 'html.parser')
        toc = soup.select('.table-of-contents .books a')

        if len(toc) == 0: #No books--just chapters
            bookName = self.name if 'Doctrine' not in self.name else 'D&C'
            self.books.append(Book(bookName, self.link))
        else:
            # Retrieve all books
            for t in toc:
                if 'Facsimile' not in t.text:
                    self.books.append(Book(t.text, t['href']))

        # Retrieve all chapters for each book
        for b in self.books:
            request = urllib.request.Request(b.link)
            request.add_header(
                'User-Agent',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
            )

            data = urllib.request.urlopen(request)
            soup = BeautifulSoup(data.read().decode('utf-8'), 'html.parser')
            chapters = soup.select('.jump-to-chapter a')

            if len(chapters) > 0:
                for c in chapters:
                    b.chapters.append(Chapter(int(c.text), 0, c['href']))
            else:
                b.chapters.append(Chapter(1, 0, b.link))

        validateText = re.compile('[^0-9A-Za-z .,;?:()‘!\[\]\-\'’\u00E6\u00C6\u2014\u2026\u201D\u201C\u0027\u2013]+')

        #Retrieve all verses for each book and chapter
        for b in self.books:
            for c in b.chapters:
                request = urllib.request.Request(c.link)
                request.add_header(
                    'User-Agent',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
                )

                print("Requesting: " + c.link)

                data = urllib.request.urlopen(request)
                soup = BeautifulSoup(data.read().decode('utf-8'), 'html.parser')
                verses = soup.select('.verses p[class=""]')
                c.numberOfVerses = len( verses)

                for v in verses:
                    markers = v.select('.studyNoteMarker')

                    for m in markers:
                        m.decompose()

                    verse = v.select('.verse')

                    verseNumber = verse[0].text  if len(verse) > 0 else 1

                    for u in verse:
                        u.decompose()

                    # Clean up the text
                    finalVerseText = v.text.replace('\xa0', '').replace('¶', '').replace('*', '')

                    # Validate that all the characters are valid
                    match = validateText.findall(finalVerseText)

                    if match:
                        print(match)
                        print(verseNumber)
                        #sys.exit("aa! errors!")
                    c.verses.append(Verse(int(verseNumber), finalVerseText))


class Scriptures:
    def __init__(self):
        self.volumes = []

    def download(self):

        for v in self.volumes:
            v.download()

        with open('scriptures.json', 'w') as outfile:
            json.dump(self, outfile, default=jsonDefault)



def jsonDefault(object):
    return object.__dict__

scriptures = Scriptures()
scriptures.volumes.append(Scripture('Old Testament',  'https://www.lds.org/scriptures/ot'))
scriptures.volumes.append(Scripture('New Testament',  'https://www.lds.org/scriptures/nt'))
scriptures.volumes.append(Scripture('Book of Mormon',  'https://www.lds.org/scriptures/bofm'))
scriptures.volumes.append(Scripture('Doctrine and Covenants',  'https://www.lds.org/scriptures/dc-testament/dc'))
scriptures.volumes.append(Scripture('Pearl of Great Price',  'https://www.lds.org/scriptures/pgp'))

scriptures.download()

#volume = 'New Testament'
#link = 'https://www.lds.org/scriptures/nt'
#fileName = 'nt.json'

#volume = 'Pearl of Great Price'
#link = 'https://www.lds.org/scriptures/pgp'
#fileName = 'pgp.json'

#volume = 'Old Testament'
#link = 'https://www.lds.org/scriptures/ot'
#fileName = 'ot.json'

#volume = 'Book of Mormon'
#link = 'https://www.lds.org/scriptures/bofm?lang=eng'
#fileName = 'bofm.json'

#volume = 'Doctrine and Covenants'
#link = 'https://www.lds.org/scriptures/dc-testament/dc?lang=eng'
#fileName = 'dc.json'

#doc = Scripture(volume, link)
#doc.download(fileName)
