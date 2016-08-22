# PrawWallpaperDownloader (Python3)

Download a bunch of wallpapers from the hot sections of r/wallpapers

Inspirations is drawn from [Daily-Reddit-Wallpaper](https://github.com/ssimunic/Daily-Reddit-Wallpaper)

### Requirements
* praw
* requests

### Usage
The script can be run by double clicking wallpaper_downloader.py or via the commandline with the latter being the best option since the script accepts a variety of optional arguments

#### Optional arguments
* --subreddit \<subreddit> or -s \<subreddit> specify which subreddit to download images from, omit the /r/ (default is wallpapers)
* --limit \<number> or -l \<number> specify how many posts to search as a whole number (default is 25)
* --re or -r will try to re download every post previously downloaded
* --log save a log of posts skipped
* --verbose or -v print skipped posts to console
