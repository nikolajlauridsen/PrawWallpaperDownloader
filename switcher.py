import praw

import download_functions as dl
from db_handler import Db_handler

r = praw.Reddit(user_agent="Wallpaper switcher V0.1.1 by /u/Pusillus")
db = Db_handler()

print("Fetching urls...")
# Get image urls
image_urls = dl.get_top_image(r.get_subreddit("wallpapers"))

# Check if links has been downloaded
image_urls = db.check_links(image_urls)

# Write links to database
for sumbission in image_urls:
    db.insert_link(sumbission)

# Download images
dl.download_images(image_urls)

# Save changes to Database
db.save_changes()
