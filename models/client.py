from datetime import datetime
from . import db

class Client(db.Model):
    __tablename__ = "clients"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), nullable=False)  # Receives reports
    website       = db.Column(db.String(200), default="")
    industry      = db.Column(db.String(80),  default="Other")
    report_email  = db.Column(db.Boolean,     default=True)
    report_freq   = db.Column(db.String(20),  default="monthly")  # "monthly"|"weekly"
    report_day    = db.Column(db.Integer,     default=1)   # Day of month 1-28
    show_ads      = db.Column(db.Boolean,     default=True)
    show_email_mkt= db.Column(db.Boolean,     default=True)
    notes         = db.Column(db.Text,        default="")  # Internal only
    is_active     = db.Column(db.Boolean,     default=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    reports       = db.relationship("Report", backref="client", lazy=True,
                       cascade="all, delete-orphan")
