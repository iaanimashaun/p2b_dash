from flask import Flask, render_template, request, session, redirect, abort
from py_scripts import database_funcs as db
from py_scripts import cloudinary_funcs as cf
from py_scripts import twillo_funcs as tf
from py_scripts import parse_funcs as pf
import datetime
import os
application = Flask(__name__)
#app = application
application.secret_key = "EIL6DNq9HVTwh8LNKKIe" #os.urandom(24)
 


@application.route('/')
def hello_world():
    if session.get("org_id") and session.get('user_id'):
        return redirect("/dash_home") #render_template("dashboard_home.html")
    return render_template('login_base.html', message="", div_class="")

@application.route('/login_form', methods=['GET','POST'])
def login_user():
    if request.method == "GET":
        return "Not the right place Mate"
    if request.method == "POST":
        # do login functions and verify user in database
        print("email: ", request.form.get('email'))
        print("pass: ", request.form.get('password'))
        ok, orgId, message = db.verify_login(request.form.get("email"), request.form.get("password"))
        # message = db.verify_login(request.form.get("email"), request.form.get("password"))
        print("message: ", ok)

        if ok:
            session['org_id'] = orgId
            session["user_id"] = message
            session['rank'] = "admin"
            print(session['org_id'])
            return redirect('/dash_home')
        else:
            return render_template('login_base.html', message="Password or Username not recognised", div_class="alert alert-danger")

@application.route('/reg_company')
def reg_company():
    # show the registration page for new organisations
    return render_template('register.html', message="", div_class="")

@application.route("/new_company", methods=["GET", "POST"])
def new_company():
    if request.method == "POST":
        if request.form.get("password") == request.form.get("confirm_password"):
            good, message, orgId = db.new_company_reg(request.form.get("companyName"),
                               request.form.get("email"),
                               request.form.get("firstName"),
                               request.form.get("lastName"),
                               request.form.get("phone"),
                               request.form.get("password"))#.encode('utf8'))
            if good:
                print(message)
                session['org_id'] = orgId
                session["user_id"] = message
                session['rank'] = "admin"
                tf.send_confirmation_email(request.form.get("email"), request.form.get("firstName"))
                return render_template('dashboard_home.html')
            else:
                return render_template('register.html', message=message, div_class="alert alert-danger" )
        else:
            return render_template("register.html", message="Passwords do not match", div_class="alert alert-danger")

@application.route('/logout', methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        print("log out")
        # log them out
        session.clear()
        return render_template('login_base.html')

@application.route('/dash_home')
def dash_home():
    if session.get("org_id") and session.get('user_id'):
        upload_vids, active_vids = db.count_uploaded_active_videos(session.get("org_id"))
        return render_template("dashboard_home.html", upload_vids=upload_vids, active_vids=active_vids)
    else:
        return redirect("/")

@application.route('/upload_video', methods=["POST", "GET"])
def upload_video():
    # upload the file to cloudinary and details to mongo
    if request.method == "POST":
        name = request.form.get("videoTitle")
        if db.check_vid_name(session.get("org_id"), name) == 0:
            # create a cloud path containing the name of the video
            cloud_path = session.get("org_id")+'/uploaded_video/' + name
            print("path is ", cloud_path)
            # get the video file from the form
            vid_file = request.files['videoFile']
            print("vid file name", type(vid_file))
            # get the uploaded product list from the form
            productList = pf.parse_product_list(request.files["productListFile"],name)
            if len(productList):
                productListprovided = True
            else:
                productListprovided = False
           
            fp = os.path.join('./uploads/', vid_file.filename)
            vid_file.save(fp)

            # upload the video to cloudinary
            r = cf.upload_video(fp,cloud_path)
            videoUploaded, vidId = db.new_video_upload(r['secure_url'],name,session.get("org_id"), productListprovided)
            #os.remove(fp)
            print(r['secure_url'])
            if len(productList):
                good = db.new_productList_upload(session.get("org_id"), 
                                                    productList, 
                                                    name,
                                                    vidId)
                print("Products added to productList.")
            else:
                print("No productList was uploaded.")
            if videoUploaded:
                return redirect("/dash_home")
            else:
                # something wrong with the upload try again
                return redirect("/dash_home")
    return "not right"

@application.before_request
def before_request():
    session.permanent = True
    application.permanent_session_lifetime = datetime.timedelta(minutes=30)
    session.modified = True

if __name__ == '__main__':
    application.debug = True
    application.run()
