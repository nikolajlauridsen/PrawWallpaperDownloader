"""
Functions related to downloading wallpapers
"""
import requests
import time
import os


# Get image link of most upvoted wallpaper of the day
def get_top_image(subreddit):
    dl_urls = []
    for submission in subreddit.get_top(limit=25):
        url = submission.url
        if url.endswith(".jpg"):
            dl_urls.append(url)
        # Imgur support
        elif ("imgur.com" in url) and ("/a/" not in url):
            if url.endswith("/new"):
                url = url.rsplit("/", 1)[0]
            id = url.rsplit("/", 1)[1].rsplit(".", 1)[0]
            dl_urls.append("http://imgur.com/" + id + ".jpg")
    return dl_urls


# Save a list of image links to disk
def download_images(image_urls):
    images = image_urls
    image_n = 0
    total_images = len(images)

    for url in images:
        print("Downloading image " + str(image_n+1) + "/" + str(total_images))
        # Send request
        response = requests.get(url)

        # Save image to disk
        if response.status_code == 200:
            file_path = os.path.join('images', str(image_n) + time.strftime(" %d-%m-%Y") + ".jpg")
            with open(file_path, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)
        image_n += 1
