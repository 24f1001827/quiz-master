from flask import Flask, render_template
from controller.database import db 
from controller.config import Config
from controller.models import *
app = Flask(__name__, template_folder='templates', static_folder='static') 
app.config.from_object(Config)
db.init_app(app) 
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role = 'admin').first()
    if not admin:
        admin = User(email = 'admin@gmail.com', password = 'admin_123', username = 'Admin', full_name = 'Ashmit', role = 'admin') 
        db.session.add(admin)
    db.session.commit()

from controller.authorization_routes import *
from controller.routes import *
from controller.admin_routes import *
from controller.user_routes import *
from controller.admin_summary_routes import *
from controller.user_summary_routes import *

if __name__ == '__main__':
    app.run() 
