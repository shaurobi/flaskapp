from flask import Flask, render_template, flash, request, redirect, url_for, jsonify, json, session
from app import app
from .forms import ExampleForm
import pprint as pp
from config import Config

from .ciscowebex import Webex
import urllib
from datetime import datetime, timedelta
import pytz
import random
import string

app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
clientID = Config.clientID
secretID = Config.secretID
redirectURI = Config.redirectURI


# - - - Routes - - -

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main Grant page"""
    redirect_URI = urllib.parse.quote_plus(redirectURI)
    return render_template('index.html', client_ID=clientID, redirect_URI=redirect_URI)



@app.route("/oauth")
def oauth():
    """Retrieves oauth code to generate tokens for users"""
    state = request.args.get("state") #Captures value of the state.
    if "code" in request.args and state == "set_state_here":
        code = request.args.get("code") #Captures value of the code.
        result, access_token, expires_in, refresh_token, refresh_token_expires_in = Webex.get_oauth_tokens(clientID, secretID, code, redirectURI)
        print ("get tokens result: " + result)
        if result == "Success":
            personID, emailID, displayName, status, avatar = Webex.get_user_info(access_token)
            token_expires = datetime.now() + timedelta(seconds=expires_in)
            refresh_expires = datetime.now() + timedelta(seconds=refresh_token_expires_in)
            data ={ 
                "access_token" : access_token, 
                "expires" : token_expires, 
                "refresh_token" : refresh_token, 
                "refresh_token_expires" : refresh_expires
            }
            json_object = json.dumps(data, indent = 4)
            writeToJSON('user', json_object)
            session['user'] = personID
            session['user_name'] = displayName
            session['avatar'] = avatar
            return render_template("main.html", expires=token_expires)
        else:
            flash(result, 'error')
            return render_template("index.html")
    else:
        return render_template("index.html")

@app.route("/join", methods = ['GET', 'POST']) 
def join():
    if request.method == 'POST':
        print (request.data)
        json_data = request.json
        MRN = json_data["MRN"]
        UserID = json_data["UserID"]
        TZ = "Australia/Sydney"
        Duration = 60
        date_now = datetime.now()
        new_date = date_now + timedelta(minutes=5)
        Str_StartDT = datetime.strftime(new_date, '%Y-%m-%d %I:%M %p')
        start_date, end_date = get_dates(Str_StartDT, Duration, TZ)
        pwd = create_pwd()
        # get access token from JSON file
        json_object = readJSON('user')
        access_token = json_object['access_token']
        # CHALLENGE: check if the access token has expired and use the refresh token to get a new access token
        success, results = Webex.create_meeting("Patient Consult: " + MRN, start_date, end_date, access_token, pwd, False, False, None, TZ)
        SIP_URI = results['sipAddress']
        HOST_KEY = results['hostKey']
        # write MRN & SIP URI to json file
        data = { 
                "MRN" : MRN, 
                "SIP_URI" : SIP_URI,
                "HOST_KEY" : HOST_KEY
            }
        json_object = json.dumps(data, indent = 4)
        writeToJSON('meeting', json_object)
        response = app.response_class(response=json.dumps(data),
                                status=200,
                                mimetype='application/json')
        return response
    else:
        return "OK"


# - - - Functions

def writeToJSON(filename, data):
    with open(filename + '.json', 'w') as outfile: 
        outfile.write(data)

def readJSON(filename):
    with open(filename + '.json', 'r') as openfile: 
        json_object = json.load(openfile)
    return json_object

def get_dates(Start_Date, Duration, TZ):
    TZ_New = pytz.timezone(TZ)
    start_datetime = datetime.strptime(Start_Date, '%Y-%m-%d %I:%M %p')
    utc_dt = TZ_New.localize(start_datetime).astimezone(pytz.utc)
    print ("UTC DT: " + str(utc_dt))
    TZ_date = utc_dt.astimezone(pytz.timezone(TZ))
    TZ_date_ISO = TZ_date.isoformat()
    print ("TZ Start Date: " + TZ_date_ISO)
    endDatetime = TZ_date + timedelta(minutes=int(Duration))
    TZ_enddate_ISO = endDatetime.isoformat()
    return TZ_date_ISO, TZ_enddate_ISO

def create_pwd(stringLength=8):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))