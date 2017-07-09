from db_handler import DbHandler
from configurator import Configurator

import time
import os
import queue
import threading
import sys
import requests
import bs4
import re
import praw
import argparse
from PIL import Image

configurator = Configurator()


class Scraper:
    """A class for scraping links on reddit, utilizes DbHandler.py,
    and configurator.py"""

    def __init__(self):
        self.db = DbHandler()
        self.r = praw.Reddit(user_agent="PrawWallpaperDownloader 1.0.0 by /u/Pusillus")

        self.succeeded = 0
        self.failed = 0
        self.skipped = 0
        self.n_posts = 0
        self.albums = 0

        self.notify = False

        self.posts = []
        self.que = queue.Queue()
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
        parser.add_argument('-na', '--noalbum', help='Skip imgur albums',
                            action='store_true', default= not self.config.getboolean('Albums'))
        parser.add_argument('-con', '--configure', help="Change settings",
                            action='store_true', default=False)
        args = parser.parse_args()
        return args

    def get_posts(self, subreddit):
        """Get and sort posts from reddit"""
        albums = []  # Array to hold all the album elements for later.
        print('Contacting reddit, please hold...')
        for submission in subreddit.get_hot(limit=self.args.limit):
            url = submission.url
            # Check for author
            if not submission.author:
                author = '[User Deleted]'
            else:
                author = str(submission.author)

            if url.endswith(".jpg"):
                context = {"url": url,
                           "title": submission.title,
                           "author": author,
                           "parent_id": None}
                self.posts.append(context)

            # Imgur support
            elif ("imgur.com" in url) and ("/a/" not in url):
                if url.endswith("/new"):
                    url = url.rsplit("/", 1)[0]
                id = url.rsplit("/", 1)[1].rsplit(".", 1)[0]
                link = "http://i.imgur.com/" + id + ".jpg"
                context = {"url": link,
                           "title": submission.title,
                           "author": author,
                           "parent_id": None}
                self.posts.append(context)
            # Album support
            elif ("imgur.com" in url) and ("/a/" in url):
                album_context = {"url"  : url,
                                 "title": submission.title,
                                 "author": author}
                albums.append(album_context)

        # Extract all image links from the imgur albums
        if not self.args.noalbum:
            self.handle_albums(albums)
        # Save amount of valid imagages
        self.n_posts = len(self.posts)
        # Sort out previously downloaded images
        if not self.args.nosort:
            if self.config["MaxAge"].lower().strip() == "none":
                self.posts, self.skipped_list = self.db.sort_links(self.posts)
            else:
                self.posts, self.skipped_list = self.db.sort_links(self.posts, age_limit=self.config["MaxAge"])
            self.print_skipped()

    def handle_albums(self, albums):
        """Extract all links from a list of imgur albums"""
        albums = self.db.sort_albums(albums)
        n_albums = len(albums)

        for _id, album in enumerate(albums):
            print("\rHandling album: {}/{}".format(_id+1,n_albums), end='')
            # Download imgur album
            res = requests.get(album["url"])
            try:
                res.raise_for_status()
            except Exception as exc:
                self.handle_error(exc, album)
                continue


            # Parse through the html fetching all link elements
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            link_elements = soup.select('a.zoom')

            # Insert link to get id
            album['length'] = len(link_elements)
            album_id = self.db.insert_album(album)

            if len(link_elements) > 0:
                for a_id, ele in enumerate(link_elements):
                    # Put the data in context for later
                    context = {"url"  : "http:" + ele.get('href'),
                               "title": album["title"],
                               "parent_id": album_id,
                               "id"   : a_id,
                               "author": album["author"]}
                    self.posts.append(context)
            self.albums += 1
        print() #Add missing newline from printing album nr

    def handle_error(self, err, post):
        """Handles error stats and prints a message if verbose is enabled"""
        self.callbacks.append(err)
        self.failed += 1
        self.failed_list.append(post)
        if self.args.verbose:
            # \033[F should return cursor to last line
            # But this is not guranteed for all consoles
            # Maybe look into curse library
            print('\nAn album error occured: ' + str(err), end='\033[F')

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

    def grab_image(self, download_folder):
        while True:
            try:
                submission = self.que.get(block=False)
            except queue.Empty:
                return

            # Try to download image
            try:
                response = requests.get(submission["url"], timeout=10)
                response.raise_for_status()
            except Exception as exc:
                self.handle_error(exc, submission)

            # Try to determine file format from headers fall back to trying to
            # determine it from url if content-type is missing.
            # Most modern operating systems will open the file regardless
            # of format suffix
            try:
                type_header = response.headers['Content-Type'].split('/')
                if type_header[0] == 'image':
                    content_type = type_header[1]
                else:
                    # Sometimes the content-type is incorrect
                    # try to guess it from URL
                    if submission["url"].endswith('.png'):
                        content_type = "png"
                    else:
                        content_type = "jpg"
            except KeyError and IndexError:
                # Missing content-type header, guess from link
                if submission["url"].endswith('.png'):
                    content_type = "png"
                else:
                    content_type = "jpg"

            # content-headers describe .jpg images with jpeg
            if  content_type == 'jpeg':
                image_format = '.jpg'
            else:
                image_format = '.' + content_type

            # If there's an id key in the submission it's from an album and
            # should be suffixed with it's position within that album
            if 'id' in submission:
                file_path = os.path.join(download_folder,
                                         re.sub(r'[\\/:*?"<>|]',
                                                '',
                                                submission["title"][:25
                                                ]) + '_' + str(submission['id']+1) + image_format)
            else:
                file_path = os.path.join(download_folder,
                                         re.sub(r'[\\/:*?"<>|]',
                                                '',
                                                submission["title"][:25]) + image_format)
            # Try to save the image to disk
            try:
                with open(file_path, 'wb') as image:
                    for chunk in response.iter_content(4096):
                        image.write(chunk)
                self.succeeded += 1
                self.downloaded_images.append(file_path)
            except Exception as exc:
                self.handle_error(exc, submission)

    def update_screen(self):
        while self.notify:
            handled_images = self.succeeded + self.failed
            print("Downloading images {}/{}".format(handled_images,len(self.posts)),
                  flush=True, end='\r')
            time.sleep(0.5)

    def download_images(self):
        """Create folders and try to download/save the image links
         in self.posts, assumes all links are image links"""
        # Stop if there's not posts to download
        if len(self.posts) < 1:
            print("No new images to download.")
            return

        # Make folders
        os.makedirs("Downloads", exist_ok=True)
        download_folder = os.path.join("Downloads", self.args.subreddit)
        os.makedirs(download_folder, exist_ok=True)

        for post in self.posts:
            self.que.put(post)

        thread_count = 10
        threads = []
        print("Starting {} threads".format(thread_count))
        for n in range(thread_count):
            thread = threading.Thread(target=self.grab_image,
                                      args=(download_folder, ))
            thread.start()
            threads.append(thread)

        self.notify = True
        threading.Thread(target=self.update_screen).start()
        for thread in threads:
            thread.join()
        self.notify = False


    def print_stats(self):
        """Print download stats to console"""
        print()
        self.skipped = len(self.skipped_list)
        new_images = self.succeeded-len(self.deleted_images)
        print('Albums: {}\nImages downloaded: {}/{} \nSkipped: {}\n'
              'Failed: {}\nDeleted: {}\n'
              'New images: {}'.format(self.albums,
                                      self.succeeded,
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
        with open("log.txt", 'w', encoding="utf-8") as log:
            # Introduction
            log.write("Log for " + time.strftime("%d-%m-%Y %H:%M") + "\n")
            log.write("Albums: {}\nSucceeded: {}\nSkipped: {}\n"
                      "Deleted: {}\nFailed: {}\n\n".format(self.albums,
                                                           self.succeeded,
                                                           self.skipped,
                                                           len(self.deleted_images),
                                                           self.failed))

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

            # Callbacks
            if len(self.callbacks) > 0:
                log.write("Begin callbacks".center(40, '=') + '\n')
                for callback in self.callbacks:
                    log.write(str(callback))
                    log.write('\n'*2)
                log.write('End callbacks'.center(40, '=') + '\n'*2)

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

            # Deleted list
            if len(self.deleted_images) > 0:
                log.write('Begin deleted list'.center(40, '=') + '\n'*2)
                for image in self.deleted_images:
                    try:
                        log.write("{} deleted due to size\n\n".format(image))
                    except UnicodeEncodeError:
                        pass
                log.write('End deleted list'.center(50, '=') + '\n'*2)


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
                    self.deleted_images.append(image_path)
                except PermissionError:
                    print('\nCan\'t delete ' + image_path + ' image is currently in use')
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
            sys.exit("It appears like you mis typed the subreddit name")
        except praw.errors.Forbidden:
            sys.exit("Access to subreddit denied")
        except praw.errors.NotFound:
            sys.exit("Subreddit not found")

        self.download_images()
        self.save_posts()
        if len(self.downloaded_images) > 0 and not self.args.noclean:
            self.clean_up()
        self.print_stats()
        if self.args.log:
            self.save_log()
