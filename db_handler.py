"""
Class that handles database interaction
"""
import sqlite3 as lite


class Db_handler():
    """Handles Database interaction"""

    def __init__(self):
        self.conn = lite.connect('wallpaper_base.db')
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS downloads (Date TEXT, Link TEXT PRIMARY KEY, Title TEXT)")

    # Insert a link into the database
    def insert_link(self, submission):
        self.c.execute("INSERT INTO downloads VALUES (?,?,?)",
                       (submission["date"],
                        submission["url"],
                        submission["title"]))

    # Return all posts downloaded as a list of dictionaries
    def get_posts(self):
        self.c.execute("SELECT * FROM downloads")
        entries = self.c.fetchall()
        posts = []

        for entry in entries:
            context = {"date": entry[0],
                       "url": entry[1],
                       "title": entry[2]}
            posts.append(context)
        return posts

    # Returns all links as a list
    def get_links(self):
        self.c.execute("SELECT Link FROM downloads")
        links = self.c.fetchall()
        return links

    # Removes all downloaded links from a list of links
    def check_links(self, submissions):
        new_links = []
        old_links = []
        skipped_list = []

        for link in self.get_links():
            old_links.append(link[0])

        for submission in submissions:
            if submission["url"] not in old_links:
                new_links.append(submission)
            else:
                try:
                    print(submission["title"] + " has already been downloaded")
                except UnicodeEncodeError:
                    print(submission["url"] + " has already been downloaded")
                skipped_list.append(submission)
        return new_links, skipped_list

    # Commit changes to the database
    def save_changes(self):
        self.conn.commit()
