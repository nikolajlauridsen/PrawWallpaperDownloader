# PrawWallpaperDownloader (Python3)

Download a bunch of wallpapers from the hot sections of r/wallpapers (or specify your own subreddit!)

Going into a little more detail the script will:

1. Query Reddit for an amount of posts (25 by default)
2. Sift through the links finding direct image links and imgur posts
3. It will check whether any of the links has been downloaded before, sorting out those who has 
4. Download all the now sorted links
5. Go through all downloaded images deleting any images less than 1280x720 (Enter configuration mode to change this)


Inspirations is drawn from [Daily-Reddit-Wallpaper](https://github.com/ssimunic/Daily-Reddit-Wallpaper)

## Install process
1. Download and install python from https://www.python.org/ (If you're unsure download version 3.5 and chose default install)
2. Clone or download/extract the repository
3. Install requirements with
```
py -m pip install -r requirements.txt
```
(You might have to use python or python3 instead of py depending on your system/install)

#### Requirements
* praw
* requests
* pillow

## Usage
The script can be run by double clicking prawpapers.py or via the commandline with the latter being the best option since the script accepts a variety of optional arguments

#### Examples
Basic use: search through the first 25 posts of /r/wallpapers
```
py prawpapers.py
```
"Advanced" use: Search the first 100 posts of /r/MinimalWallpaper and save a log
```
py prawpapers.py -s MinimalWallpaper -l 100 --log
```

### Optional arguments
* -con or --config enter configuration mode
* --subreddit \<subreddit> or -s \<subreddit> specify which subreddit to download images from, omit the /r/ (default is wallpapers)
* --limit \<number> or -l \<number> specify how many posts to search as a whole number (default is 25)
* --re or -r will try to re download every post previously downloaded
* --nc or --noclean don't delete small images
* --ns or --nosort skip sorting out previosuly downloaded images
* --log save a log of posts skipped
* --verbose or -v print skipped posts to console
