"""
Script which downloads every post saved in the database
"""
import download_functions as dl
from db_handler import Db_handler

db = Db_handler()

print("Getting urls from database")
posts = db.get_posts()

print("Downloading images...")

dl.download_images(posts)
