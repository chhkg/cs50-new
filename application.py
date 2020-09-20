import os
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    rows = db.execute("SELECT * FROM portfolio WHERE userid = :userid", userid = session.get("user_id"))

    cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session.get("user_id"))

    # Calculate the total market value of user's portfolio
    total = 0
    for i in range(0, len(rows)):
        total = total + (rows[i]["share"] * rows[i]["avgprice"])

    return render_template("portfolio.html", rows = rows, cash = cash, len = len(rows), total = total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=request.form.get("username"))

    # User reached route via POST
    if request.method == "POST":

        # Ensure symbol submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        # Ensure shares submitted
        elif not request.form.get("share") or int(request.form.get("share")) < 1:
            return apology("must provide shares", 403)

        # Look up the latest price of the stock, case insensitive
        price = lookup(request.form.get("symbol"))
        buyprice = round(price["price"], 2)

        # return error if the symbol does not exist
        if not price:
            return apology("symbol not exist", 403)

        # return error if cannot afford
        cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session.get("user_id"))

        if buyprice * int(request.form.get("share")) > cash[0]["cash"]:
            return apology("can't afford", 403)

        else:
            # Calculate the total price of the transaction
            payment = buyprice * int(request.form.get("share"))

            # Update user's cash balance
            db.execute("UPDATE users SET cash = :balance WHERE id = :id", balance = cash[0]["cash"] - payment, id = session.get("user_id"))

            # Insert transaction record
            db.execute("INSERT INTO history (userid, stocksymbol, stockname, stockprice, share, time)\
                                             VALUES (:userid, :stocksymbol, :stockname, :stockprice, :share, :time)",
                                             userid = session.get("user_id"), stocksymbol = price["symbol"], stockname = price["name"],
                                             stockprice = buyprice, share = int(request.form.get("share")), time = datetime.datetime.now())

            # Search for the purchased stock in user's portfolio
            ownedshare = db.execute("SELECT avgprice, share FROM portfolio WHERE stocksymbol = :stocksymbol AND userid = :userid",
                                     stocksymbol = price["symbol"], userid = session.get("user_id"))

            # Insert stock into user's portfolio if no share for the purchased stock
            if not ownedshare:
                db.execute("INSERT INTO portfolio (userid, stocksymbol, stockname, avgprice, share)\
                                         VALUES (:userid, :stocksymbol, :stockname, :avgprice, :share)",
                                         userid = session.get("user_id"), stocksymbol = price["symbol"], stockname = price["name"],
                                                 avgprice = buyprice, share = int(request.form.get("share")))

            # Update stock share if user has owned the purchased stock
            else:
                # Calculate the new average price of the purchased stock in user's portfolio
                newavgprice = (ownedshare[0]["avgprice"] * ownedshare[0]["share"] + payment) / (ownedshare[0]["share"] + int(request.form.get("share")))

                db.execute("UPDATE portfolio SET avgprice = :avgprice, share = :share WHERE stocksymbol = :stocksymbol AND userid = :userid",
                             avgprice = newavgprice, share = ownedshare[0]["share"] + int(request.form.get("share")), stocksymbol = price["symbol"], userid = session.get("user_id"))

                # Redirect user to the portfolio page

            flash('Bought!')
            return redirect("/")

    # User reached route via GET
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    rows = db.execute("SELECT * FROM history WHERE userid = :userid", userid = session.get("user_id"))
    cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session.get("user_id"))
    return render_template("history.html", rows = rows, cash = cash, len = len(rows))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

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
        session["user_id"] = rows[0]["id"]
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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST
    if request.method == "POST":

        # Ensure symbol submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        # Look up the latest price of the stock, case insensitive
        price = lookup(request.form.get("symbol"))

        # return error if the symbol does not exist
        if not price:
            return apology("symbol not exist", 403)

        # return price
        else:
            return render_template("quoted.html", price=price)

    # User reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    #session.clear()

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
        session["user_id"] = rows[0]["id"]

        flash('Registered!')

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure share was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        if not request.form.get("share"):
            return apology("must provide shares", 403)

        stock = db.execute("SELECT * FROM portfolio WHERE userid = :userid AND stocksymbol = :stocksymbol",
                            userid = session.get("user_id"), stocksymbol = request.form.get("symbol"))

        # Ensure user doesn't sell more shares than he has
        if stock[0]["share"] < int(request.form.get("share")):
            return apology("cannot sell more than you have", 403)

        # Reduce the share of that stock and re-calculate the avg price
        else:
            new_share = stock[0]["share"] - int(request.form.get("share"))
            price = lookup(request.form.get("symbol"))
            sellprice = round(price["price"], 2)
            ownedshare = db.execute("SELECT avgprice, share FROM portfolio WHERE stocksymbol = :stocksymbol AND userid = :userid",
                                     stocksymbol = price["symbol"], userid = session.get("user_id"))
            cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session.get("user_id"))
            gain = sellprice * int(request.form.get("share"))

            if new_share < 0:
                return apology("please contact us for support", 403)

            # If the remaining share = 0, remove that stock from portfolio
            elif new_share == 0:
                db.execute("DELETE FROM portfolio WHERE stocksymbol = :stocksymbol AND userid = :userid",
                                             stocksymbol = request.form.get("symbol"), userid = session.get("user_id"))

                # Add a transaction history
                db.execute("INSERT INTO history (userid, stocksymbol, stockname, stockprice, share, time)\
                                             VALUES (:userid, :stocksymbol, :stockname, :stockprice, :share, :time)",
                                             userid = session.get("user_id"), stocksymbol = price["symbol"], stockname = price["name"],
                                             stockprice = sellprice, share = int(request.form.get("share")) * -1, time = datetime.datetime.now())
            else:
                # Calculate the new average price of the purchased stock in user's portfolio
                newavgprice = (ownedshare[0]["avgprice"] * ownedshare[0]["share"] - gain) / new_share

                # Update the portfolio
                db.execute("UPDATE portfolio SET avgprice = :avgprice, share = :share WHERE stocksymbol = :stocksymbol AND userid = :userid",
                             avgprice = newavgprice, share = new_share, stocksymbol = price["symbol"], userid = session.get("user_id"))

                # Add a transaction history
                db.execute("INSERT INTO history (userid, stocksymbol, stockname, stockprice, share, time)\
                                             VALUES (:userid, :stocksymbol, :stockname, :stockprice, :share, :time)",
                                             userid = session.get("user_id"), stocksymbol = price["symbol"], stockname = price["name"],
                                             stockprice = sellprice, share = int(request.form.get("share")) * -1, time = datetime.datetime.now())

            # Update user's cash balance
            db.execute("UPDATE users SET cash = :balance WHERE id = :id", balance = cash[0]["cash"] + gain, id = session.get("user_id"))

            flash('Sold!')

            return redirect("/")
    else:
        rows = db.execute("SELECT * FROM portfolio WHERE userid = :userid", userid = session.get("user_id"))
        return render_template("sell.html", rows = rows, len = len(rows))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
