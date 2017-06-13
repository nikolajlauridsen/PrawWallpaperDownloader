"""
Class that handles database interaction
"""
import sqlite3 as lite
import time


class DbHandler:
    """Handles Database interaction"""

    def __init__(self):
        self.conn = lite.connect('wallpaper_base.db')
        self.c = self.conn.cursor()
        for qry in open('schema.sql', 'r').readlines():
            self.c.execute(qry)

    def insert_link(self, submission):
        """
        Insert a submission into the database takes a dict with:
        {"url": "link-to-image",
         "title": "title of the post",
         "author": "author name",
         "parent_id": INT if it's from an album this will be it's ID in the 
         database, otherwise this should be None}
        :param submission: dict in the above format
        """
        try:
            self.c.execute("INSERT INTO downloads VALUES (?, ?, ?, ?, ?, ?)",
                          (None,
                           int(time.time()),
                           submission["url"],
                           submission["title"],
                           submission["author"],
                           submission["parent_id"]))
        except lite.IntegrityError:
            # Will happen when running with nosort since the link
            # is already in the database
            pass

    def insert_album(self, album):
        """
        Insert an album into the database, requires a dictionary with:
        {"url": "link-to-imgur-album",
         "title": "post title",
         "author": "author name",
         "length": INT amount of posts}
        :param album: Dictionary
        """
        self.c.execute("INSERT INTO albums VALUES (?, ?, ?, ?, ?, ?)",
                       (None,
                        int(time.time()),
                        album["url"],
                        album["title"],
                        album["author"],
                        album["length"]))
        self.c.execute("SELECT last_insert_rowid()")
        return int(self.c.fetchone()[0])

    def get_posts(self, age_limit=None):
        """
        Return all posts downloaded as a list of context dictionaries
        in the format:
        {"id": INT id,)
         "date": INT unix time stamp,
         "url": "link-to-image"
         "title": "title of the post"}
        :return: List of dictionaries
        """
        if not age_limit:
            self.c.execute("SELECT * FROM downloads")
        else:
            self.c.execute("SELECT * FROM downloads WHERE "
                           "DATETIME(Download_date, 'unixepoch') >= "
                           "DATE('now', '-{} days')".format(age_limit))
        entries = self.c.fetchall()

        posts = []

        for entry in entries:
            context = {"id": entry[0],
                       "date": entry[1],
                       "url": entry[2],
                       "title": entry[3],
                       "author": entry[4],
                       "parent_id": entry[5]}
            posts.append(context)
        return posts

    def get_links(self, age_limit=None):
        """
        Return all links in the database
        :return: list of image links
        """
        if not age_limit:
            self.c.execute("SELECT Link FROM downloads")
        else:
            self.c.execute("SELECT Link FROM downloads WHERE "
                           "DATETIME(Download_date, 'unixepoch') >= "
                           "DATE('now', '-{} days')".format(age_limit))
        response = self.c.fetchall()
        return [link[0] for link in response]

    def get_albums_links(self):
        """
        Get all album links in the database
        :return: list of imgur album links
        """
        self.c.execute("SELECT Link FROM albums")
        return [link[0] for link in self.c.fetchall()]

    def sort_links(self, submissions, age_limit=None):
        """
        Sort out all previously downloaded links from a list of submissions
        :param submissions: list of links to be sorted
        :param age_limit: kwarg to determine max age of links to consider
        :return: list of sorted submissions, 
        and a list of discarded submissions
        """
        new_links = []
        old_links = self.get_links(age_limit=age_limit)
        skipped_list = []

        for submission in submissions:
            if submission["url"] not in old_links:
                new_links.append(submission)
            else:
                skipped_list.append(submission)
        return new_links, skipped_list

    def sort_albums(self, albums):
        """
        Sort out previously downloaded imgur albums from a list of imgur albums
        :param albums: list of imgur album links to be sorted 
        :return: list of sorted album links, and a list of discarded links
        """
        sorted_links = []
        old_links = self.get_albums_links()

        for album in albums:
            if album["url"] not in old_links:
                sorted_links.append(album)
            else:
                pass
        return sorted_links

    def save_changes(self):
        """Commit changes to the database"""
        self.conn.commit()
