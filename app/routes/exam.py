from weasyprint import HTML
from flask import make_response
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
    
    # Mark any existing in-progress submissions as 'abandoned' (start fresh)
    abandoned = Submission.query.filter_by(
        user_id=current_user.id, exam_id=exam_id, status='in_progress'
    ).all()
    for sub in abandoned:
        sub.status = 'abandoned'
    db.session.commit()
    
    # Create a brand new submission
    submission = Submission(user_id=current_user.id, exam_id=exam_id)
    db.session.add(submission)
    db.session.commit()
    
    # Calculate remaining seconds (full time limit)
    time_limit = exam.time_limit_minutes * 60 if exam.time_limit_minutes else 0
    remaining = time_limit if time_limit else None
    
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.order).all()
    return render_template('exam/take.html', exam=exam, questions=questions,
                           submission=submission, remaining_seconds=remaining)

@bp.route('/<int:exam_id>/submit', methods=['POST'])
@login_required
def submit_exam(exam_id):
    from app.utils.email import send_exam_results
    submission = Submission.query.filter_by(
        user_id=current_user.id, exam_id=exam_id, status='in_progress'
    ).first_or_404()
    exam = Exam.query.get_or_404(exam_id)

    # Check time limit (server-side)
    if exam.time_limit_minutes:
        elapsed = (datetime.utcnow() - submission.start_time).total_seconds()
        if elapsed > exam.time_limit_minutes * 60:
            flash('Time limit exceeded. Your answers have been submitted automatically.')
    
    questions = Question.query.filter_by(exam_id=exam_id).all()
    total_possible = sum(q.points for q in questions)

    score = 0
    for question in questions:
        answer_key = f'q_{question.id}'
        
        # Handle different question types
        if question.type and question.type.name == 'mcq':
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
        
        elif question.type and question.type.name == 'fill_blank':
            user_answer = request.form.get(answer_key, '').strip().lower()
            correct_answer = (question.correct_answer_text or '').strip().lower()
            is_correct = (user_answer == correct_answer)
            ans = Answer(
                submission_id=submission.id,
                question_id=question.id,
                selected_option_id=None,
                text_answer=user_answer,
                is_correct=is_correct
            )
            db.session.add(ans)
            if is_correct:
                score += question.points
        
        elif question.type and question.type.name == 'matching':
            # Collect all matching pairs answers
            all_correct = True
            answers_collected = []
            for pair in question.matching_pairs:
                pair_key = f'match_{question.id}_{pair.id}'
                user_answer = request.form.get(pair_key, '').strip().lower()
                correct_answer = pair.right_text.strip().lower()
                is_correct = (user_answer == correct_answer)
                answers_collected.append(f"{pair.left_text}: {user_answer} (correct: {correct_answer})")
                if not is_correct:
                    all_correct = False
            
            # Store combined answer as text
            combined_answer = ' | '.join(answers_collected)
            ans = Answer(
                submission_id=submission.id,
                question_id=question.id,
                selected_option_id=None,
                text_answer=combined_answer,
                is_correct=all_correct
            )
            db.session.add(ans)
            if all_correct:
                score += question.points
        
        else:
            # Fallback for questions without type (treat as MCQ)
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
                # For fill-in-blank questions that might not have type_id set
                user_answer = request.form.get(answer_key, '').strip().lower()
                correct_answer = (question.correct_answer_text or '').strip().lower()
                if correct_answer and user_answer:
                    is_correct = (user_answer == correct_answer)
                else:
                    is_correct = False
                ans = Answer(
                    submission_id=submission.id,
                    question_id=question.id,
                    selected_option_id=None,
                    text_answer=user_answer if user_answer else None,
                    is_correct=is_correct
                )
                db.session.add(ans)
                if is_correct:
                    score += question.points

    submission.score = score
    submission.total_possible = total_possible
    submission.status = 'completed'
    submission.end_time = datetime.utcnow()
    db.session.commit()
    
    # Send email notification (don't block the response if email fails)
    #try:
    #    send_exam_results(current_user, submission)
    #    print(f"Email sent to {current_user.email}")
    #except Exception as e:
    #    print(f"Failed to send email: {e}")

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
        
        # Handle different question types for display
        if q.type and q.type.name == 'fill_blank':
            user_answer = ans.text_answer if ans.text_answer else 'No answer'
            correct_answer = q.correct_answer_text or 'No correct answer provided'
        elif q.type and q.type.name == 'matching':
            user_answer = ans.text_answer if ans.text_answer else 'No answer'
            correct_answer = "All pairs must match correctly"
        else:
            user_answer = user_option.text if user_option else 'No answer'
            correct_option = Option.query.filter_by(question_id=q.id, is_correct=True).first()
            correct_answer = correct_option.text if correct_option else ''
        
        results.append({
            'question': q,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': ans.is_correct,
            'explanation': q.explanation
        })
    return render_template('exam/result.html', submission=submission, results=results)

@bp.route('/result/<int:submission_id>/certificate')
@login_required
def certificate(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    if submission.user_id != current_user.id:
        abort(403)
    
    # Only allow certificate for passing scores (70% or higher)
    percentage = (submission.score / submission.total_possible * 100) if submission.total_possible else 0
    if percentage < 70:
        flash('Certificate is only available for scores of 70% or higher.')
        return redirect(url_for('exam.result', submission_id=submission.id))
    
    html = render_template('certificate.html', user=current_user, submission=submission)
    pdf = HTML(string=html).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=certificate_{submission_id}.pdf'
    return response