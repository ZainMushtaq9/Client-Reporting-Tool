from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from models import db
from models.client import Client
import calendar
import os

def generate_and_send_report(app, client_id):
    from services.pdf_generator import generate_pdf
    from services.email_service import send_report_email
    
    with app.app_context():
        client = Client.query.get(client_id)
        if not client:
            return
            
        today = date.today()
        # For demo purposes, we report on the previous full month:
        if today.month == 1:
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year
            
        period_start = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        period_end = date(year, month, last_day)
        
        report = generate_pdf(client, period_start, period_end)
        if report and client.report_email:
            send_report_email(report.id)

def start_scheduler(app):
    scheduler = BackgroundScheduler(daemon=True)

    @scheduler.scheduled_job("cron", hour=8, minute=0, id="daily_check")
    def daily_check():
        with app.app_context():
            today = date.today()
            clients = Client.query.filter_by(is_active=True, report_email=True).all()
            for c in clients:
                send = False
                if c.report_freq == "monthly" and today.day == c.report_day:
                    send = True
                elif c.report_freq == "weekly" and today.weekday() == 0:  # Monday
                    send = True
                
                if send:
                    generate_and_send_report(app, c.id)

    scheduler.start()
    return scheduler
