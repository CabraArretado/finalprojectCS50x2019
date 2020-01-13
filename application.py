import os
import json
from decorators import falhou, login_required, success

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date

# Declaring app
app = Flask(__name__)

# Reload templates on edition
app.config["TEMPLATES_AUTO_RELOAD"] = True

database = SQL("sqlite:///final.db")

""" Add a header after the request to ensure reponse isn't cached """
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

""" Session configuration """
# Create a temp directory to save session files
app.config["SESSION_FILE_DIR"] = mkdtemp()
# Make the session not permanent
app.config["SESSION_PERMANENT"] = False
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'POST':

        # Request data from the HTML form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        creator = int(request.form.get("creator"))
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")

        # Check if user provided the input
        if not username:
            return falhou("must provide a username", 403)
        elif not email:
            return falhou("must provide a email", 403)
        elif not password:
            return falhou("must provide a password", 403)
        elif not confirmation:
            return falhou("must provide the password confirmation", 403)
        elif not firstname or not lastname:
            return falhou("must provide a complete name", 403)

        # Check if the radar was marked
        elif creator != 0 and creator != 1:
            return falhou("must select a account type", 403)

        # Check if the password matchs with the confirmartion
        elif not password == confirmation:
            return falhou("password and confirmation don't match", 403)

        # Query database for username or email if username is in use it will return true and trigger the elif
        elif database.execute("SELECT * FROM users WHERE username = :username;", username=username):
            return falhou("username already in use")
        elif database.execute("SELECT * FROM users WHERE email = :email;", email=email):
            return falhou("email already in use")

        # If everything is fine, finally register the user and redirect
        else:
            # If the user is creating a event register it and redirect for register_event.hmtl
            if creator == 1:
                # Insert the values in the table
                database.execute("INSERT INTO users (user_id, username, password, firstname, lastname, creator, email) VALUES (NULL, :username, :password, :firstname, :lastname, :creator, :email);", username=username, password=generate_password_hash(password), firstname=firstname, lastname=lastname, creator=creator, email=email)

                # Assure that the user get in the register_event already logged in
                session["user_id"] = database.execute("SELECT * FROM users WHERE username = :username;", username=username)[0]["user_id"]

                # Redirect
                return render_template("register_event.html")

            # If the user is a guest he is asked the EVENT CODE, with that information the user is registred and checked in on the event
            if creator == 0:
                # Check if the EVENT CODE was provided
                event_code = request.form.get("event_code")
                if not event_code:
                    return falhou("must provide the EVENT CODE.\n Talk with the hoster of the event you intend to check presence and ask about the EVENT CODE. Such code is made by 6 digits. Without this code is impossible check up", 403)

                # Check if the EVENT CODE provided exists
                if not database.execute("SELECT * FROM events WHERE event_code = :event_code;", event_code=event_code):
                    return falhou("EVENT CODE provided isn't on database")

                # Request from the database the event_id from the provided EVENT CODE
                event_id = database.execute("SELECT * FROM events WHERE event_code = :event_code;", event_code=event_code)[0]["event_id"]


                # Register the user in the database
                database.execute("INSERT INTO users (user_id, username, password, firstname, lastname, creator, email, linked_event_id) VALUES (NULL, :username, :password, :firstname, :lastname, :creator, :email, :event_code);", username=username, password=generate_password_hash(password), firstname=firstname, lastname=lastname, creator=creator, email=email, event_code=event_code)

                # Save season and redirect to index
                session["user_id"] = database.execute("SELECT * FROM users WHERE username = :username;", username=username)[0]["user_id"]
                return redirect("/")


    else:
        return render_template("register.html")

