import json
import sys
from app import create_app
from app.models import db, Exam, Question, Option

app = create_app()
with app.app_context():
    # Load JSON data
    filename = 'vocab1.json'  # change this for each file
    with open(filename) as f:
        data = json.load(f)

    # Create Exam
    exam = Exam(
        title=data['title'],
        description=data['description'],
        time_limit_minutes=data.get('time_limit', 20)
    )
    db.session.add(exam)
    db.session.flush()  # to get exam.id

    for q_data in data['questions']:
        question = Question(
            exam_id=exam.id,
            text=q_data['text'],
            order=q_data['order'],
            points=q_data.get('points', 1),
            explanation=q_data.get('explanation', '')
        )
        db.session.add(question)
        db.session.flush()

        for opt_data in q_data['options']:
            option = Option(
                question_id=question.id,
                text=opt_data['text'],
                is_correct=opt_data['is_correct'],
                order=opt_data['order']
            )
            db.session.add(option)

    db.session.commit()
    print(f"✅ Imported exam '{exam.title}' with {len(data['questions'])} questions.")