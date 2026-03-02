from flask import Blueprint, render_template
from flask_login import login_required
from models.client import Client
from models.report import Report
from datetime import date

bp = Blueprint("dashboard", __name__)

@bp.route("/")
@login_required
def index():
    active_clients_count = Client.query.filter_by(is_active=True).count()
    
    today = date.today()
    reports_this_month = Report.query.filter(
        db.extract('month', Report.generated_at) == today.month,
        db.extract('year', Report.generated_at) == today.year
    ).count()
    
    emails_sent = Report.query.filter(
        Report.emailed == True,
        db.extract('month', Report.generated_at) == today.month,
        db.extract('year', Report.generated_at) == today.year
    ).count()
    
    scheduled_clients = Client.query.filter_by(report_email=True, is_active=True).count()
    
    recent_reports = Report.query.order_by(Report.generated_at.desc()).limit(10).all()
    
    return render_template("dashboard/index.html", 
                           active_clients=active_clients_count,
                           reports_month=reports_this_month,
                           emails_sent=emails_sent,
                           scheduled_clients=scheduled_clients,
                           recent_reports=recent_reports)

# Need to import db here to use extract
from models import db
