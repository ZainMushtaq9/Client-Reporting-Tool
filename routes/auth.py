from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from models.settings import CompanySettings
from datetime import datetime

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard.index"))
            
        flash("Invalid username or password", "error")
        
    settings = CompanySettings.query.first()
    return render_template("auth/login.html", settings=settings)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    current_pass = request.form.get("current_password")
    new_pass = request.form.get("new_password")
    confirm_pass = request.form.get("confirm_password")
    
    if not current_user.check_password(current_pass):
        flash("Incorrect current password.", "error")
        return redirect(url_for("settings.index") if current_user.is_admin() else url_for("dashboard.index"))
        
    if new_pass != confirm_pass:
        flash("New passwords do not match.", "error")
        return redirect(url_for("settings.index") if current_user.is_admin() else url_for("dashboard.index"))
        
    if len(new_pass) < 6:
        flash("New password must be at least 6 characters.", "error")
        return redirect(url_for("settings.index") if current_user.is_admin() else url_for("dashboard.index"))
        
    current_user.set_password(new_pass)
    db.session.commit()
    flash("Password changed successfully.", "success")
    return redirect(url_for("settings.index") if current_user.is_admin() else url_for("dashboard.index"))
