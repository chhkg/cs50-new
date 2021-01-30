import os
import datetime
import uuid
import traceback
import sys

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, send_from_directory, abort
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from jinja2 import Environment


from helpers import apology, login_required, lookup, usd

# Reference https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
Session(app)


def file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///album.db")

@app.route("/")
@app.route("/album")
@login_required
def albumlist():
    rows = db.execute("SELECT * FROM albumlist WHERE userid = :userid", userid = session.get("user_id"))
    image = db.execute("SELECT * FROM image WHERE userid = :userid AND status = 1", userid = session.get("user_id"))
    return render_template("albumlist.html", rows = rows, len = len(rows), imagelen = len(image), image = image)


@app.route("/album/<albumid>", methods=["GET", "POST"])
@login_required
def album(albumid):
    # image = os.listdir('static/uploads/')
    rows = db.execute("SELECT * FROM albumlist WHERE albumid = :albumid AND userid = :userid",
                          albumid=albumid, userid = session.get("user_id"))
    image = db.execute("SELECT * FROM image WHERE albumid = :albumid AND userid = :userid AND status = 1",
                          albumid=albumid, userid = session.get("user_id"))

    # upload images
    if request.method == 'POST':
    # check if the post request has the file part
    # Reference https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
    # Reference: https://medium.com/dev-genius/get-started-with-multiple-files-upload-using-flask-e8a2f5402e20
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        for file in files:
            if file and allowed_file(file.filename):
                timestring = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = (secure_filename(file.filename))
                savefilename = (str(session["user_id"]) + '_' + timestring + '_' + uuid.uuid4().hex + '.' + file_extension(filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(session.get("user_id")), savefilename))

                db.execute("INSERT INTO image (userid, albumid, oriname, savename) VALUES(:userid, :albumid, :oriname, :savename)",
                               userid = session.get("user_id"), albumid = albumid, oriname = filename, savename = savefilename)
                db.execute("UPDATE albumlist SET imagecount = imagecount + 1 WHERE albumid = :albumid", albumid = albumid)

        return redirect(request.url)
    else:
        return render_template("inalbum.html", rows = rows, albumid = albumid, len_img = len(image), image = image, userid = session.get("user_id"))


# Allow users to access their own files
# Reference: https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
@app.route('/static/uploads/<savefilename>')
@login_required
def image(savefilename):
    return send_from_directory(os.path.join(
        app.config['UPLOAD_FOLDER'], str(session.get("user_id"))), savefilename)


# Allow users to delete images
# Reference: https://stackoverflow.com/questions/61799618/flask-how-to-delete-files-from-the-server
@app.route('/remove/<savename>')
def remove(savename):
    db.execute("UPDATE image SET status = 0 WHERE savename = :savename", savename = savename)
    targetalbum = db.execute("SELECT * FROM image WHERE savename = :savename", savename = savename)
    db.execute("UPDATE albumlist SET imagecount = imagecount - 1 WHERE albumid = :targetalbum", targetalbum = targetalbum[0]["albumid"])
    flash('File Deleted!')
    return redirect(request.referrer)


@app.route("/createalbum", methods=["GET", "POST"])
@login_required
def createalbum():
    if request.method == "POST":
        # Ensure album name was submitted
        if not request.form.get("albumname"):
            return apology("must provide album name", 403)

        # Insert the album into db
        else:
            db.execute("INSERT INTO albumlist (userid, albumname) VALUES(:userid, :albumname)",
                              userid = session.get("user_id"), albumname = request.form.get("albumname"))
            flash('Album Created!')
            return redirect("/")
    else:
        return render_template("createalbum.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Log user in

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userid"]
        flash('Welcome back!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 403)

        # Ensure password confirmation was the same as password
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("must provide the same password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username not occupied
        if len(rows) == 1:
            return apology("choose another username", 403)

        # Insert the new user to db
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                              username = request.form.get("username"), hash = generate_password_hash(request.form.get("password"), method='sha256'))

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        session["user_id"] = rows[0]["userid"]

        flash('Registered!')

        foldername = "static/uploads/" + str(session.get("user_id"))

        os.makedirs(foldername)

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
