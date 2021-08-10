import cloudinary
import cloudinary.uploader
import os
import time
from dotenv import load_dotenv, find_dotenv
import urllib
load_dotenv(find_dotenv())
heroku = False

def config_cloudinary():
    if heroku:
        cloudinary.config(
            cloud_name=os.environ["CLOUDNAME"],
            api_key=os.environ["CLOUDKEY"],
            api_secret=os.environ["CLOUDSEC"])
    else:
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDNAME"),
            api_key=os.environ.get("CLOUDKEY"),
            api_secret=os.environ.get("CLOUDSEC"))

def upload_video(img, path):
    config_cloudinary()

    r = cloudinary.uploader.upload_large(img,
                                     resource_type="video",
                                     public_id = path)
    return r


