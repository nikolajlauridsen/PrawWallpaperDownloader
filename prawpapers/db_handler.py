"""
Class that handles database interaction
"""
import sqlite3 as lite


class DbHandler:
    """Handles Database interaction"""

    def __init__(self):
        self.conn = lite.connect('wallpaper_base.db')
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS downloads "
                       "(Date TEXT, Link TEXT PRIMARY KEY, Title TEXT)")
        self.c.execute("CREATE TABLE IF NOT EXISTS albums "
                       "(Link TEXT, Title TEXT)")

    def insert_link(self, submission):
        """Insert a link into the database"""
        try:
            self.c.execute("INSERT INTO downloads VALUES (?,?,?)",
                          (submission["date"],
                           submission["url"],
                           submission["title"]))
        except lite.IntegrityError:
            # Wil happend when running with nosort since the link
            # is in the databse
            pass

    def insert_album(self, album):
        """Insert an album into the database"""
        self.c.execute("INSERT INTO albums VALUES (?,?)",
                       (album["url"],
                        album["title"]))

    def get_posts(self):
        """Return all posts downloaded as a list of context dictionaries"""
        self.c.execute("SELECT * FROM downloads")
        entries = self.c.fetchall()
        posts = []

        for entry in entries:
            context = {"date": entry[0],
                       "url": entry[1],
                       "title": entry[2]}
            posts.append(context)
        return posts

    def get_links(self):
        """Return all links as a list"""
        self.c.execute("SELECT Link FROM downloads")
        links = self.c.fetchall()
        return links

    def get_albums_links(self):
        self.c.execute("SELECT Link FROM albums")
        links = self.c.fetchall()
        return links

    def sort_links(self, submissions):
        """Sort out all previously downloaded links from a list of links"""
        new_links = []
        old_links = []
        skipped_list = []

        for link in self.get_links():
            old_links.append(link[0])

        for submission in submissions:
            if submission["url"] not in old_links:
                new_links.append(submission)
            else:
                skipped_list.append(submission)
        return new_links, skipped_list

    def sort_albums(self, albums):
        sorted_links = []
        old_links = []

        for link in self.get_albums_links():
            old_links.append(link[0])

        for album in albums:
            if album["url"] not in old_links:
                sorted_links.append(album)
            else:
                pass
        return sorted_links

    def save_changes(self):
        """Commit changes to the database"""
        self.conn.commit()
