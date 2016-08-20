from db_handler import Db_handler
import time
import os
import requests
import re
import praw


class Scraper:

    def __init__(self, sub):
        self.db = Db_handler()
        self.r = praw.Reddit(user_agent="Wallpaper switcher V0.2.1 by /u/Pusillus")
        self.succeeded = 0
        self.failed = 0
        self.skipped = 0
        self.total_posts = 0
        self.posts = []
        self.failed_list = []
        self.skipped_list = []
        self.subreddit = sub

    def get_posts(self, subreddit):
        # TODO: Rubber ducky this shit, figure it out, something is not right
        for submission in subreddit.get_hot(limit=100):
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

    def download_images(self):
        download_n = 1
        self.total_posts = len(self.posts)
        self.posts, self.skipped_list = self.db.check_links(self.posts)
        total_downloads = len(self.posts)

        os.makedirs('wallpapers', exist_ok=True)
        for submission in self.posts:
            print('\r Downloading image {}/{}'
                  .format(download_n, total_downloads), flush=True, end='')
            # Send requests
            response = requests.get(submission["url"])

            # Save image to disk
            if response.status_code == 200:
                file_path = os.path.join('wallpapers',
                                         re.sub(r'[\:/?"<>|()-=]',
                                                '', submission["title"][:25]) +
                                         ".jpg")
                with open(file_path, 'wb') as fo:
                    for chunk in response.iter_content(4096):
                        fo.write(chunk)
                    fo.close()
                self.succeeded += 1
            else:
                self.failed += 1
                self.failed_list.append(submission)
            download_n += 1

    def print_stats(self):
        print("\n")
        self.skipped = len(self.skipped_list)
        print('Posts downloaded: {}/{} \nSkipped: {}\nFailed: {}'
              .format(self.succeeded, self.total_posts, self.skipped, self.failed))

    def save_posts(self):
        for post in self.posts:
            self.db.insert_link(post)
        self.db.save_changes()

    def run(self):
        print('Fetching URLS...')
        self.get_posts(self.r.get_subreddit(self.subreddit))
        self.download_images()
        self.save_posts()
        self.print_stats()


