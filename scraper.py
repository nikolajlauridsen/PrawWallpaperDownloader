from db_handler import Db_handler

import time
import os
import requests
import re
import praw


class Scraper:
    """A class for scraping links on reddit, utilizes Db_handler.py"""

    def __init__(self, args):
        self.db = Db_handler()
        self.r = praw.Reddit(user_agent="PrawWallpaperDownload 0.3.0 by /u/Pusillus")
        self.succeeded = 0
        self.failed = 0
        self.skipped = 0
        self.n_posts = 0
        self.posts = []
        self.failed_list = []
        self.callbacks = []
        self.skipped_list = []
        self.args = args

    def get_posts(self, subreddit):
        """Get and sort posts from reddit"""
        print('Contacting reddit and fetching urls, please hold...')
        for submission in subreddit.get_hot(limit=self.args.limit):
            url = submission.url
            if url.endswith(".jpg"):
                context = {"url": url,
                           "title": submission.title,
                           "date": time.strftime("%d-%m-%Y %H:%M")}
                self.posts.append(context)

            # Imgur support
            elif ("imgur.com" in url) and ("/a/" not in url):
                if url.endswith("/new"):
                    url = url.rsplit("/", 1)[0]
                id = url.rsplit("/", 1)[1].rsplit(".", 1)[0]
                link = "http://i.imgur.com/" + id + ".jpg"
                context = {"url": link,
                           "title": submission.title,
                           "date": time.strftime("%d-%m-%Y %H:%M")}
                self.posts.append(context)
        self.n_posts = len(self.posts)
        self.posts, self.skipped_list = self.db.check_links(self.posts)
        self.print_skipped()

    def download_images(self):
        """Create folders and try to download/save the image links in self.posts"""
        # Make folders
        os.makedirs("Downloads", exist_ok=True)
        download_folder = os.path.join("Downloads", self.args.subreddit)
        os.makedirs(download_folder, exist_ok=True)

        for l_id, submission in enumerate(self.posts):
            print('\r Downloading image {}/{}'
                  .format(l_id+1, self.n_posts), flush=True, end='')
            # Send requests
            response = requests.get(submission["url"])

            # Try to download image
            try:
                response.raise_for_status()
            except Exception as exc:
                if self.args.verbose:
                    print('And error occured when downloading image\n'
                          'Callback: {}'.format(exc))
                self.callbacks.append(exc)
                self.failed += 1
                self.failed_list.append(submission)

            file_path = os.path.join(download_folder,
                                     re.sub(r'[\:/?"<>|()-=]',
                                            '',
                                            submission["title"][:25]) + ".jpg")
            # Try to save the image to disk
            try:
                with open(file_path, 'wb') as image:
                    for chunk in response.iter_content(4096):
                        image.write(chunk)
                    image.close()
                self.succeeded += 1
            except Exception as exc:
                if self.args.verbose:
                    print('An error occured when saving the image\n'
                          'Callback: {}'.format(exc))
                self.failed += 1
                self.failed_list.append(submission)
                self.callbacks.append(exc)

    def print_skipped(self):
        """Print posts in skipped_list to console"""
        if self.args.verbose:
            print('\n', 'Skipped posts'.center(40, '='))
            for post in self.skipped_list:
                try:
                    print(post["title"] + " has already been downloaded... skipping")
                except UnicodeEncodeError:
                    print(post["url"] + " has already been downloaded... skipping")
            print('End list'.center(40, '='), '\n')

    def print_stats(self):
        """Print download stats to console"""
        print("\n")
        self.skipped = len(self.skipped_list)
        print('Posts downloaded: {}/{} \nSkipped: {}\n'
              'Failed: {}'.format(self.succeeded,
                                  self.n_posts,
                                  self.skipped,
                                  self.failed))

    def save_posts(self):
        """Save posts currently in self.posts to database"""
        for post in self.posts:
            self.db.insert_link(post)
        self.db.save_changes()

    def save_log(self):
        """Build log file"""
        with open("log.txt", 'w') as log:
            # Introduction
            log.write("Log for " + time.strftime("%d-%m-%Y %H:%M") + "\n")
            log.write("Succeeded: {}\nSkipped: {}\n"
                     "Failed: {}\n\n".format(self.succeeded,
                                             self.skipped,
                                             self.failed))

            # Skipped list
            if len(self.skipped_list) > 0:
                log.write("Begin skipped list".center(40, '=') + '\n')
                for post in self.skipped_list:
                    log.write("{}\n{}\n{}\n"
                             "\n".format(post["title"],
                                         post["url"],
                                         post["date"]))
                log.write("End skipped list".center(40, '=') + '\n'*2)

            # Failed list
            if len(self.failed_list) > 0:
                log.write("Begin failed list".center(40, '=') + '\n')
                for post in self.failed_list:
                    log.write("{}\n{}\n{}\n"
                             "\n".format(post["title"],
                                         post["url"],
                                         post["date"]))
                log.write("End failed list".center(40, '=') + '\n'*2)

            # Callbacks
            if len(self.callbacks) > 0:
                log.write("Begin callbacks".center(40, '=') + '\n')
                for callback in self.callbacks:
                    log.write(str(callback))
                    log.write('\n'*2)
                log.write('End callbacks'.center(40, '=') + '\n'*2)

            log.close()

    def re_download(self):
        """Attempts to re-download all links in the database"""
        self.posts = self.db.get_posts()
        self.n_posts = len(self.posts)
        self.download_images()
        self.print_stats()
        if self.args.log:
            self.save_log()

    def run(self):
        """Run the scraper"""
        self.get_posts(self.r.get_subreddit(self.args.subreddit))
        self.download_images()
        self.save_posts()
        self.print_stats()
        if self.args.log:
            self.save_log()
