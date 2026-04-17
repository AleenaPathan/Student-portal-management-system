from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))  # admin, teacher, parent
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    # For parents, link to student
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    class_name = db.Column(db.String(50))
    roll_number = db.Column(db.String(20), unique=True)
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    parent_contact = db.Column(db.String(20))
    fees_paid = db.Column(db.Float, default=0.0)
    total_fees = db.Column(db.Float, default=0.0)
    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    activities = db.relationship('Activity', backref='student', lazy=True)
    progress_records = db.relationship('ProgressRecord', backref='student', lazy=True)
    homeworks = db.relationship('Homework', backref='student', lazy=True)
    classworks = db.relationship('Classwork', backref='student', lazy=True)
    fees = db.relationship('Fee', backref='student', lazy=True)
    feedbacks = db.relationship('Feedback', backref='student', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    status = db.Column(db.String(10))  # present, absent, late

class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, default=datetime.utcnow().date)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    achievement_type = db.Column(db.String(50))  # sports, academic, cultural, etc.

class ProgressRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(50))
    marks_obtained = db.Column(db.Float)
    total_marks = db.Column(db.Float)
    exam_type = db.Column(db.String(50))  # midterm, final, quiz, etc.
    date = db.Column(db.Date, default=datetime.utcnow().date)
    remarks = db.Column(db.Text)

class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(50))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    assigned_date = db.Column(db.Date, default=datetime.utcnow().date)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, submitted, completed

class Classwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(50))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    marks_obtained = db.Column(db.Float, nullable=True)
    total_marks = db.Column(db.Float, nullable=True)

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50))
    day = db.Column(db.String(20))  # monday, tuesday, etc.
    period = db.Column(db.Integer)
    subject = db.Column(db.String(50))
    teacher = db.Column(db.String(100))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    target_audience = db.Column(db.String(20))  # all, parents, teachers, students

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    parent_name = db.Column(db.String(100))
    feedback_type = db.Column(db.String(20))  # feedback, complaint
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    status = db.Column(db.String(20), default='pending')  # pending, resolved    