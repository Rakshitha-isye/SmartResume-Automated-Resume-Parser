import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from models import db, Candidate
from parser import parse_resume

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'smartresume.db'}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

db.init_app(app)
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    total = Candidate.query.count()
    latest = Candidate.query.order_by(Candidate.created_at.desc()).limit(5).all()
    return render_template("index.html", total=total, latest=latest)

@app.route("/candidates")
def candidates():
    q = request.args.get("q", "").strip()
    query = Candidate.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Candidate.name.ilike(like), Candidate.email.ilike(like),
                   Candidate.skills.ilike(like), Candidate.education.ilike(like))
        )
    records = query.order_by(Candidate.created_at.desc()).all()
    return render_template("candidates.html", candidates=records, q=q)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("resume")
        if not file or not file.filename:
            flash("Please choose a resume file.", "error")
            return redirect(url_for("upload"))
        if not allowed_file(file.filename):
            flash("Only PDF and DOCX files are supported.", "error")
            return redirect(url_for("upload"))

        original = secure_filename(file.filename)
        stored_name = f"{os.urandom(8).hex()}_{original}"
        path = UPLOAD_DIR / stored_name
        file.save(path)

        try:
            data = parse_resume(path)
            candidate = Candidate(
                name=data.get("name") or "Not detected",
                email=data.get("email") or "",
                phone=data.get("phone") or "",
                skills=", ".join(data.get("skills", [])),
                education="; ".join(data.get("education", [])),
                filename=stored_name,
                original_filename=original,
                extracted_text=data.get("text", "")[:20000]
            )
            db.session.add(candidate)
            db.session.commit()
            flash("Resume parsed and saved. Please review extracted details for accuracy.", "success")
            return redirect(url_for("candidate_detail", candidate_id=candidate.id))
        except Exception as exc:
            db.session.rollback()
            path.unlink(missing_ok=True)
            app.logger.exception("Resume parsing failed")
            flash(f"Could not process this file: {exc}", "error")
            return redirect(url_for("upload"))
    return render_template("upload.html")

@app.route("/candidate/<int:candidate_id>")
def candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    return render_template("candidate_detail.html", candidate=candidate)

@app.route("/candidate/<int:candidate_id>/delete", methods=["POST"])
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    if candidate.filename:
        (UPLOAD_DIR / candidate.filename).unlink(missing_ok=True)
    db.session.delete(candidate)
    db.session.commit()
    flash("Candidate record deleted.", "success")
    return redirect(url_for("candidates"))

@app.route("/resume/<path:filename>")
def download_resume(filename):
    # Only serve files that belong to a stored candidate record.
    candidate = Candidate.query.filter_by(filename=filename).first_or_404()
    return send_from_directory(app.config["UPLOAD_FOLDER"], candidate.filename,
                               as_attachment=True, download_name=candidate.original_filename)

@app.errorhandler(413)
def too_large(_):
    flash("File is too large. Maximum allowed size is 8 MB.", "error")
    return redirect(url_for("upload"))

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
