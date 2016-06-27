import praw
import requests
import os
import time

import download_functions as dl

r = praw.Reddit(user_agent="Wallpaper switcher V0.1.1 by /u/Pusillus")

print("Fetching urls...")
# Get Urls
image_urls = dl.get_top_image(r.get_subreddit("wallpapers"))

dl.download_images(image_urls)
