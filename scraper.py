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
        self.callbacks = []
        self.skipped_list = []
        self.args = args

    # get posts from reddit and add them to self.posts
    def get_posts(self, subreddit):
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

    # Sort out previously downloaded links and download the image links in self.posts
    def download_images(self):
        os.makedirs('wallpapers', exist_ok=True)
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
                    print('And error occured when downloading image\nCallback: {}'.format(exc))
                self.callbacks.append(exc)
                self.failed += 1
                self.failed_list.append(exc)

            file_path = os.path.join('wallpapers',
                                     re.sub(r'[\:/?"<>|()-=]',
                                            '', submission["title"][:25]) +
                                     ".jpg")
            # Try to save the image to disk
            try:
                with open(file_path, 'wb') as fo:
                    for chunk in response.iter_content(4096):
                        fo.write(chunk)
                    fo.close()
                self.succeeded += 1
            except Exception as exc:
                if self.args.verbose:
                    print('An error occured when saving the image\nCallback: {}'.format(exc))
                self.failed += 1
                self.failed_list.append(submission)
                self.callbacks.append(exc)

    # Print posts in skipped_list to console
    def print_skipped(self):
        if self.args.verbose:
            print('\n', 'Skipped posts'.center(40, '='))
            for post in self.skipped_list:
                try:
                    print(post["title"] + " has already been downloaded... skipping")
                except UnicodeEncodeError:
                    print(post["url"] + " has already been downloaded... skipping")
            print('End list'.center(40, '='), '\n')

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
                fo.write("Begin skipped list".center(40, '=') + '\n')
                for post in self.skipped_list:
                    fo.write("{}\n{}\n{}\n\n".format(post["title"], post["url"], post["date"]))
                fo.write("End skipped list".center(40, '=') + '\n'*2)

            if len(self.failed_list) > 0:
                fo.write("Begin failed list".center(40, '=') + '\n')
                for post in self.failed_list:
                    fo.write("{}\n{}\n{}\n\n".format(post["title"], post["url"], post["date"]))
                fo.write("End skipped list".center(40, '=') + '\n'*2)

            if len(self.callbacks) > 0:
                fo.write("Begin callbacks".center(40, '=') + '\n')
                for callback in self.callbacks:
                    fo.write(callback)
                    fo.write('\n'*2)
                fo.write('End callbacks'.center(40, '=') + '\n'*2)

            fo.close()

    # Attempts to re-download all links in the database
    def re_download(self):
        self.posts = self.db.get_posts()
        self.n_posts = len(self.posts)
        self.download_images()
        self.print_stats()
        if self.args.log:
            self.save_log()

    # Run the scraper
    def run(self):
        self.get_posts(self.r.get_subreddit(self.args.subreddit))
        self.download_images()
        self.save_posts()
        self.print_stats()
        if self.args.log:
            self.save_log()
