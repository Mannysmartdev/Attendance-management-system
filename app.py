import os
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['QR_FOLDER'] = os.path.join(app.root_path, 'static', 'qrcodes')

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['QR_FOLDER'], exist_ok=True)

from routes import main
app.register_blueprint(main)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(username='admin', password=hashed_pw, role='admin', name='System Admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