@app.route("/register_event", methods=["GET", "POST"])
def register_event():
    """ Register Event """
    if request.method == 'POST':

        # Request data from the HTML form
        eventName = request.form.get("eventName")
        hosterName = request.form.get("hosterName")
        hosterPhone = request.form.get("hosterPhone")
        inputDate = request.form.get("inputDate")
        inputTime = request.form.get("inputTime")
        event_code = request.form.get("event_code")


        # Requesting and formating address filds in a dictionary
        inputAddress = request.form.get("inputAddress")
        inputCity = request.form.get("inputCity")
        inputState = request.form.get("inputState")
        inputZip = request.form.get("inputZip")
        inputAddress2 = request.form.get("inputAddress2")

        # As the secound line of address is opitional this line make it and the first one an unique line.
        if inputAddress2:
            inputAddress = inputAddress + " " + inputAddress2
        address = {"streetNumber": inputAddress, "city": inputCity, "state": inputState, "zip": inputZip}

        # Check if the input were provided
        if not eventName:
            return falhou("Must provide event's name")
        if not hosterName:
            return falhou("Must provide hoster's name")
        if not hosterPhone:
           return falhou("Must provide hoster's phone")
        if not inputDate or not inputTime:
            return falhou("Must provide complete data and time of the event")
        if not inputAddress or not inputCity or not inputState or not inputZip:
            return falhou("Must provide complete address")
        if not event_code:
            return falhou("Must provide complete an EVENT CODE")

        # Check if the event code is original
        if database.execute("SELECT * FROM events WHERE event_code = :event_code;", event_code=event_code):
            return falhou("EVENT CODE already in use. Try a new one.")

        # Everything being correct the event is finally registered in the database and the user redirected to the index
        database.execute("INSERT INTO events (owner_id, event_id, event_name, date, time, hoster_name, hoster_phone, address, event_code) VALUES (:user, NULL, :eventName, :inputDate, :inputTime, :hosterName, :hosterPhone, :address, :event_code);", user=session["user_id"], eventName=eventName, inputTime=inputTime, inputDate=inputDate, hosterName=hosterName, hosterPhone=hosterPhone, address=json.dumps(address), event_code=event_code)
        return redirect("/")

    else:
        return render_template("register_event.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # User submit the login and password via POST
    if request.method == "POST":

        # Cleaning former season
        session.clear()

        # Request the login and password input from the HTML
        username = request.form.get("username")
        password = request.form.get("password")


        # Check if a username and a password are submited
        if not username:
                return falhou("must provide a username", 403)
        if not password:
                return falhou("must provide a password", 403)

        # Check the if there is such username in the database and check password
        userquery = database.execute("SELECT * FROM users WHERE username = :username;", username=username)

        if len(userquery) != 1 or not check_password_hash(userquery[0]["password"], password):
            return falhou("invalid username/password", 403)

        # Remember the user logged
        else:
            session["user_id"] = userquery[0]["user_id"]

        # Redirect for the index
            return redirect("/")

    # If method GET render login HTML
    else:
         return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to /login
    return redirect("/")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """ Index page """
    if request.method == "POST":
        # Easter Egg
        print("Hello, world!")
    else:
        # Requesting user data from database as a dictionary
        user = database.execute("SELECT * FROM users WHERE user_id = :user_id;", user_id=session["user_id"])[0]

        # Creating the variables that may be used as empty dictionary
        place = {}
        eventQuery = {}

        # Setting data if the user is a creator
        if user["creator"]:

            # Checking if the creator user has a event in the database
            eventQuery = database.execute("SELECT * FROM events WHERE owner_id = :user_id;", user_id=session["user_id"])
            if eventQuery:

                # Change the eventQuery to the actual dictionary
                eventQuery = database.execute("SELECT * FROM events WHERE owner_id = :user_id;", user_id=session["user_id"])[0]

                # Create the adress dictionary
                place = json.loads(eventQuery["address"])



        # Setting data if the user is a guest
        elif not user["creator"]:

            # Requesting data of the event the user guest is linked with
            eventQuery = database.execute("SELECT * FROM events WHERE event_code = :event_code;", event_code=user["linked_event_id"])[0]

            # Saving event's address data as a dictionary
            place = json.loads(eventQuery["address"])

        # Redirect to index
        return render_template("index.html", user=user, creator=user["creator"], eventQuery=eventQuery, place=place)

@app.route("/guest_list", methods=["GET"])
@login_required
def guest_list():
    """ Guest List """

    # Request the data of the event in the database
    eventQuery = database.execute("SELECT * FROM events WHERE owner_id = :user_id;", user_id=session["user_id"])[0]
    guestList = database.execute("SELECT * FROM users WHERE linked_event_id = :event_id AND presence = 1;", event_id=eventQuery["event_code"])

    # Render the guest list
    return render_template("guest_list.html", guestList=guestList)


@app.route("/checkin", methods=["GET"])
@login_required
def checkin():
    ''' Check guest presence '''

    # Request data from the database
    user = database.execute("SELECT * FROM users WHERE user_id = :user_id;", user_id=session["user_id"])[0]
    guestList = json.loads(database.execute("SELECT * FROM events WHERE event_code = :event_code;", event_code=user["linked_event_id"])[0]["guest_list"])

    # Function to mark in the historic (presence list) who marked presence even if he mark it off later
    guestList[str(session["user_id"])] = 0

    # Update the database with the presence
    database.execute("UPDATE events SET guest_list = :guest_list WHERE event_code = :event_code;", guest_list=json.dumps(guestList), event_code=user["linked_event_id"])
    database.execute("UPDATE users SET presence = :presence WHERE user_id = :user_id;", presence=True, user_id=session["user_id"])

    return success("You have confirmed presence!")

@app.route("/markoff", methods=["GET"])
@login_required
def markoff():
    ''' Mark off presence '''
    database.execute("UPDATE users SET presence = :presence WHERE user_id = :user_id;", presence=False, user_id=session["user_id"])
    return success("You have marked off presence!")



