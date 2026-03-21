from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_admin import Admin
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
csrf = CSRFProtect()
admin = Admin(name='PrepVivo Admin', template_mode='bootstrap3')  # ONLY ONE instance
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    admin.init_app(app)  # This attaches the admin to the app, doesn't create a new one
    mail.init_app(app)

    @app.context_processor
    def inject_app_name():
        return dict(app_name=app.config.get('APP_NAME', 'PrepVivo'))

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.exam import bp as exam_bp
    app.register_blueprint(exam_bp, url_prefix='/exam')

    # Import models and admin views
    from app import models
    from app.admin_views import SecureModelView, UserView, ExamView, QuestionView, OptionView, QuestionTypeView, MatchingPairView

    # Add models to admin with unique endpoint names
    # admin.add_view(UserView(models.User, db.session, name='Users', endpoint='admin_users'))
    admin.add_view(ExamView(models.Exam, db.session, name='Exams', endpoint='admin_exams'))
    admin.add_view(QuestionView(models.Question, db.session, name='Questions', endpoint='admin_questions'))
    admin.add_view(OptionView(models.Option, db.session, name='Options', endpoint='admin_options'))
    admin.add_view(SecureModelView(models.Submission, db.session, name='Submissions', endpoint='admin_submissions'))
    admin.add_view(SecureModelView(models.Answer, db.session, name='Answers', endpoint='admin_answers'))
    admin.add_view(QuestionTypeView(models.QuestionType, db.session, name='Question Types', endpoint='admin_question_types'))
    admin.add_view(MatchingPairView(models.MatchingPair, db.session, name='Matching Pairs', endpoint='admin_matching_pairs'))
    return app