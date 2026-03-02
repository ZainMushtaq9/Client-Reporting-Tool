from flask import Blueprint, render_template, redirect, url_for, flash, send_file, current_app, request
from flask_login import login_required
from models import db
from models.report import Report
from models.client import Client
from utils import admin_required
from services.pdf_generator import generate_pdf
from services.email_service import send_report_email
import os
from datetime import date
import calendar

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.route("/")
@login_required
def list_reports():
    reports = Report.query.order_by(Report.generated_at.desc()).all()
    return render_template("reports/list.html", reports=reports)

def get_last_month_period():
    today = date.today()
    if today.month == 1:
        month = 12
        year = today.year - 1
    else:
        month = today.month - 1
        year = today.year
    period_start = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    period_end = date(year, month, last_day)
    return period_start, period_end

@bp.route("/generate/<int:cid>", methods=["POST"])
@login_required
def generate(cid):
    client = Client.query.get_or_404(cid)
    period_start, period_end = get_last_month_period()
    report = generate_pdf(client, period_start, period_end)
    if report:
        flash(f"Report generated for {client.name}", "success")
    else:
        flash(f"Failed to generate report for {client.name}", "error")
    # Redirect back to where the user came from
    next_url = request.referrer or url_for("reports.list_reports")
    return redirect(next_url)

@bp.route("/generate-all", methods=["POST"])
@login_required
@admin_required
def generate_all():
    clients = Client.query.filter_by(is_active=True).all()
    period_start, period_end = get_last_month_period()
    success_count = 0
    for client in clients:
        report = generate_pdf(client, period_start, period_end)
        if report:
            success_count += 1
    flash(f"Generated {success_count} / {len(clients)} reports.", "success")
    return redirect(url_for("reports.list_reports"))

@bp.route("/<int:id>/download")
@login_required
def download(id):
    report = Report.query.get_or_404(id)
    abs_path = os.path.join(current_app.root_path, report.pdf_path)
    if os.path.exists(abs_path):
        return send_file(abs_path, as_attachment=True)
    flash("PDF file not found.", "error")
    return redirect(url_for("reports.list_reports"))

@bp.route("/<int:id>/send", methods=["POST"])
@login_required
@admin_required
def send_email(id):
    report = Report.query.get_or_404(id)
    if send_report_email(report.id):
        flash("Email sent successfully.", "success")
    else:
        flash("Failed to send email. Check SMTP settings.", "error")
    return redirect(url_for("reports.list_reports"))

@bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(id):
    report = Report.query.get_or_404(id)
    abs_path = os.path.join(current_app.root_path, report.pdf_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)
    db.session.delete(report)
    db.session.commit()
    flash("Report deleted.", "success")
    return redirect(url_for("reports.list_reports"))
