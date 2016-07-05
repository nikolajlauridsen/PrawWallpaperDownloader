"""
Class that handles database interaction
"""
import sqlite3 as lite
import time


class Db_handler():
    """Handles Database interaction"""

    def __init__(self):
        self.conn = lite.connect('wallpaper_base.db')
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS downloads (Date TEXT, Link TEXT PRIMARY KEY, Title TEXT)")

    # Insert a link into the database
    def insert_link(self, submission):
        self.c.execute("INSERT INTO downloads VALUES (?,?,?)", (submission["date"], submission["url"], submission["title"]))

    # Returns all links as a list
    def get_links(self):
        self.c.execute("SELECT Link FROM downloads")
        links = self.c.fetchall()
        return links

    # Removes all downloaded links from a list of links
    def check_links(self, submissions):
        new_links = []
        old_links = []

        for link in self.get_links():
            old_links.append(link[0])

        for submission in submissions:
            if submission["url"] not in old_links:
                new_links.append(submission)
            else:
                print(submission["title"] + " has already been downloaded")
        return new_links

    # Commit changes to the database
    def save_changes(self):
        self.conn.commit()
