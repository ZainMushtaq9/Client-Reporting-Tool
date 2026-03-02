from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db
from models.client import Client
from utils import admin_required
from datetime import date
import calendar
from services.mock_data import generate_metrics

bp = Blueprint("clients", __name__, url_prefix="/clients")

@bp.route("/")
@login_required
def list_clients():
    clients = Client.query.filter_by(is_active=True).all()
    return render_template("clients/list.html", clients=clients)

@bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add():
    if request.method == "POST":
        client = Client(
            name=request.form.get("name"),
            email=request.form.get("email"),
            website=request.form.get("website"),
            industry=request.form.get("industry"),
            report_email=request.form.get("report_email") == "on",
            report_freq=request.form.get("report_freq"),
            report_day=int(request.form.get("report_day", 1)),
            show_ads=request.form.get("show_ads") == "on",
            show_email_mkt=request.form.get("show_email_mkt") == "on",
            notes=request.form.get("notes")
        )
        db.session.add(client)
        db.session.commit()
        flash("Client added successfully.", "success")
        return redirect(url_for("clients.list_clients"))
    return render_template("clients/add.html")

@bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(id):
    client = Client.query.get_or_404(id)
    if request.method == "POST":
        client.name = request.form.get("name")
        client.email = request.form.get("email")
        client.website = request.form.get("website")
        client.industry = request.form.get("industry")
        client.report_email = request.form.get("report_email") == "on"
        client.report_freq = request.form.get("report_freq")
        client.report_day = int(request.form.get("report_day", 1))
        client.show_ads = request.form.get("show_ads") == "on"
        client.show_email_mkt = request.form.get("show_email_mkt") == "on"
        client.notes = request.form.get("notes")
        db.session.commit()
        flash("Client updated successfully.", "success")
        return redirect(url_for("clients.list_clients"))
    return render_template("clients/edit.html", client=client)

@bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(id):
    client = Client.query.get_or_404(id)
    client.is_active = False
    db.session.commit()
    flash("Client deactivated.", "success")
    return redirect(url_for("clients.list_clients"))

@bp.route("/<int:id>/view")
@login_required
def view(id):
    client = Client.query.get_or_404(id)
    # Generate mock metrics for the past month
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
    
    metrics = generate_metrics(client.id, period_start, period_end)
    
    # Months labels
    months_labels = ["M-5", "M-4", "M-3", "M-2", "M-1", "Current"]
    # Mocking historical trend logic for dashboard Chart.js
    monthly_sessions = [metrics["sessions"]] * 6 
    monthly_users = [metrics["users"]] * 6
    
    source_values = [
        metrics["source_organic"], metrics["source_direct"],
        metrics["source_social"], metrics["source_referral"],
        metrics["source_paid"]
    ]
    
    return render_template(
        "clients/view.html",
        client=client,
        metrics=metrics,
        period_start=period_start,
        period_end=period_end,
        months_labels=months_labels,
        monthly_sessions=monthly_sessions,
        monthly_users=monthly_users,
        source_values=source_values
    )
