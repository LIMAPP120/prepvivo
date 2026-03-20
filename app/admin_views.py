from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort, request, redirect, url_for
from flask_admin import expose
from app import db
from app.models import Question
from app.forms import QuestionForm

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        abort(403)

class UserView(SecureModelView):
    column_list = ['id', 'username', 'email', 'role', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['role', 'created_at']
    form_columns = ['username', 'email', 'role']
    can_create = True
    can_edit = True
    can_delete = True
    column_editable_list = ['role']

class ExamView(SecureModelView):
    column_list = ['id', 'title', 'description', 'time_limit_minutes', 'created_at']
    column_searchable_list = ['title']
    form_columns = ['title', 'description', 'time_limit_minutes']
    form_widget_args = {
        'description': {'rows': 4}
    }

class OptionView(SecureModelView):
    column_list = ['id', 'question', 'text', 'is_correct', 'order']
    column_filters = ['question', 'is_correct']
    form_columns = ['question', 'text', 'is_correct', 'order']

class QuestionView(SecureModelView):
    column_list = ['id', 'exam', 'type', 'text', 'order', 'points']
    column_searchable_list = ['text']
    column_filters = ['exam', 'type']
    
    def create_form(self):
        return QuestionForm()
    
    def edit_form(self, obj):
        form = QuestionForm(obj=obj)
        return form
    
    def create_model(self, form):
        try:
            model = self.model(
                exam_id=form.exam.data,
                type_id=form.type.data,
                text=form.text.data,
                order=form.order.data,
                points=form.points.data,
                explanation=form.explanation.data,
                correct_answer_text=form.correct_answer_text.data
            )
            db.session.add(model)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error creating question: {e}")
            return False
    
    def update_model(self, form, model):
        try:
            model.exam_id = form.exam.data
            model.type_id = form.type.data
            model.text = form.text.data
            model.order = form.order.data
            model.points = form.points.data
            model.explanation = form.explanation.data
            model.correct_answer_text = form.correct_answer_text.data
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error updating question: {e}")
            return False

class QuestionTypeView(SecureModelView):
    column_list = ['id', 'name', 'display_name']
    column_searchable_list = ['name', 'display_name']
    form_columns = ['name', 'display_name']

class MatchingPairView(SecureModelView):
    column_list = ['id', 'question', 'left_text', 'right_text', 'order']
    column_searchable_list = ['left_text', 'right_text']
    column_filters = ['question']
    form_columns = ['question', 'left_text', 'right_text', 'order']
    form_args = {
        'question': {'query_factory': lambda: db.session.query(Question).filter(
            Question.type.has(name='matching')
        )}
    }