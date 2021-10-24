import requests

KEY = "8dc9f107280d9cde68b5069dd496d363"

class DBPManager:
    def __init__(self, lang, version):
        self.lang = lang
        self.version = version

    def stdParams(self):
        params = { "v"   : 2,
                   "key" : KEY
                 }
        return params

    def passage(self, book, chapter_start = 1, chapter_finish = None, verse_start = None, verse_finish = None):
        # Calculate the dam id based on which book of the Bible this is
        (damid, book) = self.calcDamId(book)
        if damid is None:
            print("Error: Cannot calculate DAM ID")
            return None

        # Find what the last chapter in this book is
        if chapter_finish is None:
            parameters = {"dam_id" : damid, "book_id" : book}
            parameters.update(self.stdParams())
            response = requests.get("http://dbt.io/library/chapter", params=parameters)
            if response.status_code == 200:
                chapter_info = response.json()
                chapter_finish = int(chapter_info[-1]["chapter_id"])

        if verse_start is None:
            verse_start = 1
        if verse_finish is None:
            verse_finish = self.last_verse_num_in_chapter(damid, book, chapter_finish)

        chapter_num = chapter_start
        text = ""
        book_list = []
        # For each chapter, get all verses needed
        while chapter_num <= chapter_finish:
            verse_begin = 1
            verse_end = -1
            if chapter_num == chapter_start:
                verse_begin = verse_start
            if chapter_num == chapter_finish:
                verse_end = verse_finish

            # If we're getting a whole book or the remainder of a book
            if chapter_num >= chapter_start and chapter_num < chapter_finish:
                verse_end = self.last_verse_num_in_chapter(damid, book, chapter_num)
            
            # Query for the actual verses in this book
            parameters = { "dam_id"      : damid,
                           "book_id"     : book ,
                           "chapter_id"  : chapter_num,
                           "verse_start" : verse_begin,
                           "verse_end"   : verse_end
                         }
            parameters.update(self.stdParams())
            response = requests.get("http://dbt.io/text/verse", params=parameters)

            # If the query was successful, get all the verse text together
            chapter_text = ""
            chapter_list = []
            if response.status_code == 200:
                verse_info = response.json()
                for verse in verse_info:
                    verse_text = verse["verse_text"].strip()
                    chapter_text += verse_text + " "
                    chapter_list.append(verse_text)
            
            # Add the chapter text to the whole
            text += chapter_text
            book_list.append(chapter_list)
            
            # Go to next chapter
            chapter_num += 1

        return (text.strip(), book_list)

    def calcDamId(self, book):
        damId = self.lang + self.version
        damIdOT = damId + "O2ET"
        # check if the book is in the OT
        parameters = {"dam_id" : damIdOT}
        parameters.update(self.stdParams())
        responseOT = requests.get("http://dbt.io/library/bookorder", params=parameters)
        if responseOT.status_code == 200:
            books = responseOT.json()
            for book_item in books:
                book_id = book_item["book_id"]
                book_name = book_item["book_name"]
                if book_id == book or book_name == book:
                    return (damIdOT, book_id)
        # not there, must be in the NT (but let's check anyway)
        damIdNT = damId + "N2ET"
        parameters = {"dam_id" : damIdNT}
        parameters.update(self.stdParams())
        responseNT = requests.get("http://dbt.io/library/bookorder", params=parameters)
        if responseNT.status_code == 200:
            books = responseNT.json()
            for book_item in books:
                book_id = book_item["book_id"]
                book_name = book_item["book_name"]
                if book_id == book or book_name == book:
                    return (damIdNT, book_id)
        
        # if get here, something went wrong
        return None
    
    def last_verse_num_in_chapter(self, damid, book, chapter):
        parameters = {"dam_id" : damid, "book_id" : book, "chapter_id" : chapter}
        parameters.update(self.stdParams())
        verse = None
        response = requests.get("http://dbt.io/library/verseinfo", params=parameters)
        if response.status_code == 200:
            verse_info = response.json()
            chapter_info = verse_info[book]
            verses = chapter_info[str(chapter)]
            verse = int(verses[-1])
        return verse