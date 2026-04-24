from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # Generic identifier: Username for admin/lecturer, Matric Number for student
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'lecturer', 'student'
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True) # Important for students
    
    # For students only
    photo_path = db.Column(db.String(200), nullable=True)
    face_encoding = db.Column(db.Text, nullable=True) # Store JSON string of 128-d array
    qr_code_path = db.Column(db.String(200), nullable=True)
    
    # Relationships
    courses = db.relationship('Course', backref='lecturer', cascade="all, delete-orphan", lazy=True)
    attendances = db.relationship('Attendance', backref='student', cascade="all, delete-orphan", lazy=True)
    
    # Many-to-Many student ownership
    registered_students = db.relationship('User', 
        secondary='student_ownership',
        primaryjoin=('User.id == student_ownership.c.lecturer_id'),
        secondaryjoin=('User.id == student_ownership.c.student_id'),
        backref=db.backref('registrars', lazy=True),
        lazy=True)

# Association table for Many-to-Many student ownership
student_ownership = db.Table('student_ownership',
    db.Column('lecturer_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    sessions = db.relationship('Session', backref='course', cascade="all, delete-orphan", lazy=True)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    attendances = db.relationship('Attendance', backref='session', cascade="all, delete-orphan", lazy=True)

class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    method = db.Column(db.String(50), nullable=False) # 'QR Code' or 'Facial Recognition'
    
    # To prevent duplicate attendance for the same session
    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='unique_attendance'),
    )
