import os
import io
import json
import base64
from datetime import datetime
from flask import render_template, current_app
from models import db
from models.report import Report
from models.settings import CompanySettings
from services.mock_data import generate_metrics

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt


def chart_to_base64(labels, values, title, color="#1D4ED8"):
    fig, ax = plt.subplots(figsize=(6, 2.8))
    ax.bar(labels, values, color=color, edgecolor="white", linewidth=0.5)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.tick_params(labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def generate_pdf(client, period_start, period_end):
    """Generates a PDF report, saves it, and logs it to DB."""
    try:
        settings = CompanySettings.query.first()
        metrics = generate_metrics(client.id, period_start, period_end)
        
        # Build charts
        months_labels = ["M1", "M2", "M3", "M4", "M5", "M6"]
        monthly_sessions = [metrics["sessions"]] * 6 # Simplified for demo
        chart_b64 = chart_to_base64(months_labels, monthly_sessions, "Sessions Trend", color=settings.primary_color)
        
        source_labels = ["Organic", "Direct", "Social", "Referral", "Paid"]
        source_values = [
            metrics["source_organic"], metrics["source_direct"],
            metrics["source_social"], metrics["source_referral"],
            metrics["source_paid"]
        ]
        source_chart_b64 = chart_to_base64(source_labels, source_values, "Traffic Sources", color=settings.accent_color)
        
        # Render HTML template
        rendered_html = render_template(
            "reports/pdf.html",
            client=client,
            settings=settings,
            metrics=metrics,
            period_start=period_start,
            period_end=period_end,
            chart_b64=chart_b64,
            source_chart_b64=source_chart_b64
        )
        
        # Ensure static/reports exists
        reports_dir = os.path.join(current_app.root_path, "static", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"client_{client.id}_{period_start.strftime('%Y_%m')}.pdf"
        pdf_path = os.path.join(reports_dir, filename)
        
        try:
            from weasyprint import HTML
            HTML(string=rendered_html).write_pdf(pdf_path)
        except ImportError:
            current_app.logger.warning("WeasyPrint not installed. PDF generation skipped. Writing HTML for debug.")
            with open(pdf_path.replace('.pdf', '.html'), 'w', encoding='utf-8') as f:
                f.write(rendered_html)
        
        # Create record
        report = Report(
            client_id=client.id,
            period_start=period_start,
            period_end=period_end,
            pdf_path=f"static/reports/{filename}",
            status="generated",
            metrics_json=json.dumps(metrics)
        )
        db.session.add(report)
        db.session.commit()
        return report

    except Exception as e:
        current_app.logger.error(f"PDF generation failed: {e}")
        return None
