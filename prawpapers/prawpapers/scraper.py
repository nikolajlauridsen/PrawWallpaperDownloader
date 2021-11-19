from .Persistance.db_handler import DbHandler
from .Configuration.configurator import Configurator
from .Configuration.argument_parser import ArgumentParser
from .PyCLIBar.CLIBar import CLIBar
from prawcore.exceptions import RequestException, ResponseException

import time
import os
import queue
import threading
import sys
import requests
import bs4
import re
import praw
import json
from PIL import Image
import logging


class Scraper:
    """
    The scraper, pretty much does all the hard work. 
    When the Scraper is initialized it wil parse commandline arguments.
    utilizes DbHandler.py,´and configurator.py
    """

    def __init__(
            self,
            configurator: Configurator,
            argument_parser: ArgumentParser,
            database: DbHandler) -> None:

        self.database = database
        self.config = configurator.get_config()
        self.args = argument_parser.parse_arguments()

        _id = self.get_id()
        self.reddit = praw.Reddit(user_agent="PrawWallpaperDownloader 1.0.0 by /u/Pusillus", client_id=_id["id"], client_secret=_id["secret"])

        self.post_count = 0
        self.albums = 0
        self.succeeded = 0
        self.failed = 0
        self.skipped = 0
        self.deleted = 0

        self.notify = False

        self.posts = []
        self.queue = queue.Queue()
        self.downloaded_images = []

    @staticmethod
    def get_id():
        if os.path.isfile('client_secret.json'):
            with open('client_secret.json', 'r') as id_file:
                return json.loads("".join(id_file.readlines()))
        else:
            logging.error('Client_secret.json not found, exiting')
            sys.exit('Unable to locate client_secret.json.\n'
                     'Please have a look at README.md '
                     'and follow the instructions')

    def get_submissions(self, subreddit):
        """
        Get submissions from reddit
        Takes a subreddit object from PRAW as argument
        Returns list of PRAW submission objects
        """
        section = self.args.section.lower().strip()
        limit = self.args.limit
        if self.args.search:
            return subreddit.search(self.args.search)
        elif section == "top":
            return subreddit.top(limit=limit)
        elif section == "new":
            return subreddit.new(limit=limit)
        elif section == "rising":
            return subreddit.rising(limit=limit)
        else:
            if section != "hot":
                logging.warning("Unknown section, defaulting to hot")
                print("Unknown section, defaulting to hot")
            return subreddit.hot(limit=limit)

    def extract_submission_data(self, submission):
        """
        Exctract direct image links, and relevant data from a PRAW submission
        object
        Takes a PRAW submission object as arguments and appends a dictionary
        in the following format to self.posts:

        {"url": image-link,
         "title": submission title,
         "author": author of the submission (reddit user name),
         "parent_id": None (only used for images in albums)}

        If the submission link to an album this function will instead return
        an album dictionary for further processing later in the process
        album dictionary format:
        {"url": link to imgur album,
         "title": submission title,
         "author": submission author (reddit username}
        """
        url = submission.url
        # Check for author
        if not submission.author:
            author = '[User Deleted]'
        else:
            author = str(submission.author)

        # Direct jpg and png links
        if url.endswith(".jpg") or url.endswith(".png"):
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
            album_context = {"url": url,
                             "title": submission.title,
                             "author": author}
            return album_context

    def handle_submissions(self, submissions):
        """Get and sort posts from reddit"""
        albums = []  # Array to hold all the album elements for later.
        for submission in submissions:
            album = self.extract_submission_data(submission)
            if album:
                albums.append(album)

        # Extract all image links from the imgur albums
        if not self.args.noalbum:
            self.handle_albums(albums)

        # Save amount of valid images
        self.post_count = len(self.posts)

        # Sort out previously downloaded images
        if not self.args.nosort:
            if int(self.config["MaxAge"]) == 0:
                self.posts = self.database.sort_links(self.posts)
            else:
                self.posts = self.database.sort_links(self.posts, age_limit=self.config["MaxAge"])
            self.skipped = self.post_count - len(self.posts)

    def handle_albums(self, albums):
        """Extract all links from a list of imgur albums"""
        logging.info('Extracting albums...')
        albums = self.database.sort_albums(albums)
        n_albums = len(albums)

        for _id, album in enumerate(albums):
            print("\rHandling album: {}/{}".format(_id+1, n_albums), end='')
            logging.info('Handling album {}/{}'.format(_id+1, n_albums))
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
            album_id = self.database.insert_album(album)

            if len(link_elements) > 0:
                for a_id, ele in enumerate(link_elements):
                    # Put the data in context for later
                    context = {"url": "http:" + ele.get('href'),
                               "title": album["title"],
                               "parent_id": album_id,
                               "id": a_id,
                               "author": album["author"]}
                    self.posts.append(context)
            self.albums += 1
        print()  # Add missing newline from printing album nr

    def handle_error(self, err, post):
        """Handles error stats and prints a message if verbose is enabled"""
        self.failed += 1
        logging.error('Error occurred at:{} {}: {}'.format(post["title"],
                                                           type(err),
                                                           str(err)))

    def grab_image(self, download_folder, bar):
        """
        Worker function for downloading images, keeps pulling a new link
        from image que, downloads it, and saves it, untill the que is empty.
        Takes 2 arguments:
        download_folder: Path to desired save folder
        bar: PyCLIBar to be stepped after image has been downloaded
        """
        while True:
            try:
                submission = self.queue.get(block=False)
            except queue.Empty:
                logging.info('Download thread done... Stopping')
                return

            # Try to download image
            logging.info('Downloading image {}'.format(submission["title"]))
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
            if content_type == 'jpeg':
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
                bar.step()
            except Exception as exc:
                self.handle_error(exc, submission)

    def update_screen(self, bar):
        """
        Keeps refreshing the CLIbar every .5 seconds as llong as self.notify
        is true, always run as a seperate thread
        """
        while self.notify:
            print("{}".format(bar.get_progress_bar()),
                  flush=True, end='\r')
            time.sleep(0.5)
        logging.info('Notify thread stopping')
        return

    def download_images(self):
        """Create folders and try to download/save the image links
         in self.posts, assumes all links are image links"""
        # Stop if there's not posts to download
        if len(self.posts) < 1:
            logging.info('No images to download, stopping')
            sys.exit("No new images to download.")

        logging.info('Starting download')
        # Make folders
        logging.info('Creating folders')
        os.makedirs("Downloads", exist_ok=True)
        download_folder = os.path.join("Downloads", self.args.subreddit)
        os.makedirs(download_folder, exist_ok=True)

        for post in self.posts:
            self.queue.put(post)

        # Create progress bar
        bar = CLIBar(_max=len(self.posts))

        threads = []
        print("Starting {} threads".format(self.args.threads))
        for n in range(min(len(self.posts), self.args.threads)):
            logging.info('Starting thread: {}'.format(n))
            thread = threading.Thread(target=self.grab_image,
                                      args=(download_folder, bar))
            thread.start()
            threads.append(thread)

        print("Downloading images")
        bar.start()

        self.notify = True
        logging.info('Starting notify thread')
        threading.Thread(target=self.update_screen,
                         args=(bar, )).start()

        logging.info('Waiting for download threads to finish')
        for thread in threads:
            try:
                thread.join()
            except KeyboardInterrupt:
                # Don't know how to handle this, ideas?
                pass
        logging.info('Done, telling notify thread to stop')
        self.notify = False

    def print_stats(self):
        """Print download stats to console"""
        print()
        new_images = self.succeeded-self.deleted
        print('Albums: {}\nImages downloaded: {}/{} \nSkipped: {}\n'
              'Failed: {}\nDeleted: {}\n'
              'New images: {}'.format(self.albums,
                                      self.succeeded,
                                      self.post_count,
                                      self.skipped,
                                      self.failed,
                                      self.deleted,
                                      new_images))

    def save_posts(self):
        """Save posts currently in self.posts to database"""
        for post in self.posts:
            self.database.insert_link(post)
        self.database.save_changes()

    def clean_up(self):
        """Examines all downloaded images, deleting duds"""
        print('\nCleaning up')
        min_ratio = (int(self.config['MinWidth'])/int(self.config['MinHeight']))*self.args.ratiolock
        max_ratio = (int(self.config['MinWidth'])/int(self.config['MinHeight']))*(2-self.args.ratiolock)
        if float(self.args.ratiolock) <= 0:
            max_ratio = 100000
        logging.info("Ratio settings: RatioLock: {} | MinRatio: {} | MaxRatio: {}".format(self.args.ratiolock,
                                                                                          min_ratio, max_ratio))
        for image_path in self.downloaded_images:
            try:
                logging.info("Checking: {}".format(image_path))
                image = Image.open(image_path)
                image_ratio = image.size[0] / image.size[1]
                logging.info("Image size: {}x{}".format(image.size[0], image.size[1]))
                logging.info("Image ratio: {}".format(image_ratio))
            except OSError:
                continue
            # Check for size.
            if image.size[0] < int(self.config['MinWidth'])\
                    or image.size[1] < int(self.config['MinHeight']):
                image.close()
                try:
                    os.remove(image_path)
                    logging.info('Removing image due to size: {}'.format(image_path))
                    self.deleted += 1
                except PermissionError as e:
                    logging.warning('Error deleting image: {}: {}: {}'.format(
                        image_path, type(e), str(e)))
                    print('\nCan\'t delete ' + image_path + ' image is currently in use')
                continue
            else:
                logging.info("Image size ok, checking ratio")
            # Check for ratio
            if min_ratio > image_ratio or max_ratio > max_ratio:
                logging.info('Removing image due to ratio: {}'.format(image_path))
                image.close()
                try:
                    os.remove(image_path)
                    self.deleted += 1
                except PermissionError as e:
                    logging.warning('Error deleting image: {}: {}: {}'.format(
                        image_path, type(e), str(e)))
                    print('\nCan\'t delete ' + image_path + ' image is currently in use')
            else:
                logging.info('Ratio ok.')
                image.close()

    def re_download(self):
        """Attempts to re-download all links in the database"""
        self.posts = self.database.get_posts()
        self.post_count = len(self.posts)
        self.download_images()
        if len(self.downloaded_images) > 0 and not self.args.noclean:
            self.clean_up()
        self.print_stats()

    def run(self):
        """Run the scraper"""
        try:
            if not self.args.search:
                print('Getting {} posts from the {} section of {}'
                      .format(self.args.limit, self.args.section, self.args.subreddit))
            else:
                print('Searching {} for {}'.format(self.args.subreddit, self.args.search))
            # Get submissions from sub
            submissions = self.get_submissions(self.reddit.subreddit(self.args.subreddit))
            # Handle the submissions and add them to self.posts
            # Sorts out previously downloaded images and extracts imgur albums
            self.handle_submissions(submissions)
        except RequestException:
            sys.exit('\nError connecting to reddit, please check your '
                     'internet connection')
        except ResponseException:
            sys.exit('\nError connecting to reddit.\n'
                     'Probably because you wrote an invalid subreddit name.\n'
                     'If that\'s not the case it\'s probably an'
                     'invalid client_secret.json file\nPlease see README.md '
                     'about how to set up the file properly.')
        except Exception as e:
            sys.exit('\nAn unknown error occurred:\n{}: {}'.format(type(e),
                                                                   str(e)))
        # Download all images in self.posts.
        self.download_images()
        self.save_posts()
        if len(self.downloaded_images) > 0 and not self.args.noclean:
            self.clean_up()
        self.print_stats()
