#!/usr/bin/env python
from app import create_app, db
from app.models import QuestionType

app = create_app()
with app.app_context():
    # Check if types already exist
    if QuestionType.query.count() == 0:
        types = [
            QuestionType(name='mcq', display_name='Multiple Choice'),
            QuestionType(name='fill_blank', display_name='Fill in the Blank'),
            QuestionType(name='matching', display_name='Matching'),
        ]
        for t in types:
            db.session.add(t)
        db.session.commit()
        print("✅ Question types added!")
    else:
        print("Question types already exist")
    
    # List existing types
    print("\nExisting question types:")
    for t in QuestionType.query.all():
        print(f"  ID: {t.id}, Name: {t.name}, Display: {t.display_name}")