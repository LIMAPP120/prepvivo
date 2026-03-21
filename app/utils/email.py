from flask import render_template
from flask_mail import Message
from app import mail

def send_email(to, subject, template, **kwargs):
    """Send an email using a template"""
    try:
        msg = Message(subject, recipients=[to])
        msg.html = render_template(f'email/{template}', **kwargs)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_exam_results(user, submission):
    """Send exam results email to user"""
    percentage = (submission.score / submission.total_possible * 100) if submission.total_possible else 0
    passed = percentage >= 70
    
    return send_email(
        to=user.email,
        subject=f'Your {submission.exam.title} Results - PrepVivo',
        template='exam_results.html',
        user=user,
        submission=submission,
        percentage=percentage,
        passed=passed
    )
