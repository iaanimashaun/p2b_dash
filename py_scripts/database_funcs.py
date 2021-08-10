import pymongo as pm
import bson
import bcrypt
import os
import time
from dotenv import load_dotenv, find_dotenv
import urllib
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv(find_dotenv())

heroku = False


def connect_to_db():
    if heroku:
        s1 = os.environ["MONGODBURL1"]
        pwd = os.environ["MONGODBPWD"]
        s2 = os.environ["MONGODBURL2"]
        client = pm.MongoClient(s1 + urllib.parse.quote(pwd) + s2)
        return client
    else:
        s1 = os.environ.get("MONGODBURL1")
        pwd = os.environ.get("MONGODBPWD")
        s2 = os.environ.get("MONGODBURL2")
        client = pm.MongoClient(s1 + urllib.parse.quote(pwd) + s2)
        return client

def verify_login(email, pwd):
    db = connect_to_db().Streamers

#    db = connect_to_db().Streamers
    users_col = db["users"]
    user = users_col.find_one({"email":email})
    if check_password_hash(user['password'], pwd): #bcrypt.checkpw(pwd.encode('utf8'), user["password"]):
        print("password match")
        orgId = str(user["orgId"])
        userId = str(user["_id"])
        return True, orgId, userId
    return False, "", ""

def new_company_reg(org, email, first_name, last_name, phone, password):
    db = connect_to_db().Streamers
    org_col = db["orgs"]
    users_col = db["users"]
    # check if org exists
    if org_col.find_one({"org":org}):
        # org already exists
        return False, "Organisation already exists!", None
    if org_col.find_one({"email":email}):
        return  False, "Email already exists", None
    pwd =  generate_password_hash(password)  #bcrypt.hashpw(password, bcrypt.gensalt())
    objId = bson.objectid.ObjectId()
    new_comp = {'_id':objId,"org":org, "email":email, "contactFirst": first_name,
                "contactLast":last_name, "contactPhone":phone}
    new_user = {"orgId":objId,"firstName": first_name, "lastName": last_name,
                "email": email, "password": pwd, "rank":"admin"}
    user_id = ""
    try:
        r = org_col.insert_one(new_comp)
        u = users_col.insert_one(new_user)
        user_id = u.inserted_id
        print("r is", r)
        print("u is ", u.inserted_id)
    except:
        print("An error occurred add to db")
        return False, "Something went wrong, please try again", None

    return True, str(user_id), str(objId)


def new_user_reg():
    pass

def new_video_upload(secure_url, name, orgId, productListProvided):
    db = connect_to_db().Streamers
    vid_col = db['videos']
    new_vid = {"orgId":orgId, "vidName":name, "url":secure_url, "active":False, "productListProvided": productListProvided}
    try:
        vid_col.insert_one(new_vid)
    except:
        print("upload failed")
        return False
    video = vid_col.find_one({"vidName":name, "url":secure_url})
    vidId = video["_id"]
    return True, vidId

def check_vid_name(orgID, name):
    # check if the video name exists so we don't overite them
    db = connect_to_db().Streamers
    vid_col = db['videos']
    r = vid_col.count_documents({"orgId":orgID, "vidName":name})
    return r

def count_uploaded_active_videos(orgId):
    db = connect_to_db().Streamers
    vid_col = db['videos']
    u = vid_col.count_documents({"orgId":orgId})
    a = vid_col.count_documents({"orgId":orgId, "active":True})
    return u,a

def new_productList_upload(orgID, productList, vidName, vidId):
    db = connect_to_db().Streamers
    prod_col = db["productList"]
    for i in range(0, len(productList)):
        print(i)
        new_product = {"orgId": orgID,
                        "vidId": vidId, 
                        "productName": productList[i]["productName"], 
                        "brandName": productList[i]["brandName"], 
                        "TC": productList[i]["TC"],
                        "numberOfScenes": productList[i]["numberOfScenes"],
                        "paidProductPlacement": productList[i]["paidProductPlacement"],
                        "vidName": vidName}
        try:
            prod_col.insert_one(new_product)
        except:
            print("insert failed")
            return False
    return True



