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
                fo.close()
        image_n += 1


# Write image links to file_path
def write_links(image_links):
    f = open('links-downloaded.txt', 'a')
    for link in image_links:
        f.write(link + "\n")
    f.close()


# Check links
def check_links(image_links):
    try:
        image_links = image_links
        new_links = []
        old_links = open('links-downloaded.txt').readlines()
        old_links_modulated = []
        for link in old_links:
            old_links_modulated.append(link[:-1])

        for link in image_links:
            if link not in old_links_modulated:
                new_links.append(link)
            else:
                print(link + " Has already been downloaded.")
        return new_links

    except FileNotFoundError:
        print("No old links")
        return image_links
