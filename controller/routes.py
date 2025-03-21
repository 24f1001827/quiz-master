from main import app 
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from controller.models import *

@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard', username = current_user.username))
    else:
         return render_template("home.html") 