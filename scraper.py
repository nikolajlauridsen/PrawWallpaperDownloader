from db_handler import Db_handler
import time
import os
import requests
import re
import praw


class Scraper:

    def __init__(self, args):
        self.db = Db_handler()
        self.r = praw.Reddit(user_agent="Wallpaper switcher V0.2.1 by /u/Pusillus")
        self.succeeded = 0
        self.failed = 0
        self.skipped = 0
        self.n_posts = 0
        self.posts = []
        self.failed_list = []
        self.skipped_list = []
        self.args = args

    # get posts from reddit and add them to self.posts
    def get_posts(self, subreddit):
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

    # Sort out previously downloaded links and download the image links in self.posts
    def download_images(self):
        self.n_posts = len(self.posts)
        self.posts, self.skipped_list = self.db.check_links(self.posts)

        os.makedirs('wallpapers', exist_ok=True)
        for l_id, submission in enumerate(self.posts):
            print('\r Downloading image {}/{}'
                  .format(l_id+1, self.n_posts), flush=True, end='')
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

    # Print download stats to console
    def print_stats(self):
        print("\n")
        self.skipped = len(self.skipped_list)
        print('Posts downloaded: {}/{} \nSkipped: {}\nFailed: {}'
              .format(self.succeeded, self.n_posts, self.skipped, self.failed))

    # Save posts currently in self.posts to database
    def save_posts(self):
        for post in self.posts:
            self.db.insert_link(post)
        self.db.save_changes()

    # Save logs to file
    def save_log(self):
        with open("log.txt", 'w') as fo:
            fo.write("Log for " + time.strftime("%d-%m-%Y %H:%M") + "\n")
            fo.write("Succeeded: {}\nSkipped: {}\nFailed: {}\n\n".format(self.succeeded, self.skipped, self.failed))

            if len(self.skipped_list) > 0:
                fo.write("="*5 + "Begin skipped list" + "="*5 + "\n ")
                for post in self.skipped_list:
                    fo.write("{}\n{}\n{}\n\n".format(post["title"], post["url"], post["date"]))
                fo.write("=" * 5 + "End skipped list" + "=" * 5 + "\n")

            if len(self.failed_list) > 0:
                fo.write("="*5 + "Begin failed list" + "="*5 + "\n")
                for post in self.failed_list:
                    fo.write("{}\n{}\n{}\n\n".format(post["title"], post["url"], post["date"]))
                fo.write("=" * 5 + "End failed list" + "=" * 5 + "\n")

            fo.close()

    # Run the scraper
    def run(self):
        print('Contacting reddit and fetching urls, please hold...')
        self.get_posts(self.r.get_subreddit(self.args.subreddit))
        self.download_images()
        self.save_posts()
        self.print_stats()
        if self.args.log:
            self.save_log()
