import praw
import requests
import os

r = praw.Reddit(user_agent="Wallpaper switcher V0.1 by /u/Pusillus")


# Get image link of most upvoted wallpaper of the day
def get_top_image(subreddit):
    dl_urls = []
    for submission in subreddit.get_top(limit=25):
        url = submission.url
        if url.endswith(".jpg") or url.endswith(".png"):
            dl_urls.append(url)
        # Imgur support
        elif ("imgur.com" in url) and ("/a/" not in url):
            if url.endswith("/new"):
                url = url.rsplit("/", 1)[0]
            id = url.rsplit("/", 1)[1].rsplit(".", 1)[0]
            dl_urls.append("http://imgur.com/" + id + ".jpg")
    return dl_urls

print("Fetching urls...")
# Get Urls
image_urls = get_top_image(r.get_subreddit("wallpapers"))
image_n = 0
total_images = len(image_urls)

for url in image_urls:
    print("Downloading image" + str(image_n+1) + "/" + str(total_images))
    # Send request
    response = requests.get(url)

    # Save image to disk
    if response.status_code == 200:
        file_path = os.path.join('images', str(image_n) + ".jpg")
        f = open(file_path, 'wb')
        for chunk in response.iter_content(10000):
            f.write(chunk)
        f.close()
    image_n += 1
