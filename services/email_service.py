from flask import render_template, current_app
from flask_mail import Message
from models import db
from models.report import Report
from models.settings import CompanySettings
from app import mail
from datetime import datetime
import os

def send_report_email(report_id: int) -> bool:
    report = Report.query.get(report_id)
    if not report:
        return False
        
    client = report.client
    settings = CompanySettings.query.first()

    if not settings or not settings.smtp_user:
        current_app.logger.warning("SMTP not configured")
        return False

    subject = (f"{settings.company_name} — {client.name} Report"
               f" | {report.period_start.strftime('%B %Y')}")

    # Explicitly configure mail here since settings are dynamic
    current_app.config['MAIL_SERVER'] = settings.smtp_host
    current_app.config['MAIL_PORT'] = settings.smtp_port
    current_app.config['MAIL_USE_TLS'] = (settings.smtp_port == 587)
    current_app.config['MAIL_USE_SSL'] = (settings.smtp_port == 465)
    current_app.config['MAIL_USERNAME'] = settings.smtp_user
    current_app.config['MAIL_PASSWORD'] = settings.smtp_pass
    mail.init_app(current_app)

    msg = Message(subject=subject,
                  sender=(settings.company_name, settings.smtp_from),
                  recipients=[client.email])
    msg.html = render_template("emails/report.html",
                               client=client, report=report, settings=settings)

    filename = f"{client.name}_Report_{report.period_start.strftime('%Y_%m')}.pdf"
    
    # Report.pdf_path is relative to static folder (e.g. "static/reports/client_1_2023_10.pdf")
    # or absolute path depending on how it's stored.
    # In pdf_generator we store it as "static/reports/X.pdf". Let's resolve the absolute path:
    abs_pdf_path = os.path.join(current_app.root_path, report.pdf_path)
    
    try:
        with open(abs_pdf_path, "rb") as f:
            msg.attach(filename, "application/pdf", f.read())
            
        mail.send(msg)
        report.emailed = True
        report.emailed_at = datetime.utcnow()
        report.status = "sent"
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Email failed: {e}")
        report.status = "error"
        db.session.commit()
        return False
