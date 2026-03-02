import os
from flask import Flask
from models import db
from flask_login import LoginManager
from flask_mail import Mail
# We will initialize routes, schedule, and plugins shortly

mail = Mail()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///client_reporter.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Routes
    from routes import auth, dashboard, clients, reports, settings_routes, users
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(clients.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(settings_routes.bp)
    app.register_blueprint(users.bp)

    # Initialize Scheduler
    from services.scheduler import start_scheduler
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_scheduler(app)

    # Context processors
    from models.settings import CompanySettings
    @app.context_processor
    def inject_settings():
        settings = CompanySettings.query.first()
        if not settings:
            settings = CompanySettings(company_name="My Company")
        return dict(get_company_settings=lambda: settings)

    # User loader
    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error handlers
    from flask import render_template
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(403)
    def access_denied(e):
        return render_template('errors/403.html'), 403
        
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
