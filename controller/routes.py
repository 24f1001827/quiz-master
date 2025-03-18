from main import app 
from flask import render_template, redirect, url_for, flash, request
from controller.models import *

@app.route('/')
def home():
    return render_template("home.html") 