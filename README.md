# PrawPapers (Praw Wallpaper Downloader)

Download a bunch of wallpapers from the hot sections of r/wallpapers

It doesn't even have to be wallpapers! PrawPapers will download images from any subreddit

Going into a little more detail the script will:

1. Query Reddit for an amount of posts (25 by default)
2. Sift through the reddit posts finding direct image links and imgur posts/albums
3. Extract all image links from any imgur albums found and add them to the link pool
4. Check whether any of the links has been downloaded before, sorting out those who has
5. Download all the now sorted links
6. Go through all downloaded images deleting images smaller than the minimum size, and those with a different aspect ratio

The configuration mode lets you tweak almost all settings to your desire, including but not limited to:
* Default subreddit
* Minimum image dimensions
* Amound of posts to sift through
* And more

Inspirations is drawn from [Daily-Reddit-Wallpaper](https://github.com/ssimunic/Daily-Reddit-Wallpaper)

#### Features
* Sort by size
* Sort by aspect ratio
* Multi threaded download for fast downloading
* Database functionality ensuring no redownloads and allows you to keep track of images downloaded
* Scrape by section
* Scrape by subreddit search
* Imgur album support (up to 10 images pr. album, will hopefully be improved)
* Customize behaviour to your liking through an easy to use configurator
* Logging functionality

## Install process
1. Download and install python from https://www.python.org/ (If you're unsure download version 3.5 and chose default install)
2. Clone or download/extract the repository
3. Install requirements with
```
py -m pip install -r requirements.txt
```
(You might have to use python or python3 instead of py depending on your system/install)
4. Set up your client_secret.json file

### Setting up your client_secret.json file
The new version of praw requires you to identify the script before you can use it, this is fortunately quite easy, just follow the steps below.
1. Go to [this page on reddit](https://www.reddit.com/prefs/apps/) (you might have to log in)
2. Scroll down to the bottom and click the "Create another app" button
3. Tick off 'script' and fill out the remaining boxes
4. You'll now be able to see your app in the list
5. Open your client_secret.json file in your favourite text editor
6. Replace YOUR-CLIENT-ID with the weird line of characters under the "personal use script" label, keep the quotations (See screenshot)
7. Repeat step 6 for the YOUR-CLIENT-SECRET field, this time using the characters next to the "secret" label (See screenshot)

![Client secret guide](https://raw.githubusercontent.com/nikolajlauridsen/PrawWallpaperDownloader/master/documentation/client_secret_guide.png)

#### Requirements
* praw
* requests
* bs4
* pillow

## Usage
The script can be run by double clicking prawpapers.py or via the commandline with the latter being the best option since the script accepts a variety of optional arguments

#### Examples
Basic use: search through the first 25 posts of /r/wallpapers
```
py prawpapers
```
"Advanced" use: Search the first 100 posts of /r/MinimalWallpaper and save a log
```
py prawpapers -s MinimalWallpaper -l 100 --log
```

### Optional arguments
* -con or --config enter configuration mode
* --subreddit \<subreddit> or -s \<subreddit> specify which subreddit to download images from, omit the /r/ (default is wallpapers)
* --limit \<number> or -l \<number> specify how many posts to search as a whole number (default is 25)
* --threads \<number> or -t \<number> specify how many download threads to spawn
* --re or -r will try to re download every post previously downloaded
* --nc or --noclean don't delete small images
* --ns or --nosort skip sorting out previosuly downloaded images
* --na or --noalbum skip imgur albums
* --log save a log of posts skipped
* --verbose or -v print skipped posts to console
* --section or -se \<section> Specify which section you want to scrape (hot, new, top, rising)
* --ratiolock or -rlock \<lock strength> Lock downloaded images to a certain aspect ratio, the value of the lock will determine the allowed margin of error, 0 for no lock, 1 for fully locked (only exactly matching aspect ratios), I recommend a value between 0.9 and 1 for decent results.
* --search or -q \<query> scrape all search results of chosen subreddit