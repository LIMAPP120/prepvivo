import json
import os
from glob import glob
from app import create_app
from app.models import db, Exam, Question, Option

app = create_app()
with app.app_context():
    # Find all JSON files except maybe vocab1.json (already imported) – but we can just import all
    json_files = glob("*.json")
    # Optionally exclude some
    exclude = ['vocab1.json']  # already imported
    for json_file in json_files:
        if json_file in exclude:
            continue
        print(f"Importing {json_file}...")
        with open(json_file) as f:
            data = json.load(f)

        # Check if exam with same title already exists (to avoid duplicates)
        existing = Exam.query.filter_by(title=data['title']).first()
        if existing:
            print(f"  Exam '{data['title']}' already exists, skipping.")
            continue

        exam = Exam(
            title=data['title'],
            description=data['description'],
            time_limit_minutes=data.get('time_limit', 20)
        )
        db.session.add(exam)
        db.session.flush()

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
        print(f"  ✅ Imported '{exam.title}' with {len(data['questions'])} questions.")

    print("All imports completed.")