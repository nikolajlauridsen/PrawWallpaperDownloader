from db_handler import DbHandler
from configurator import Configurator

import time
import os
import requests
import bs4
import re
import praw
import argparse
from PIL import Image

configurator = Configurator()
"""
 TODO: CLEAN UP!
     : Maybe make a dedicated function for download errors
     : Improve naming of album pictures
"""
class Scraper:
    """A class for scraping links on reddit, utilizes DbHandler.py,
    and configurator.py"""

    def __init__(self):
        self.db = DbHandler()
        self.r = praw.Reddit(user_agent="PrawWallpaperDownloader 0.9.0 by /u/Pusillus")
        self.succeeded = 0
        self.failed = 0
        self.skipped = 0
        self.n_posts = 0
        self.posts = []
        self.downloaded_images = []
        self.failed_list = []
        self.callbacks = []
        self.skipped_list = []
        self.deleted_images = []
        self.config = configurator.get_config()
        self.args = self.parse_arguments()

    def parse_arguments(self):
        """Parse arguments from commandline"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--subreddit",
                            help="specify subreddit to scrape",
                            default=self.config['Sub'])
        parser.add_argument("-l", "--limit",
                            help="set amount of posts to sift through "
                                 "(default " + self.config['Limit'] + ")",
                            default=int(self.config['Limit']), type=int)
        parser.add_argument("--log",
                            help="save a log of wallpapers downloaded/skipped/failed",
                            action="store_true", default=False)
        parser.add_argument("-re", "--redownload",
                            help="attempt to download all the links in the database",
                            action="store_true", default=False)
        parser.add_argument("-v", "--verbose", help="increase output detail",
                            action="store_true",
                            default=False)
        parser.add_argument('-nc', "--noclean", help="Skip cleaning off small images (Cleaning: " + self.config['Clean'] + ")",
                            action="store_true", default= not self.config.getboolean('Clean'))
        parser.add_argument('-ns', '--nosort', help="Skip sorting out previously downloaded images (Sorting: {})".format(self.config['sort']),
                            action="store_true", default= not self.config.getboolean('Sort'))
        parser.add_argument('-con', '--configure', help="Change settings",
                            action='store_true', default=False)
        args = parser.parse_args()
        return args

    def get_posts(self, subreddit):
        """Get and sort posts from reddit"""
        albums = []
        print('Contacting reddit, please hold...')
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
            elif ("imgur.com" in url) and ("/a/" in url):
                album_context = {"url"  : url,
                                 "title": submission.title,
                                 "date": time.strftime("%d-%m-%Y %H:%M")}
                albums.append(album_context)
        # Extract all image links from the imgur albums
        self.handle_albums(albums)
        # Save amount of valid imagages
        self.n_posts = len(self.posts)
        # Sort out previously downloaded images
        if not self.args.nosort:
            self.posts, self.skipped_list = self.db.sort_links(self.posts)
            self.print_skipped()

    def handle_albums(self, albums):
        """Extract all links from a list of imgur albums"""
        n_albums = len(albums)

        for _id, album in enumerate(albums):
            print("\rHandling album: {}/{}".format(_id+1,n_albums), end='')
            res = requests.get(album["url"])
            try:
                res.raise_for_status()
            except Exception as exc:
                self.callbacks.append(exc)
                self.failed += 1
                self.failed_list.append(album)
                if self.args.verbose:
                    # \033[F should return cursor to last line
                    # But this is not guranteed for all consoles
                    # Maybe look into curse library
                    print('\nAn album error occured: ' + str(exc), end='\033[F')
                continue

            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            link_elements = soup.select('a.zoom')
            if len(link_elements) > 0:
                for n, ele in enumerate(link_elements):
                    context = {"url"  : "http:" + ele.get('href'),
                               "title": str(n) + "_" + album["title"],
                               "date" : album["date"]}
                    self.posts.append(context)
        print() #Add missing newline from printing album nr

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

    def download_images(self):
        """Create folders and try to download/save the image links in self.posts"""
        # Make folders
        os.makedirs("Downloads", exist_ok=True)
        download_folder = os.path.join("Downloads", self.args.subreddit)
        os.makedirs(download_folder, exist_ok=True)

        for l_id, submission in enumerate(self.posts):
            print('\r Downloading image {}/{}'
                  .format(l_id+1, len(self.posts)), flush=True, end='')
            # Send requests
            response = requests.get(submission["url"])

            # Try to download image
            try:
                response.raise_for_status()
            except Exception as exc:
                if self.args.verbose:
                    print('And error occured when downloading image\n'
                          'Callback: {}'.format(exc), end='\033[F')
                self.callbacks.append(exc)
                self.failed += 1
                self.failed_list.append(submission)

            if submission["url"].endswith('.png'):
                format = '.png'
            else:
                format = '.jpg'
            file_path = os.path.join(download_folder,
                                     re.sub(r'[\\/:*?"<>|]',
                                            '',
                                            submission["title"][:25]) + format)
            # Try to save the image to disk
            try:
                with open(file_path, 'wb') as image:
                    for chunk in response.iter_content(4096):
                        image.write(chunk)
                    image.close()
                self.succeeded += 1
                self.downloaded_images.append(file_path)
            except Exception as exc:
                if self.args.verbose:
                    print('An error occured when saving the image\n'
                          'Callback: {}'.format(exc), end='\033[F')
                self.failed += 1
                self.failed_list.append(submission)
                self.callbacks.append(exc)

    def print_stats(self):
        """Print download stats to console"""
        print()
        self.skipped = len(self.skipped_list)
        new_images = self.succeeded-len(self.deleted_images)
        print('Posts downloaded: {}/{} \nSkipped: {}\n'
              'Failed: {}\nDeleted: {}\n'
              'New images: {}'.format(self.succeeded,
                                      self.n_posts,
                                      self.skipped,
                                      self.failed,
                                      len(self.deleted_images),
   				                      new_images))

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
                    try:
                        log.write("{}\n{}\n"
                                 "\n".format(post["title"],
                                             post["url"]))
                    except UnicodeEncodeError:
                        pass
                log.write("End skipped list".center(40, '=') + '\n'*2)

            # Failed list
            if len(self.failed_list) > 0:
                log.write("Begin failed list".center(40, '=') + '\n')
                for post in self.failed_list:
                    try:
                        log.write("{}\n{}\n"
                                 "\n".format(post["title"],
                                             post["url"]))
                    except UnicodeEncodeError:
                        pass
                log.write("End failed list".center(40, '=') + '\n'*2)

            # Deleted list
            if len(self.deleted_images) > 0:
                log.write('Begin deleted list'.center(40, '=') + '\n'*2)
                for image in self.deleted_images:
                    log.write("{} deleted due to size\n\n".format(image))
                log.write('End deleted list'.center(50, '=') + '\n'*2)
            # Callbacks
            if len(self.callbacks) > 0:
                log.write("Begin callbacks".center(40, '=') + '\n')
                for callback in self.callbacks:
                    log.write(str(callback))
                    log.write('\n'*2)
                log.write('End callbacks'.center(40, '=') + '\n'*2)

            log.close()

    def clean_up(self):
        """Examines all downloaded images, deleting duds"""
        print('\nCleaning up')
        for image_path in self.downloaded_images:
            try:
                image = Image.open(image_path)
            except OSError:
                continue
            if image.size[0] < int(self.config['MinWidth'])\
                    or image.size[1] < int(self.config['MinHeight']):
                image.close()
                try:
                    os.remove(image_path)
                except PermissionError:
                    print('\nCan\'t delete ' + image_path + ' image is currently in use')
                self.deleted_images.append(image_path)
            else:
                image.close()

    def re_download(self):
        """Attempts to re-download all links in the database"""
        self.posts = self.db.get_posts()
        self.n_posts = len(self.posts)
        self.download_images()
        if len(self.downloaded_images) > 0 and not self.args.noclean:
            self.clean_up()
        self.print_stats()
        if self.args.log:
            self.save_log()

    def run(self):
        """Run the scraper"""
        try:
            print('Getting posts from: ' + self.args.subreddit)
            self.get_posts(self.r.get_subreddit(self.args.subreddit))
        except praw.errors.InvalidSubreddit:
            print("It appears like you mis typed the subreddit name")
        self.download_images()
        self.save_posts()
        if len(self.downloaded_images) > 0 and not self.args.noclean:
            self.clean_up()
        self.print_stats()
        if self.args.log:
            self.save_log()
