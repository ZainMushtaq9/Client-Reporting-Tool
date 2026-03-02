from datetime import datetime
from . import db

class Report(db.Model):
    __tablename__ = "reports"
    id            = db.Column(db.Integer, primary_key=True)
    client_id     = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    period_start  = db.Column(db.Date,    nullable=False)
    period_end    = db.Column(db.Date,    nullable=False)
    generated_at  = db.Column(db.DateTime,default=datetime.utcnow)
    pdf_path      = db.Column(db.String(300), nullable=True)
    emailed       = db.Column(db.Boolean, default=False)
    emailed_at    = db.Column(db.DateTime,nullable=True)
    status        = db.Column(db.String(20),default="generated")  # generated|sent|error
    metrics_json  = db.Column(db.Text,    nullable=True)  # JSON snapshot at generation time
