import praw

import download_functions as dl

r = praw.Reddit(user_agent="Wallpaper switcher V0.1.1 by /u/Pusillus")

print("Fetching urls...")
# Get image urls
image_urls = dl.get_top_image(r.get_subreddit("wallpapers"))

# Check if links has been downloaded
# TODO: Use better way to store downloaded links
image_urls = dl.check_links(image_urls)

# Write new links to file
dl.write_links(image_urls)

# Downloda images
dl.download_images(image_urls)
