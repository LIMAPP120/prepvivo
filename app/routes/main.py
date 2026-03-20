from flask import render_template, Blueprint
from flask_login import login_required, current_user
from app.models import Exam, Submission

# Create the blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    exams = Exam.query.all()
    return render_template('index.html', exams=exams)
@bp.route('/dashboard')
@login_required
def dashboard():
    # Get all COMPLETED submissions for the current user
    submissions = Submission.query.filter_by(
        user_id=current_user.id, 
        status='completed'
    ).order_by(Submission.end_time.asc()).all()
    
    print(f"DEBUG: Found {len(submissions)} completed submissions for user {current_user.id}")  # Debug
    
    # Prepare chart data
    chart_labels = []
    chart_data = []
    for sub in submissions:
        if sub.end_time and sub.total_possible and sub.total_possible > 0:
            chart_labels.append(sub.end_time.strftime('%Y-%m-%d'))
            percentage = round((sub.score / sub.total_possible * 100), 1)
            chart_data.append(percentage)
    
    print(f"DEBUG: Chart labels: {chart_labels}")  # Debug
    print(f"DEBUG: Chart data: {chart_data}")  # Debug
    
    # Convert submissions to JSON-serializable dictionaries
    submissions_data = []
    for sub in submissions:
        submissions_data.append({
            'id': sub.id,
            'exam': {
                'id': sub.exam.id,
                'title': sub.exam.title
            },
            'score': sub.score,
            'total_possible': sub.total_possible,
            'end_time': sub.end_time.isoformat() if sub.end_time else None,
            'status': sub.status
        })
    
    print(f"DEBUG: Submissions data count: {len(submissions_data)}")  # Debug
    
    return render_template('dashboard.html', submissions=submissions_data,
                           chart_labels=chart_labels, chart_data=chart_data)