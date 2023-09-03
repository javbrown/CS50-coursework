from flask import redirect, render_template, session
from functools import wraps
from datetime import date


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

""" function that takes an date in the form of string and callculates the age"""
def fage(text):
    list_dob = text.split("-")
    today = date.today()
    int_list_dob = []
    for item in list_dob:
        int_list_dob.append(int(item))
    ndob = date(int_list_dob[0], int_list_dob[1], int_list_dob[2])
    # brackes will return true or false which = 1 or 0
    age = today.year - ndob.year - ((today.month, today.day) < (ndob.month, ndob.day))
    return age

"""a function that takes a date in a string format and turns it into a date object """
def tdate(text):
    list_date = text.split("-")
    int_list_date = []
    for item in list_date:
        int_list_date.append(int(item))
    ndate = date(int_list_date[0], int_list_date[1], int_list_date[2])
    return ndate

# a function to calculate creatinine clearance
def cclearance(age, weight, creatinine):
    crcl = ((140 - age) * weight)/(creatinine * 0.814)
    return crcl