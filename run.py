from app import create_app
from models import db
from models.user import User
from models.client import Client
from models.settings import CompanySettings
from werkzeug.security import generate_password_hash

app = create_app()

def seed_database():
    # Default admin user
    if not User.query.filter_by(username="admin").first():
        db.session.add(User(
            username="admin",
            email="admin@company.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            is_active=True
        ))
        print("[SEED] Admin user created: admin / admin123")
        print("[!]   Change this password immediately after first login!")

    # Company settings
    if not CompanySettings.query.first():
        db.session.add(CompanySettings(company_name="My Company"))

    # Demo clients
    if Client.query.count() == 0:
        db.session.add_all([
            Client(name="Maple Coffee Roasters",  email="client1@demo.com",
                   industry="Local Business",      report_freq="monthly"),
            Client(name="SwiftCart E-commerce",   email="client2@demo.com",
                   industry="E-commerce",          report_freq="monthly"),
            Client(name="NovaTech SaaS",          email="client3@demo.com",
                   industry="SaaS",                report_freq="weekly"),
        ])
        print("[SEED] 3 demo clients created")

    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_database()
    print("\n  Client Reporter running at: http://localhost:5000")
    print("  Login: admin / admin123  (CHANGE THIS PASSWORD NOW)\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
