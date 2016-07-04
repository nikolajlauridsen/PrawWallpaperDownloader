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
        self.c.execute("CREATE TABLE IF NOT EXISTS downloads (Date TEXT, Link TEXT PRIMARY KEY)")

    def insert_link(self, link):
        timestamp = time.strftime("%d-%m-%Y %H:%M")
        self.c.execute("INSERT INTO downloads VALUES (?,?)", (timestamp, link))

    def get_links(self):
        self.c.execute("SELECT Link FROM downloads")
        links = self.c.fetchall()
        return links

    def check_links(self, image_links):
        new_links = []
        old_links = []

        for link in self.get_links():
            old_links.append(link[0])

        for link in image_links:
            if link not in old_links:
                new_links.append(link)
            else:
                print(link + " has already been downloaded")
        return new_links

    def save_changes(self):
        self.conn.commit()
