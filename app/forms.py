from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Exam, QuestionType

# Authentication Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# Admin Question Form
class QuestionForm(FlaskForm):
    exam = SelectField('Exam', coerce=int, validators=[DataRequired()])
    type = SelectField('Question Type', coerce=int, validators=[DataRequired()])
    text = TextAreaField('Question Text', validators=[DataRequired()])
    order = IntegerField('Order', default=0)
    points = IntegerField('Points', default=1)
    explanation = TextAreaField('Explanation')
    correct_answer_text = TextAreaField('Correct Answer (for Fill-in-Blank)')
    submit = SubmitField('Save')
    
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.exam.choices = [(e.id, e.title) for e in Exam.query.order_by('title')]
        self.type.choices = [(t.id, t.display_name) for t in QuestionType.query.order_by('name')]