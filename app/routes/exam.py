from flask import render_template, redirect, url_for, abort, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Exam, Question, Option, Submission, Answer
from datetime import datetime
from flask import Blueprint

bp = Blueprint('exam', __name__)

@bp.route('/<int:exam_id>')
@login_required
def take_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    # Check if user already has an in-progress submission for this exam
    submission = Submission.query.filter_by(
        user_id=current_user.id, exam_id=exam_id, status='in_progress'
    ).first()
    
    # If no in-progress submission, create a new one (allow retakes)
    if submission is None:
        submission = Submission(user_id=current_user.id, exam_id=exam_id)
        db.session.add(submission)
        db.session.commit()
    
    # Calculate remaining seconds for timer
    elapsed = (datetime.utcnow() - submission.start_time).total_seconds()
    time_limit = exam.time_limit_minutes * 60 if exam.time_limit_minutes else 0
    remaining = max(time_limit - elapsed, 0) if time_limit else None

    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.order).all()
    return render_template('exam/take.html', exam=exam, questions=questions,
                           submission=submission, remaining_seconds=remaining)

@bp.route('/<int:exam_id>/submit', methods=['POST'])
@login_required
def submit_exam(exam_id):
    submission = Submission.query.filter_by(
        user_id=current_user.id, exam_id=exam_id, status='in_progress'
    ).first_or_404()
    exam = Exam.query.get_or_404(exam_id)

    # Check time limit (server-side)
    if exam.time_limit_minutes:
        elapsed = (datetime.utcnow() - submission.start_time).total_seconds()
        if elapsed > exam.time_limit_minutes * 60:
            flash('Time limit exceeded. Your answers have been submitted automatically.')
            # We'll still process whatever they answered

    questions = Question.query.filter_by(exam_id=exam_id).all()
    total_possible = sum(q.points for q in questions)

    score = 0
    for question in questions:
        answer_key = f'q_{question.id}'
        selected_option_id = request.form.get(answer_key)
        if selected_option_id:
            option = Option.query.get(selected_option_id)
            is_correct = option.is_correct if option else False
            ans = Answer(
                submission_id=submission.id,
                question_id=question.id,
                selected_option_id=selected_option_id,
                is_correct=is_correct
            )
            db.session.add(ans)
            if is_correct:
                score += question.points
        else:
            ans = Answer(
                submission_id=submission.id,
                question_id=question.id,
                selected_option_id=None,
                is_correct=False
            )
            db.session.add(ans)

    submission.score = score
    submission.total_possible = total_possible
    submission.status = 'completed'
    submission.end_time = datetime.utcnow()
    db.session.commit()

    flash(f'Exam submitted! Your score: {score}/{total_possible}')
    return redirect(url_for('exam.result', submission_id=submission.id))

@bp.route('/result/<int:submission_id>')
@login_required
def result(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    if submission.user_id != current_user.id:
        abort(403)
    answers = Answer.query.filter_by(submission_id=submission_id).all()
    results = []
    for ans in answers:
        q = ans.question
        user_option = Option.query.get(ans.selected_option_id) if ans.selected_option_id else None
        correct_option = Option.query.filter_by(question_id=q.id, is_correct=True).first()
        results.append({
            'question': q,
            'user_answer': user_option.text if user_option else 'No answer',
            'correct_answer': correct_option.text if correct_option else '',
            'is_correct': ans.is_correct,
            'explanation': q.explanation
        })
    return render_template('exam/result.html', submission=submission, results=results)