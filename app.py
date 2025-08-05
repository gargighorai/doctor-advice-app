from flask import Flask, render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from xhtml2pdf import pisa
from io import BytesIO
import os, json
from flask import jsonify
import qrcode
import base64
from datetime import datetime
import base64
import qrcode
from io import BytesIO
from io import BytesIO
import qrcode
import base64
from datetime import datetime
from flask import send_file, render_template
from xhtml2pdf import pisa
from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ---------------- Models ----------------

class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

patient_drugs = db.Table('patient_drugs',
    db.Column('patient_id', db.Integer, db.ForeignKey('patient.id')),
    db.Column('drug_id', db.Integer, db.ForeignKey('drug.id'))
)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    complaint = db.Column(db.String(200))
    advice = db.Column(db.String(200))
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))
    drugs = db.relationship('Drug', secondary=patient_drugs, backref='patients')

@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(int(user_id))

# ---------------- Routes ----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        if Doctor.query.filter_by(username=username).first():
            flash("Username already exists.")
            return render_template("register.html")
        doctor = Doctor(name=name, username=username, password=password)
        db.session.add(doctor)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        doctor = Doctor.query.filter_by(username=request.form["username"]).first()
        if doctor and doctor.password == request.form["password"]:
            login_user(doctor)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/dashboard')
@login_required
def dashboard():
    patients = Patient.query.filter_by(doctor_id=current_user.id).all()
    return render_template("dashboard.html", patients=patients)

import os
from flask import send_file, redirect, url_for, flash, render_template
from flask_login import login_required

PDF_DIR = os.path.join("static", "pdfs")

@app.route('/pdfs')
@login_required
@admin_required
def list_pdfs():
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
    return render_template('list_pdfs.html', pdfs=pdf_files)

@app.route('/pdfs/download/<filename>')
@login_required
def download_pdf(filename):
    path = os.path.join(PDF_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    flash("File not found.", "danger")
    return redirect(url_for('list_pdfs'))

@app.route('/pdfs/delete/<filename>', methods=["POST"])
@login_required
@admin_required
def delete_pdf(filename):
    path = os.path.join(PDF_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f"{filename} deleted successfully.", "success")
    else:
        flash("File not found.", "danger")
    return redirect(url_for('list_pdfs'))

@app.route('/add_patient', methods=["POST"])
@login_required
def add_patient():
    p = Patient(
        name=request.form["name"],
        age=request.form["age"],
        complaint=request.form["complaint"],
        advice=request.form["advice"],
        doctor_id=current_user.id
    )
    db.session.add(p)
    db.session.commit()
    flash("Advice saved successfully!", "success")
    return redirect(url_for("dashboard"))


def format_date(date):
    """Format date like 2nd Aug 2025"""
    return date.strftime('%d{} %b %Y').replace(
        '1st', '1st').replace('2nd', '2nd').replace('3rd', '3rd').replace('11th', '11th').replace('12th', '12th').replace('13th', '13th') \
        if date.day in [1, 2, 3, 11, 12, 13] else date.strftime(f'%dth %b %Y')

@app.route('/download/<int:patient_id>')
@login_required
def download(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Generate QR code
    qr_data = f"Patient: {patient.name}, Age: {patient.age}, Doctor: {current_user.name}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Render HTML
    html = render_template(
        "patient_pdf.html",
        patient=patient,
        doctor=current_user,
        qr_code=qr_base64,
        current_date=format_date(datetime.now())
    )

    # Create PDF
    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    pdf.seek(0)

    # Clean filename
    filename = f"{patient.name.replace(' ', '_')} prescription.pdf"

    return send_file(pdf, download_name=filename, as_attachment=True)
###----------------- PDF Management i.e. delete PDF----------------
@app.route('/delete_pdf/<filename>')
@login_required
def delete_pdf(filename):
    path = os.path.join("static", "pdfs", filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f"{filename} deleted.")
    else:
        flash("File not found.")
    return redirect(url_for('dashboard'))

# ---------------- Admin Drug Management ----------------

@app.route('/admin/drugs')
@login_required
def manage_drugs():
    drugs = Drug.query.order_by(Drug.name).all()
    return render_template("admin_drugs.html", drugs=drugs)

@app.route('/admin/drugs/add', methods=["POST"])
@login_required
def add_drug():
    name = request.form.get("name", "").strip()
    if name:
        if not Drug.query.filter_by(name=name).first():
            db.session.add(Drug(name=name))
            db.session.commit()
            flash("Drug added successfully.", "success")
        else:
            flash("Drug already exists.", "warning")
    else:
        flash("Invalid drug name.", "danger")
    return redirect(url_for("manage_drugs"))

@app.route('/admin/drugs/delete/<int:drug_id>', methods=["POST"])
@login_required
def delete_drug(drug_id):
    drug = Drug.query.get_or_404(drug_id)
    db.session.delete(drug)
    db.session.commit()
    flash("Drug deleted", "danger")
    return redirect(url_for("manage_drugs"))

@app.route('/admin/drugs/export')
@login_required
def export_drugs():
    drugs = Drug.query.all()
    data = [{"id": drug.id, "name": drug.name} for drug in drugs]
    response = app.response_class(
        response=json.dumps(data, indent=2),
        mimetype='application/json'
    )
    response.headers.set("Content-Disposition", "attachment", filename="drugs.json")
    return response

@app.route('/admin/drugs/import', methods=['POST'])
@login_required
def import_drugs():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.json'):
        flash("Invalid file type. Please upload a .json file", "danger")
        return redirect(url_for('manage_drugs'))

    try:
        imported = json.load(file)
        count = 0
        for item in imported:
            name = item.get("name", "").strip()
            if name and not Drug.query.filter_by(name=name).first():
                db.session.add(Drug(name=name))
                count += 1
        db.session.commit()
        flash(f"{count} drugs imported successfully.", "success")
    except Exception as e:
        flash(f"Failed to import: {str(e)}", "danger")

    return redirect(url_for("manage_drugs"))

# ---------------- Advice Form with Autocomplete ----------------

@app.route('/give_advice', methods=["GET", "POST"])
@login_required
def give_advice():
    drugs = Drug.query.all()
    if request.method == "POST":
        name = request.form.get("patient_name")
        selected_drugs = request.form.getlist("drugs")
        advice = request.form.get("advice")
        if not name or not selected_drugs or not advice:
            flash("Please fill all fields", "warning")
            return redirect(url_for('give_advice'))

        # Store drugs as many-to-many
        drug_objs = Drug.query.filter(Drug.name.in_(selected_drugs)).all()
        new_patient = Patient(
            name=name,
            advice=advice,
            doctor_id=current_user.id,
            drugs=drug_objs
        )
        db.session.add(new_patient)
        db.session.commit()
        flash("Advice successfully saved!", "success")
        return redirect(url_for('dashboard'))
    return render_template("advice.html", drugs=drugs)

@app.route('/autocomplete/drugs')
@login_required
def autocomplete_drugs():
    term = request.args.get("term", "")
    results = Drug.query.filter(Drug.name.ilike(f"%{term}%")).all()
    return jsonify([{"name": d.name} for d in results])

# ---------------- App Entry ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not Doctor.query.filter_by(username='admin').first():
            admin = Doctor(name="Admin", username="admin", password="admin123")
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin doctor created: username=admin, password=admin123")

        try:
            port = int(os.environ.get("PORT", 5050))
        except ValueError:
            port = 5050
        app.run(debug=True, host='127.0.0.1', port=port)
