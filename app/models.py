from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Question Type Model
class QuestionType(db.Model):
    __tablename__ = 'question_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 'mcq', 'fill_blank', 'matching'
    display_name = db.Column(db.String(50), nullable=False)

# Exam Model
class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    time_limit_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Question Model - Updated with new fields
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('question_types.id'), nullable=False, default=1)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer)
    points = db.Column(db.Integer, default=1)
    explanation = db.Column(db.Text)
    correct_answer_text = db.Column(db.Text, nullable=True)  # For fill-in-blank
    exam = db.relationship('Exam', backref='questions')
    type = db.relationship('QuestionType')

# Option Model (for MCQ)
class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer)
    question = db.relationship('Question', backref='options')

# Matching Pair Model
class MatchingPair(db.Model):
    __tablename__ = 'matching_pairs'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    left_text = db.Column(db.String(200), nullable=False)
    right_text = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer)
    question = db.relationship('Question', backref='matching_pairs')

# Submission Model
class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    score = db.Column(db.Float)
    total_possible = db.Column(db.Float)
    status = db.Column(db.String(20), default='in_progress')
    user = db.relationship('User', backref='submissions')
    exam = db.relationship('Exam', backref='submissions')

# Answer Model
class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True)
    text_answer = db.Column(db.Text, nullable=True)  # For fill-in-blank and matching
    is_correct = db.Column(db.Boolean)
    submission = db.relationship('Submission', backref='answers')
    question = db.relationship('Question')
    option = db.relationship('Option')

# User Loader
from app import login

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
 