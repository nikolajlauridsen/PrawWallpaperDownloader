import praw

import download_functions as dl
from db_handler import Db_handler

r = praw.Reddit(user_agent="Wallpaper switcher V0.1.1 by /u/Pusillus")
db = Db_handler()

print("Fetching urls...")
# Get image urls
submissions = dl.get_top_image(r.get_subreddit("wallpapers"))

# Check if links has been downloaded
submissions = db.check_links(submissions)

# Write links to database
for sumbission in submissions:
    db.insert_link(sumbission)

# Download images
dl.download_images(submissions)

# Save changes to Database
db.save_changes()
