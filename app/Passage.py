from DBPManager import DBPManager
import Utils
from collections import OrderedDict

import scriptures

def passageKey(passage):
    return passage.score

class Passage:
    def __init__(self, reference, score=0):
        self.startRef = None
        self.endRef = None
        self.score = score
        try:
            if type(reference) == tuple:
                self.startBook = self.endBook = reference[0]
                self.startChapter = reference[1]
                self.endChapter = reference[3]
                self.startVerse = reference[2]
                self.endVerse = reference[4]
                self.reference = scriptures.reference_to_string(self.startBook, self.startChapter, self.startVerse, self.endChapter, self.endVerse)
            elif type(reference) == str:
                # This is assumed to be in OSIS reference format
                self.reference = reference
                refParts = reference.split('-')
                self.startRef = refParts[0]
                self.endRef = refParts[1] if len(refParts) > 1 else None
                startRefParts = self.startRef.split('.')
                self.startBook = startRefParts[0]
                self.startChapter = int(startRefParts[1])
                self.startVerse = int(startRefParts[2])
                if self.endRef == None:
                    self.endBook = self.startBook
                    self.endChapter = self.startChapter
                    self.endVerse = self.startVerse
                else:
                    endRefParts = self.endRef.split('.')
                    self.endBook = endRefParts[0]
                    self.endChapter = int(endRefParts[1])
                    self.endVerse = int(endRefParts[2])
        except Exception as e:
            print("Exception parsing passage " + str(reference) + ": " + str(e))
            self.clear()
            raise e

    def __eq__(self, other):
        if self.startRef == other.startRef and self.endRef == other.endRef and self.score == other.score and self.reference == other.reference:
            return True
        return False

    def __str__(self):
        return self.reference

    def __hash__(self):
        return hash(str(self))

    def includes(self, other):
        # Base case, if they are the same passage, then by definition, it is included
        if self == other:
            return True
        
        # Get the numerical order of each book (i.e. Genesis = 0, Exodus = 1, etc.)
        self_start_book_order = self.book_order(self.startBook)
        self_end_book_order = self.book_order(self.endBook)
        other_start_book_order = self.book_order(other.startBook)
        other_end_book_order = self.book_order(other.endBook)

        # We're going to determine if this passage starts before and ends after the given passage, which means the given passage is
        # included within it 
        starts_before = False
        ends_after = False

        if self_start_book_order < other_start_book_order:
            starts_before = True
        elif self_start_book_order == other_start_book_order:
            if self.startChapter < other.startChapter:
                starts_before = True
            elif self.startChapter == other.startChapter:
                if self.startVerse <= other.startVerse:
                    starts_before = True

        if self_end_book_order > other_end_book_order:
            ends_after = True
        elif self_end_book_order == other_end_book_order:
            if self.endChapter > other.endChapter:
                ends_after = True
            elif self.endChapter == other.endChapter:
                if self.endVerse >= other.endVerse:
                    ends_after = True

        # If this passage both starts before and ends after the given one, then it includes it
        return starts_before and ends_after  

    def text(self):
        dbp = DBPManager("ENG","ESV")
        (text, _) = dbp.passage(self.startBook, self.startChapter, self.endChapter, self.startVerse, self.endVerse)
        return text

    def ref_osis(self):
        book_start = scriptures.references.get_book(self.startBook)
        book_end = scriptures.references.get_book(self.endBook)
        osis = ""
        if book_start is not None:
            osis = book_start[1] + "." + str(self.startChapter) + "." + str(self.startVerse)
            # If there is only 1 verse, this is sufficient, otherwise add the next part of the reference
            if not (self.endBook == self.startBook and self.endChapter == self.startChapter and self.endVerse == self.startVerse) and book_end is not None:
                osis = osis + "-" + book_end[1] + "." + str(self.endChapter) + "." + str(self.endVerse)
        return osis

    def data(self):
        return {"reference":self.reference, "start":self.startRef, "end":self.endRef, "score":self.score}

    def ref_data(self):
        return {
            "osis-reference" : self.ref_osis(),
            "reference" : scriptures.reference_to_string(self.startBook, self.startChapter, self.startVerse, self.endChapter, self.endVerse),
            "book-start" : self.startBook,
            "chapter-start" : self.startChapter,
            "verse-start" : self.startVerse,
            "book-end" : self.endBook,
			"chapter-end" : self.endChapter,
			"verse-end" : self.endVerse
            }

    def book_order(self, book):
        index = 0
        # ordered_books = OrderedDict(scriptures.references.pcanon.books)
        for key in scriptures.references.pcanon.books:
            book_entry = scriptures.references.pcanon.books[key]
            # Compare to the full name (index 0) and abbreviation (index 1)
            if book == book_entry[0] or book == book_entry[1]:
                return index
            index = index + 1
        return -1

    def clear(self):
        # Clear fields except string reference itself
        self.startBook = self.endBook = None
        self.startChapter = self.endChapter = None
        self.startVerse = self.endVerse = None