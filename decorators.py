import os
import requests
import urllib.parse
from functools import wraps
from flask import request, redirect, url_for, session, render_template

def falhou(message="An stranger error ocurred. Please report the situation to the staff.", code=400):
    return render_template("error.html", message=message, code=code), code

def success(message="Success!"):
    return render_template("success.html", message=message)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function