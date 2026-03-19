from flask import render_template
from flask_login import login_required, current_user
from app.models import Exam, Submission
from flask import Blueprint

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    exams = Exam.query.all()
    return render_template('index.html', exams=exams)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get all submissions for the current user, oldest first for chart
    submissions = Submission.query.filter_by(user_id=current_user.id)\
                                  .order_by(Submission.end_time.asc()).all()
    
    # Prepare chart data
    chart_labels = []
    chart_data = []
    for sub in submissions:
        if sub.end_time and sub.total_possible and sub.total_possible > 0:
            chart_labels.append(sub.end_time.strftime('%Y-%m-%d'))
            percentage = round((sub.score / sub.total_possible * 100), 1)
            chart_data.append(percentage)
    
    return render_template('dashboard.html', submissions=submissions,
                           chart_labels=chart_labels, chart_data=chart_data)