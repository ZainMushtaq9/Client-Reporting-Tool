from . import db

class CompanySettings(db.Model):
    __tablename__ = "company_settings"
    id             = db.Column(db.Integer, primary_key=True)
    company_name   = db.Column(db.String(120), default="My Company")
    description    = db.Column(db.Text,        default="")
    logo_filename  = db.Column(db.String(200), default="")
    primary_color  = db.Column(db.String(7),   default="#1D4ED8")
    accent_color   = db.Column(db.String(7),   default="#065F46")
    contact_email  = db.Column(db.String(120), default="")
    smtp_host      = db.Column(db.String(200), default="smtp.gmail.com")
    smtp_port      = db.Column(db.Integer,     default=587)
    smtp_user      = db.Column(db.String(120), default="")
    smtp_pass      = db.Column(db.String(200), default="")
    smtp_from      = db.Column(db.String(120), default="")
    # Always ONE row — access with: CompanySettings.query.first()
