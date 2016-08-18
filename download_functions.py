"""
Functions related to downloading wallpapers
"""
import requests
import time
import os
import re


# Get image link of most upvoted wallpaper of the day
def get_top_image(subreddit):
    dl_urls = []
    for submission in subreddit.get_top(limit=100):
        url = submission.url
        if url.endswith(".jpg"):
            context = {"url": url,
                       "title": submission.title,
                       "date": time.strftime("%d-%m-%Y %H:%M")}
            dl_urls.append(context)
        # Imgur support
        elif ("imgur.com" in url) and ("/a/" not in url):
            if url.endswith("/new"):
                url = url.rsplit("/", 1)[0]
            id = url.rsplit("/", 1)[1].rsplit(".", 1)[0]
            link = "http://imgur.com/" + id + ".jpg"
            context = {"url": link,
                       "title": submission.title,
                       "date": time.strftime("%d-%m-%Y %H:%M")}
            dl_urls.append(context)
    return dl_urls


# Save a list of image links to disk
def download_images(submissions):
    image_n = 1
    total_images = len(submissions)

    os.makedirs('wallpapers', exist_ok=True)
    for submission in submissions:
        print('\r Downloading image {}/{}'.format(image_n, total_images), flush=True, end='')
        # Send request
        response = requests.get(submission["url"])

        # Save image to disk
        if response.status_code == 200:
            # Sanitise file name TODO: mkdir)
            file_path = os.path.join('wallpapers',
                                     re.sub(r'[\:/?"<>|()-=]',
                                            '', submission["title"][:25]) +
                                     ".jpg")
            with open(file_path, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)
                fo.close()
        image_n += 1
