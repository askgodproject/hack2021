import json
import requests
import os

# API key is expected to be set as an environment variable. It is only available for project members
# Please contact project admin if you don't have it
KEY = os.environ["DBP_KEY"]

API_HOST = "https://4.dbt.io/api"

class APIException(Exception): ...
class ValidityException(Exception): ...

class DBPManager:
    def __init__(self, lang : str, version : str):
        """
        Parameters
        ----------
        lang : str
            The ISO language code to use for the Bible content retrieved; should be 3 characters long
        version : str
            The translation/version code to use for the Bible content retrieved; should be 3 characters long
        
        Raises
        ------
        ValidityException if either the language or version given are invalid, or there was an error validating them

        Example
        -------
        DBPManager("ENG", "ESV")
            This creates a manager for the English Standard Version in English  
        """

        try:
            if self.verify_language(lang):
                self.lang = lang
        except APIException as e:
            raise ValidityException("Could not find language id " + lang + " in supported list. Please check language ISO code. " + e)

        try:
            if self.verify_version(version):
                self.version = version
        except APIException as e:
            raise ValidityException("Could not find translation/vbersion " + version + " for language " + self.lang + ". " + e)

    def std_params(self):
        """
        Returns the parameter values that must be included in every call to the DBP API
        
        Returns
        -------
        dict
            Object with the necessary API request parameters
        """

        params = { "v"   : 4,
                   "key" : KEY
                 }
        return params

    def verify_language(self, lang : str):
        """
        Verifies that the given language code is one for which the DBP has content

        Parameters
        ----------
        lang : str
            ISO language id to verify
        
        Raises
        ------
        APIException if calling the applicable endpoint(s) returns a failing status code, or the returned format is unexepcted

        Returns
        -------
        True if content for the given language can be found on the DBP, False otherwise
        """

        max_page = -1
        page = 1
        while page <= max_page or max_page == -1:
            parameters = {"limit": 150, "page": page}
            parameters.update(self.std_params())
            response = requests.get(os.path.join(API_HOST, "languages"), params=parameters)
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    lang_data = response_json["data"]
                    meta_data = response_json["meta"]
                    # The first time we query the endpoint, we should get the total number of pages
                    if max_page == -1:
                        max_page = meta_data["pagination"]["total_pages"]

                    # Go through each language and see if the ISO codes match
                    for language in lang_data:
                        if language["iso"] == lang.lower():
                            return True

                    # If we get here, the language id was not found yet, so go to the next page
                    page += 1
                except Exception as e:
                    raise APIException("Error: Response to " + response.url + " has unexpected format: " + json.dumps(response.json()) + " | " + e)
            else:
                raise APIException("Error: " + response.status_code + " when retrieving languages with " + response.url)
        # If we end up here then we never found the ISO code
        return False

    def verify_version(self, version : str):
        """
        Verifies that there is content in the expected language for the given translation/version identifier.
        This assumes that the language for this manager has already been verified

        Parameters
        ----------
        version : str
            The translation/version identifier to verify
        
        Raises
        ------
        APIException if calling the applicable endpoint(s) returns a failing status code, or the returned format is unexepcted

        Returns
        -------
        True if a filesetID can be found that combines the expected language and the given version, False otherwise
        """

        max_page = -1
        page = 1
        fileset_id = self.lang + version
        while page <= max_page or max_page == -1:
            parameters = {"language_code": self.lang, "media": "text_plain", "limit": 150, "page": page}
            parameters.update(self.std_params())
            response = requests.get(os.path.join(API_HOST, "bibles"), params=parameters)
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    versions_data = response_json["data"]
                    meta_data = response_json["meta"]
                    # The first time we query the endpoint, we should get the total number of pages
                    if max_page == -1:
                        max_page = meta_data["pagination"]["last_page"]

                    # Go through each Bible and its variants, looking for a filesetID that matches our expected one
                    # Since we're only asking for plain text there will probably just be one variant for each Bible
                    for version in versions_data:
                        # There is also "dbp-vid", but that's only for video, so it won't be here cause we're only asking for text
                        variants_data = version["filesets"]["dbp-prod"]
                        for variant in variants_data:
                            if variant["id"] == fileset_id:
                                return True

                    # If we get here, the filesetID was not found yet, so go to the next page
                    page += 1
                except Exception as e:
                    raise APIException("Error: Response to " + response.url + " has unexpected format: " + json.dumps(response.json()) + " | " + e)
            else:
                raise APIException("Error: " + response.status_code + " when retrieving versions with " + response.url)
        # If we end up here then we never found the filesetID
        return False

    def get_book_info(self, fileset_id, book):
        """
        Queries the API for the given book in the given filesetID, and returns the associated data.
        This data contains the following kind of information about the book:
            - Full and abbreviated names
            - Which Testament it is included in
            - How many chapters there are
            - For each chapter, how many verses it holds
            - Order and Group among all Biblical books

        Parameters
        ----------
        fileset_id : str
            The identifier for the Bible to look in
        book : str
            Full or abbreviated name of the book

        Raises
        ------
        APIException if calling the applicable endpoint(s) returns a failing status code, or the returned format is unexepcted

        Returns
        -------
        dict
            Object containing information about the number of chapters, verses, and the location of this book in the Bible
        """

        parameters = {"book_id" : book, "verify_content": True, "verse_count": True}
        parameters.update(self.std_params())
        response = requests.get(os.path.join(API_HOST, fileset_id, "book"), params=parameters)
        if response.status_code == 200:
            try:
                return response.json()["data"][0]
            except Exception as e:
                raise APIException("Error: Response to " + response.url + " has unexpected format: " + json.dumps(response.json()) + " | " + e)
        else:
            raise APIException("Error: " + response.status_code + " when retrieving book info with " + response.url)

    def passage(self, book, chapter_start = 1, chapter_finish = None, verse_start = None, verse_finish = None):
        """
        The main workhorse of the DBPManager. Retrieves the text of the given passage.
        A passage can be any length of content within a single book.
        For instance: a single verse, a range of verses in a chapter, a whole chapter, part of one chapter and part of the next, etc., up to
        the entire book.

        Parameters
        ----------
        `book` : `str`
            The name (either full or abbreviated) of the book containing the passage
        `chapter_start` : `int`
            The chapter of the book in which the passage begins
        `chapter_finish` : `int`
            The chapter of the book in which the passage ends
        `verse_start` : `int`
            The verse within the starting chapter ('chapter_start') where the passage begins
        `verse_end` : `int`
            The verse within the ending chapter ('chapter_finish') where the passage ends

        Returns
        -------
        `tuple` : `(str, [])`
            A tuple containing:
                - The entire text of the passage, concatenated together with a single space between verses
                - The entire text of the passage, organized in a 2D array organized like [chapter number][verse number]

        Examples
        --------
        - `passage("JHN", 3, 3, 16, 16)` and passage("John", 3, 3, 16, 16) both return the text of John 3:16
        - `passage("John", 3, 3, 16, 18)` returns the text of John 3:16-18
        - `passage("John", 3, 4, 16, 18)` returns the text of John 3:16 - John 4:18 (John 3:16-4:18)
        - `passage("John", 3, verse_start=16, 18)` and passage("John", 3, 21, 16, 18) both return the text of John 3:16 - John 21:18
        - `passage("John", 3, verse_start=16)` returns the text of John 3:16 - John 21:25 (the end of the book)
        - `passage("John", 3, 3)` returns the whole text of John chapter 3
        - `passage("John", 3)` returns the whole text of John 3-21 (chapters 3 through 21)
        - `passage("John")` returns the whole text of John (the entire book)
        """

        text = ""
        book_list = []
        book_info = None

        # Internal helper function to return the last verse of a given chapter in the retrieved book data
        def last_verse_in_chapter(chapter : int) -> int:
            return book_info["verses_count"][chapter - 1]["verses"]

        try:
            # FilesetID for text-only content is just the language id with the translation appended
            fileset_id = self.lang + self.version

            # Find the last chapter in this book if necessary
            if chapter_finish is None:
                book_info = self.get_book_info(fileset_id, book)
                chapter_finish = len(self.book_info["chapters"])

            # The first verse of the first chapter and the last verse of the last chapter
            if verse_start is None:
                verse_start = 1
            if verse_finish is None:
                if book_info is None:
                    book_info = self.get_book_info(fileset_id, book)
                verse_finish = last_verse_in_chapter(chapter_finish)

            chapter_num = chapter_start
            # For each chapter, get all verses needed
            while chapter_num <= chapter_finish:
                # Determine the beginning and ending verses in this particular chapter
                verse_begin = 1
                verse_end = -1
                if chapter_num == chapter_start:
                    verse_begin = verse_start
                if chapter_num == chapter_finish:
                    verse_end = verse_finish

                # If we're getting a whole book or the remainder of a book
                if chapter_num >= chapter_start and chapter_num < chapter_finish:
                    if book_info is None:
                        book_info = self.get_book_info(fileset_id, book)
                    verse_end = last_verse_in_chapter(chapter_num)
                
                # Query for the actual verse(s) in this chapter and verse range
                parameters = {"verse_start" : verse_begin, "verse_end" : verse_end}
                parameters.update(self.std_params())
                response = requests.get(os.path.join(API_HOST, "bibles/filesets", fileset_id, book, str(chapter_num)), params=parameters)

                # If the query was successful, get all the verse text together
                chapter_text = ""
                chapter_list = []
                if response.status_code == 200:
                    try:
                        verses_info = response.json()["data"]
                        for verse in verses_info:
                            verse_text = verse["verse_text"].strip()
                            chapter_text += verse_text + " "
                            chapter_list.append(verse_text)
                    except Exception as e:
                        raise APIException("Error: Response to " + response.url + " has unexpected format: " + json.dumps(response.json()) + " | " + e)
                else:
                    raise APIException("Error: " + response.status_code + " when retrieving verses with " + response.url)
                
                # Add the chapter text to the whole
                text += chapter_text
                book_list.append(chapter_list)
                
                # Go to next chapter
                chapter_num += 1
        except Exception as e:
            # Rethrow the exception
            raise e

        # Return the whole text of the passage, as well as the array containing the same text
        return (text.strip(), book_list)
