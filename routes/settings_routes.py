from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.settings import CompanySettings
from utils import admin_required
import os
from PIL import Image

bp = Blueprint("settings", __name__, url_prefix="/settings")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def index():
    settings = CompanySettings.query.first()
    if not settings:
        settings = CompanySettings()
        db.session.add(settings)
        db.session.commit()
        
    if request.method == "POST":
        settings.company_name = request.form.get("company_name", "My Company")
        settings.description = request.form.get("description", "")
        settings.primary_color = request.form.get("primary_color", "#1D4ED8")
        settings.accent_color = request.form.get("accent_color", "#065F46")
        settings.contact_email = request.form.get("contact_email", "")
        settings.smtp_host = request.form.get("smtp_host", "smtp.gmail.com")
        settings.smtp_port = int(request.form.get("smtp_port", 587))
        settings.smtp_user = request.form.get("smtp_user", "")
        if request.form.get("smtp_pass"):
            settings.smtp_pass = request.form.get("smtp_pass")
        settings.smtp_from = request.form.get("smtp_from", "")
        db.session.commit()
        flash("Settings updated successfully.", "success")
        return redirect(url_for("settings.index"))
        
    return render_template("settings/index.html", settings=settings)

@bp.route("/upload-logo", methods=["POST"])
@login_required
@admin_required
def upload_logo():
    if 'logo' not in request.files:
        flash('No file part', "error")
        return redirect(url_for('settings.index'))
    file = request.files['logo']
    if file.filename == '':
        flash('No selected file', "error")
        return redirect(url_for('settings.index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Rename with timestamp
        import time
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"logo_{int(time.time())}.{ext}"
        
        upload_dir = os.path.join(current_app.root_path, "static", "uploads", "logo")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, new_filename)
        
        # Resize if not svg
        if ext != 'svg':
            img = Image.open(file)
            # max height 200px
            ratio = 200 / float(img.size[1])
            new_width = int(float(img.size[0]) * float(ratio))
            img = img.resize((new_width, 200), Image.Resampling.LANCZOS)
            img.save(filepath)
        else:
            file.save(filepath)
            
        settings = CompanySettings.query.first()
        settings.logo_filename = new_filename
        db.session.commit()
        
        flash('Logo uploaded successfully', "success")
    else:
        flash('Invalid file type. Only PNG, JPG, and SVG are allowed', "error")
        
    return redirect(url_for('settings.index'))

@bp.route("/test-email", methods=["POST"])
@login_required
@admin_required
def test_email():
    from flask_mail import Message
    from app import mail
    settings = CompanySettings.query.first()
    
    current_app.config['MAIL_SERVER'] = settings.smtp_host
    current_app.config['MAIL_PORT'] = settings.smtp_port
    current_app.config['MAIL_USE_TLS'] = (settings.smtp_port == 587)
    current_app.config['MAIL_USE_SSL'] = (settings.smtp_port == 465)
    current_app.config['MAIL_USERNAME'] = settings.smtp_user
    current_app.config['MAIL_PASSWORD'] = settings.smtp_pass
    mail.init_app(current_app)
    
    try:
        msg = Message(subject=f"{settings.company_name} Test Email",
                      sender=(settings.company_name, settings.smtp_from),
                      recipients=[settings.contact_email or settings.smtp_user])
        msg.body = "This is a test email sent from Client Reporter."
        mail.send(msg)
        flash("Test email sent successfully.", "success")
    except Exception as e:
        flash(f"Failed to send test email: {str(e)}", "error")
        
    return redirect(url_for("settings.index"))
