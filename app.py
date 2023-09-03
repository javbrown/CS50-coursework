from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date


from helpers import apology, login_required, fage, tdate, cclearance

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# This route gathers all the info i have entered into my database and displays it to my index.html page
@app.route("/", methods=["GET"])
@login_required
def index():
    dates = db.execute("SELECT date FROM history WHERE userid = ?", session["user_id"])
    bmis = db.execute("SELECT bmi FROM history WHERE userid = ?", session["user_id"])
    age = db.execute("SELECT age FROM users WHERE id = ?", session["user_id"])
    weight = db.execute("SELECT weight FROM results WHERE id = ?", session["user_id"])
    creatinine= db.execute("SELECT creatinine FROM results WHERE id = ?", session["user_id"])
    sex = db.execute("SELECT sex FROM results WHERE id = ?", session["user_id"])
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    meds = db.execute("SELECT * FROM meds WHERE id = ?", session["user_id"])
    conditions = db.execute("SELECT * FROM conditions WHERE id = ?", session["user_id"])
    height = db.execute("SELECT height FROM results WHERE id = ?", session["user_id"])
    smoker = db.execute("SELECT smoker FROM results WHERE id = ?", session["user_id"])

    # calculate the creatinine clearance depending on if the user is male of female

    user = db.execute("SELECT * FROM results WHERE id = ?", session["user_id"])
    if len(user) == 0:
        return redirect("/account")

    if sex[0]["sex"] == None:
        crcl = "please enter sex in account"
    elif sex[0]["sex"] == "female":
        if creatinine[0]["creatinine"] == None:
            crcl = "Please enter a serum Creatinine in results"
        elif weight[0]["weight"] == None:
            crcl = "Please enter a serum weight in account"
        else:
            crcl = round(cclearance(int(age[0]["age"]), int(weight[0]["weight"]), int(creatinine[0]["creatinine"])) * 0.85, 1)
    else:
        if creatinine[0]["creatinine"] == None:
            crcl = "Please enter a serum Creatinine in results"
        elif weight[0]["weight"] == None:
            crcl = "Please enter a serum weight in account"
        else:
            crcl = round(cclearance(int(age[0]["age"]), int(weight[0]["weight"]), int(creatinine[0]["creatinine"])), 1)
    date = []
    bmi = []

    myage = age[0]["age"]
    myusername = username[0]["username"].upper()
    mysex = sex[0]["sex"]
    myheight = height[0]["height"]
    myweight = weight[0]["weight"]
    mysmoker = smoker[0]["smoker"]

    # ignore gaps in my databases and adds the values to the relevent lists
    for i in range(len(dates)):
        if dates[i]["date"] == None:
            continue
        else:
            date.append(dates[i]["date"])
    for i in range(len(bmis)):
        if bmis[i]["bmi"] == None:
            continue
        else:
            bmi.append(bmis[i]["bmi"])

    return render_template("index.html", date=date, bmi=bmi, crcl=crcl, myage=myage, myusername=myusername, meds=meds, conditions=conditions, mysex=mysex, myheight=myheight, myweight=myweight, mysmoker=mysmoker)

# This route allows the user to add health conditions to the conditions database
@app.route("/pms", methods=["GET", "POST"])
@login_required
def pms():
    if request.method == "POST":
        if not request.form.get("condition"):
            return apology("Please enter a condition", 400)
        db.execute("INSERT INTO conditions (id, condition) VALUES(?, ?)", session["user_id"], request.form.get("condition"))
        return redirect("/pms")
    else:
        history = db.execute("SELECT * FROM conditions WHERE id = ?", session["user_id"])
        return render_template("pms.html", history=history)


# This route allows users to remove conditions from the database
@app.route("/removepms", methods=["POST"])
def removepms():
    condition = request.form.get("condition")

    if condition:
        db.execute("DELETE FROM conditions WHERE condition = ? AND id = ?", condition, session["user_id"])
    return redirect("/pms")

# This route allows the user to add medications to the meds database

