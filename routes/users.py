from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.user import User
from utils import admin_required

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/")
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template("users/index.html", users=users)

@bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        role = request.form.get("role")
        
        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("users.add"))
        
        # Check uniqueness
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return redirect(url_for("users.add"))
            
        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "error")
            return redirect(url_for("users.add"))
            
        user = User(username=username, email=email, role=role, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f"User {username} created.", "success")
        return redirect(url_for("users.index"))
        
    return render_template("users/add.html")

@bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "error")
        return redirect(url_for("users.index"))
        
    # Prevent deactivating the last active admin
    if user.role == "admin" and user.is_active:
        active_admins = User.query.filter_by(role="admin", is_active=True).count()
        if active_admins <= 1:
            flash("Cannot deactivate the last active admin.", "error")
            return redirect(url_for("users.index"))
            
    user.is_active = not user.is_active
    db.session.commit()
    status = "activated" if user.is_active else "deactivated"
    flash(f"User {user.username} {status}.", "success")
    return redirect(url_for("users.index"))

@bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("users.index"))
        
    # Prevent deleting the last active admin
    if user.role == "admin" and user.is_active:
        active_admins = User.query.filter_by(role="admin", is_active=True).count()
        if active_admins <= 1:
            flash("Cannot delete the last active admin.", "error")
            return redirect(url_for("users.index"))
            
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted.", "success")
    return redirect(url_for("users.index"))
