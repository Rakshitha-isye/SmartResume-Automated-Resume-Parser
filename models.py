from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, default="Not detected")
    email = db.Column(db.String(160), nullable=False, default="")
    phone = db.Column(db.String(50), nullable=False, default="")
    skills = db.Column(db.Text, nullable=False, default="")
    education = db.Column(db.Text, nullable=False, default="")
    filename = db.Column(db.String(255), nullable=False, unique=True)
    original_filename = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