@app.route("/meds", methods=["GET", "POST"])
@login_required
def meds():
    if request.method == "POST":
        if not request.form.get("med"):
            return apology("Please enter a medication", 400)
        elif not request.form.get("dose"):
            return apology("Please enter a dose", 400)
        elif not request.form.get("freq"):
            return apology("Please enter a frequency", 400)

        db.execute("INSERT INTO meds (id, medication, dose, frequency) VALUES(?, ?, ?, ?)", session["user_id"], request.form.get("med"), request.form.get("dose"), request.form.get("freq"))
        return redirect("/meds")

    else:
        med = db.execute("SELECT * FROM meds WHERE id = ?", session["user_id"])
        return render_template("meds.html", med=med)

# This route allows users to remove meds from the database

@app.route("/removemed", methods=["POST"])
def removemed():
    med = request.form.get("med")

    if med:
        db.execute("DELETE FROM meds WHERE medication = ? AND id = ?", med, session["user_id"])
    return redirect("/meds")

# This route allows users to add tests to the results and history database.
@app.route("/test", methods=["GET", "POST"])
@login_required
def test():
    if request.method == "POST":
        today = date.today()
        rows = db.execute("SELECT * FROM results WHERE id = ?", session["user_id"])
        if rows == 0:
            db.execute("INSERT INTO results (id, fbc, creatinine, egfr) VALUES(?, ?, ?, ?)", session["user_id"], request.form.get("fbc"), request.form.ger("creatinine"), request.form.get("egfr"))
            db.execute("INSERT INTO history (userid, fbc, creatinine, egfr, date) VALUES(?, ?, ?, ?, ?)", session["user_id"], request.form.get("fbc"), request.form.ger("creatinine"), request.form.get("egfr"), today)
            return redirect("/test")
            # If not all fields are entered, i will use the latest value that is in the results table and update the history table with that value
        else:
            if not request.form.get("fbc"):
                fbc = db.execute("SELECT fbc FROM results WHERE id = ?", session["user_id"])
                fbc = fbc[0]["fbc"]
            else:
                fbc = request.form.get("fbc")
            if not request.form.get("creatinine"):
                creatinine = db.execute("SELECT creatinine FROM results WHERE id = ?", session["user_id"])
                creatinine = creatinine[0]["creatinine"]
            else:
                creatinine = request.form.get("creatinine")
            if not request.form.get("egfr"):
                egfr = db.execute("SELECT egfr FROM results WHERE id = ?", session["user_id"])
                egfr = egfr[0]["egfr"]
            else:
                egfr = request.form.get("egfr")
            db.execute("UPDATE results SET fbc = ?, creatinine = ?, egfr = ? WHERE id = ?", fbc, creatinine, egfr, session["user_id"])
            udate = db.execute("SELECT date FROM history WHERE userid = ?", session["user_id"])
            for i in range(len(udate)):
                if tdate(udate[i]["date"]) == today:
                    db.execute("UPDATE history SET fbc = ?, creatinine = ?, egfr = ? WHERE date = ? AND userid = ?", fbc, creatinine, egfr, today, session["user_id"])
                    return redirect("/test")
            db.execute("INSERT INTO history (userid, fbc, creatinine, egfr, date) VALUES(?, ?, ?, ?, ?)", session["user_id"], fbc, creatinine, egfr, today)
            return redirect("/test")
    else:
        user = db.execute("SELECT * FROM results WHERE id = ?", session["user_id"])
        if len(user) == 0:
            return redirect("/account")
        else:
            return render_template("test.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide unique username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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
    if request.method == "POST":

        # endure DoB was submitted
        if not request.form.get("birthday"):
            return apology("must provide a DoB", 400)

        # Ensure username was submitted
        elif not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords do not match")
        else:
            hash = generate_password_hash(request.form.get("password"))

        dob = request.form.get("birthday")
        # fage meand function age
        age = fage(dob)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 0:
            return apology("Username in use", 400)
        else:
            db.execute("INSERT INTO users (username, hash, age, dob) VALUES(?, ?, ?, ?)", request.form.get("username"), hash, int(age), dob)

        nrow = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = nrow[0]["id"]

        # Redirect user to home page
        return redirect("/account")

    else:
        return render_template("register.html")


# This route allows the user to input information about them selfs
@app.route("/account", methods=["GET", "POST"])
@login_required
def info():
    if request.method == "POST":

        today = date.today()

        rows = db.execute("SELECT * FROM results WHERE id = ?", session["user_id"])
        if len(rows) == 0:

            if request.form.get("ethnicity") == "Choose Ethnicity":
                return apology("Please provide an ethnicity", 400)
            elif not request.form.get("height"):
                return apology("Please provide a height and weight", 400)
            elif not request.form.get("weight"):
                return apology("please provide a height and weight", 400)

            db.execute("INSERT INTO results (id, ethnicity, height, weight, smoker, sex) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], request.form.get("ethnicity"), request.form.get("height"), request.form.get("weight"), request.form.get("smoker"), request.form.get("sex"))
            height = db.execute("SELECT height FROM results WHERE id = ?", session["user_id"])
            weight = db.execute("SELECT weight FROM results WHERE id = ?", session["user_id"])


            bmi = float(weight[0]["weight"]) / (float(height[0]["height"]) ** 2)
            db.execute("INSERT INTO history (userid, height, weight, bmi, date) VALUES(?, ?, ?, ?, ?)", session["user_id"], request.form.get("height"), request.form.get("weight"), round(bmi, 2), today)
            return redirect("/account")
        else:
            if not request.form.get("height"):
                height = db.execute("SELECT height FROM results WHERE id = ?", session["user_id"])
                height = height[0]["height"]
            else:
                height = request.form.get("height")
            if not request.form.get("weight"):
                weight = db.execute("SELECT weight FROM results WHERE id = ?", session["user_id"])
                weight = weight[0]["weight"]
            else:
                weight = request.form.get("weight")
            if not request.form.get("sex"):
                sex = db.execute("SELECT sex FROM results WHERE id = ?", session["user_id"])
                sex = sex[0]["sex"]
            else:
                sex = request.form.get("sex")
            if not request.form.get("smoker"):
                smoker = db.execute("SELECT smoker FROM results WHERE id = ?", session["user_id"])
                smoker = smoker[0]["smoker"]
            else:
                smoker = request.form.get("smoker")
            if request.form.get("ethnicity") == "Choose Ethnicity":
                ethnicity = db.execute("SELECT ethnicity FROM results WHERE id = ?", session["user_id"])
                ethnicity = ethnicity[0]["ethnicity"]
            else:
                ethnicity = request.form.get("ethnicity")


            bmi = float(weight) / (float(height) ** 2)
            db.execute("UPDATE results SET ethnicity = ?, height = ?, weight = ?, sex = ?, smoker = ? WHERE id = ?", ethnicity, height, weight, sex, smoker, session["user_id"])
            udate = db.execute("SELECT date FROM history WHERE userid= ?", session["user_id"])
            for i in range(len(udate)):
                if tdate(udate[i]["date"]) == today:
                    db.execute("UPDATE history SET height = ?, weight = ?, bmi = ? WHERE userid = ? AND date = ?", height, weight, round(bmi, 2), session["user_id"], today)
                    return redirect("/account")
            db.execute("INSERT INTO history (userid, height, weight, bmi, date) VALUES(?, ?, ?, ?, ?)", session["user_id"], height, weight, round(bmi, 2), today)
            return redirect("/account")
    else:
        return render_template("account.html")

# This route allows users to change their password
@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        if not request.form.get("old_password") or not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            return apology("must provide your old password", 403)

        # Ensure password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide a new password", 403)

        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 403)

        elif request.form.get("confirmation") != request.form.get("new_password"):
            return apology("passwords do not match")
        else:
            hash = generate_password_hash(request.form.get("new_password"))

        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])
        return redirect("/")

    else:
        return render_template("account.html")