from main import app 
from flask import render_template, redirect, url_for, flash, request 
from flask_login import login_user, logout_user, current_user, LoginManager, login_required
from controller.models import * 

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET' :
        #Check if user is already logged in 
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return render_template('login.html')
    
    if request.method == 'POST':
        email_id = request.form['email']
        password = request.form['password']

        #Check email validity
        if '@' not in email_id:
            flash("Invalid email", 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email_id).first()
        #Check if user has been registered in the database
        if not user:
            flash('User does not exist. Please register first', 'danger')
            return render_template('login.html')
        
        #Check if password is incorrect 
        if user.password != password:
            flash("Incorrect password", 'danger')
            return render_template('login.html')
        
        if user and user.password == password:
            login_user(user)
            current_user.last_login = datetime.now()
            db.session.commit()
            flash('You have been logged in!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard')) 
            else:
                return redirect(url_for('user_dashboard', user_id = user.id))
            
        
        
@app.route('/logout')
@login_required
def logout():
    if not current_user.is_authenticated:
        flash("You are not logged in.", "info")  # If the user is not logged in
    else:
        logout_user()  # Log out the user
        flash("You have been logged out.", "success")
    return redirect(url_for('home'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        email_id = request.form["email"]
        password = request.form["password"] 
        confirm_password = request.form["confirm_password"]
        full_name = request.form["full_name"]
        username = request.form["username"] 

        if "@" not in email_id:
            flash("Invalid Email ID")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Passwords do not match") 
            return render_template("register.html") 
        
        if len(password) <8:
            flash("Password should be a minimum of 8 characters")
            return render_template("register.html")
        
        if len(password)>20:
            flash("Password should be a maximum of 20 characters")
            return render_template("register.html")
        
        user = User.query.filter_by(email=email_id).first() 
        if user:
            flash("User already exists. Please go to login, or use a different email") 
            return render_template("register.html")
        
        user = User(email=email_id,password=password,username=username,full_name=full_name,role="user")
        db.session.add(user)
        db.session.commit() 
        
        flash("User registered successfully", "success")
        return redirect(url_for("login"))
    


        
        

        
    
