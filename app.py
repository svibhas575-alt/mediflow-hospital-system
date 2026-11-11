from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import csv
import io
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-before-deployment")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "mediflow.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
os.makedirs(app.instance_path, exist_ok=True)
db = SQLAlchemy(app)

# This is a functional educational/local-use application. Do not enter real patient data
# or deploy it for clinical use without a security, privacy, and regulatory review.

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(30), default="")
    email = db.Column(db.String(120), default="")
    address = db.Column(db.Text, default="")
    blood_group = db.Column(db.String(5), default="")
    emergency_contact = db.Column(db.String(100), default="")
    notes = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointments = db.relationship("Appointment", backref="patient", lazy=True)
    admissions = db.relationship("Admission", backref="patient", lazy=True)

    @property
    def age(self):
        if not self.dob:
            return "—"
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), default="")
    doctors = db.relationship("Doctor", backref="department", lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=False)
    phone = db.Column(db.String(30), default="")
    active = db.Column(db.Boolean, default=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(250), default="")
    status = db.Column(db.String(20), default="Scheduled")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    doctor = db.relationship("Doctor")

class Bed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ward = db.Column(db.String(80), nullable=False)
    bed_number = db.Column(db.String(20), nullable=False, unique=True)
    status = db.Column(db.String(20), default="Available")
    notes = db.Column(db.String(200), default="")

class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    bed_id = db.Column(db.Integer, db.ForeignKey("bed.id"), nullable=False)
    admitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    discharged_at = db.Column(db.DateTime, nullable=True)
    diagnosis = db.Column(db.String(250), default="")
    status = db.Column(db.String(20), default="Admitted")
    bed = db.relationship("Bed")

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="Unpaid")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    patient = db.relationship("Patient")

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), default="General")
    quantity = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=5)
    unit = db.Column(db.String(20), default="units")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(250), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def log(action, details=""):
    db.session.add(ActivityLog(action=action, details=details))

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None

def parse_datetime(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M")

@app.context_processor
def inject_globals():
    return {"today": date.today(), "now": datetime.now()}

@app.route("/")
def dashboard():
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    stats = {
        "patients": Patient.query.count(),
        "appointments": Appointment.query.filter(Appointment.scheduled_at >= today_start, Appointment.scheduled_at <= today_end).count(),
        "beds": Bed.query.count(),
        "occupied": Bed.query.filter_by(status="Occupied").count(),
        "unpaid": db.session.query(db.func.coalesce(db.func.sum(Invoice.amount), 0)).filter_by(status="Unpaid").scalar(),
        "low_stock": InventoryItem.query.filter(InventoryItem.quantity <= InventoryItem.reorder_level).count()
    }
    upcoming = Appointment.query.filter(Appointment.scheduled_at >= datetime.now(), Appointment.status == "Scheduled").order_by(Appointment.scheduled_at).limit(8).all()
    recent = Patient.query.order_by(Patient.created_at.desc()).limit(6).all()
    activity = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(8).all()
    return render_template("dashboard.html", stats=stats, upcoming=upcoming, recent=recent, activity=activity)

@app.route("/patients")
def patients():
    q = request.args.get("q", "").strip()
    query = Patient.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Patient.name.ilike(like), Patient.mrn.ilike(like), Patient.phone.ilike(like)))
    return render_template("patients.html", patients=query.order_by(Patient.created_at.desc()).all(), q=q)

@app.route("/patients/new", methods=["GET", "POST"])
def patient_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        gender = request.form.get("gender", "")
        if not name or gender not in ["Female", "Male", "Other", "Prefer not to say"]:
            flash("Enter a patient name and select a valid gender.", "error")
            return redirect(url_for("patient_new"))
        dob = parse_date(request.form.get("dob"))
        mrn = f"MF-{datetime.now():%y%m%d%H%M%S%f}"[-15:]
        patient = Patient(mrn=mrn, name=name, dob=dob, gender=gender,
            phone=request.form.get("phone", "").strip(), email=request.form.get("email", "").strip(),
            address=request.form.get("address", "").strip(), blood_group=request.form.get("blood_group", ""),
            emergency_contact=request.form.get("emergency_contact", "").strip(),
            notes=request.form.get("notes", "").strip())
        db.session.add(patient)
        log("Patient registered", f"{name} · {mrn}")
        db.session.commit()
        flash(f"Patient {name} registered. Medical record number: {mrn}", "success")
        return redirect(url_for("patient_detail", patient_id=patient.id))
    return render_template("patient_form.html", patient=None)

@app.route("/patients/<int:patient_id>")
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    invoices = Invoice.query.filter_by(patient_id=patient.id).order_by(Invoice.created_at.desc()).all()
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.scheduled_at.desc()).all()
    admissions = Admission.query.filter_by(patient_id=patient.id).order_by(Admission.admitted_at.desc()).all()
    return render_template("patient_detail.html", patient=patient, invoices=invoices, appointments=appointments, admissions=admissions)

@app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
def patient_edit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        patient.name = request.form.get("name", "").strip()
        patient.gender = request.form.get("gender", patient.gender)
        patient.dob = parse_date(request.form.get("dob"))
        patient.phone = request.form.get("phone", "").strip()
        patient.email = request.form.get("email", "").strip()
        patient.address = request.form.get("address", "").strip()
        patient.blood_group = request.form.get("blood_group", "")
        patient.emergency_contact = request.form.get("emergency_contact", "").strip()
        patient.notes = request.form.get("notes", "").strip()
        patient.status = request.form.get("status", patient.status)
        log("Patient updated", f"{patient.name} · {patient.mrn}")
        db.session.commit()
        flash("Patient record updated.", "success")
        return redirect(url_for("patient_detail", patient_id=patient.id))
    return render_template("patient_form.html", patient=patient)

@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    if request.method == "POST":
        try:
            patient = Patient.query.get_or_404(int(request.form["patient_id"]))
            doctor = Doctor.query.get_or_404(int(request.form["doctor_id"]))
            when = parse_datetime(request.form["scheduled_at"])
            if when < datetime.now():
                flash("Choose a future appointment date and time.", "error")
                return redirect(url_for("appointments"))
            conflict = Appointment.query.filter_by(doctor_id=doctor.id, scheduled_at=when, status="Scheduled").first()
            if conflict:
                flash("That doctor already has an appointment at this time.", "error")
                return redirect(url_for("appointments"))
            appt = Appointment(patient_id=patient.id, doctor_id=doctor.id, scheduled_at=when, reason=request.form.get("reason", "").strip())
            db.session.add(appt)
            log("Appointment created", f"{patient.name} with {doctor.name} at {when:%d %b %Y %H:%M}")
            db.session.commit()
            flash("Appointment scheduled.", "success")
        except (ValueError, KeyError):
            flash("Please complete all appointment fields.", "error")
        return redirect(url_for("appointments"))
    items = Appointment.query.order_by(Appointment.scheduled_at.desc()).all()
    return render_template("appointments.html", appointments=items, patients=Patient.query.filter_by(status="Active").all(), doctors=Doctor.query.filter_by(active=True).all())

@app.post("/appointments/<int:appointment_id>/status")
def appointment_status(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    status = request.form.get("status")
    if status not in ["Scheduled", "Checked in", "Completed", "Cancelled"]:
        flash("Invalid appointment status.", "error")
    else:
        appt.status = status
        log("Appointment status changed", f"Appointment #{appt.id}: {status}")
        db.session.commit()
        flash("Appointment status updated.", "success")
    return redirect(request.referrer or url_for("appointments"))

@app.route("/beds")
def beds():
    all_beds = Bed.query.order_by(Bed.ward, Bed.bed_number).all()
    active_admissions = Admission.query.filter_by(status="Admitted").all()
    return render_template("beds.html", beds=all_beds, admissions=active_admissions, patient_list=Patient.query.filter_by(status="Active").order_by(Patient.name).all())

@app.post("/beds/new")
def bed_new():
    ward, number = request.form.get("ward", "").strip(), request.form.get("bed_number", "").strip()
    if not ward or not number:
        flash("Ward and bed number are required.", "error")
    elif Bed.query.filter_by(bed_number=number).first():
        flash("That bed number already exists.", "error")
    else:
        db.session.add(Bed(ward=ward, bed_number=number))
        log("Bed added", f"{ward} · {number}")
        db.session.commit()
        flash("Bed added.", "success")
    return redirect(url_for("beds"))

@app.post("/beds/<int:bed_id>/admit")
def admit_patient(bed_id):
    bed = Bed.query.get_or_404(bed_id)
    patient_id = request.form.get("patient_id", type=int)
    patient = Patient.query.get_or_404(patient_id) if patient_id else None
    if bed.status != "Available" or not patient or patient.status != "Active":
        flash("Select an available bed and an active patient.", "error")
    elif Admission.query.filter_by(patient_id=patient.id, status="Admitted").first():
        flash("This patient already has an active admission.", "error")
    else:
        db.session.add(Admission(patient_id=patient.id, bed_id=bed.id, diagnosis=request.form.get("diagnosis", "").strip()))
        bed.status = "Occupied"
        log("Patient admitted", f"{patient.name} → {bed.bed_number}")
        db.session.commit()
        flash(f"{patient.name} admitted to {bed.bed_number}.", "success")
    return redirect(url_for("beds"))

@app.post("/admissions/<int:admission_id>/discharge")
def discharge(admission_id):
    admission = Admission.query.get_or_404(admission_id)
    if admission.status == "Admitted":
        admission.status = "Discharged"
        admission.discharged_at = datetime.utcnow()
        admission.bed.status = "Available"
        log("Patient discharged", f"{admission.patient.name} from {admission.bed.bed_number}")
        db.session.commit()
        flash("Patient discharged and bed marked available.", "success")
    return redirect(url_for("beds"))

@app.route("/doctors", methods=["GET", "POST"])
def doctors():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        specialization = request.form.get("specialization", "").strip()
        dept_id = request.form.get("department_id", type=int)
        if not name or not specialization or not Department.query.get(dept_id):
            flash("Complete all doctor details.", "error")
        else:
            db.session.add(Doctor(name=name, specialization=specialization, department_id=dept_id, phone=request.form.get("phone", "").strip()))
            log("Doctor added", name)
            db.session.commit()
            flash("Doctor added to directory.", "success")
        return redirect(url_for("doctors"))
    return render_template("doctors.html", doctors=Doctor.query.order_by(Doctor.name).all(), departments=Department.query.order_by(Department.name).all())

@app.route("/billing", methods=["GET", "POST"])
def billing():
    if request.method == "POST":
        patient = Patient.query.get(request.form.get("patient_id", type=int))
        try:
            amount = Decimal(request.form.get("amount", "0"))
            if amount <= 0 or not amount.is_finite():
                raise InvalidOperation()
            if not patient:
                raise ValueError()
        except (InvalidOperation, ValueError):
            flash("Select a patient and enter a valid positive amount.", "error")
            return redirect(url_for("billing"))
        invoice = Invoice(patient_id=patient.id, description=request.form.get("description", "").strip() or "Hospital services", amount=amount)
        db.session.add(invoice)
        log("Invoice created", f"{patient.name} · ₹{amount}")
        db.session.commit()
        flash("Invoice created.", "success")
        return redirect(url_for("billing"))
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    total = sum((i.amount for i in invoices), Decimal("0"))
    paid = sum((i.amount for i in invoices if i.status == "Paid"), Decimal("0"))
    return render_template("billing.html", invoices=invoices, patients=Patient.query.all(), total=total, paid=paid, unpaid=total-paid)

@app.post("/invoices/<int:invoice_id>/pay")
def invoice_pay(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.status == "Unpaid":
        invoice.status = "Paid"
        invoice.paid_at = datetime.utcnow()
        log("Invoice paid", f"Invoice #{invoice.id} · ₹{invoice.amount}")
        db.session.commit()
        flash("Invoice marked as paid.", "success")
    return redirect(url_for("billing"))

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            quantity = int(request.form.get("quantity", "0"))
            reorder = int(request.form.get("reorder_level", "0"))
            if not name or quantity < 0 or reorder < 0:
                raise ValueError()
        except ValueError:
            flash("Enter a name and valid non-negative stock numbers.", "error")
            return redirect(url_for("inventory"))
        db.session.add(InventoryItem(name=name, category=request.form.get("category", "General"), quantity=quantity, reorder_level=reorder, unit=request.form.get("unit", "units")))
        log("Inventory item added", name)
        db.session.commit()
        flash("Inventory item added.", "success")
        return redirect(url_for("inventory"))
    items = InventoryItem.query.order_by(InventoryItem.name).all()
    return render_template("inventory.html", items=items)

@app.post("/inventory/<int:item_id>/adjust")
def inventory_adjust(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    try:
        delta = int(request.form.get("delta", "0"))
        if item.quantity + delta < 0:
            raise ValueError()
        item.quantity += delta
        log("Inventory adjusted", f"{item.name}: {delta:+d} {item.unit}")
        db.session.commit()
        flash("Stock updated.", "success")
    except ValueError:
        flash("Invalid adjustment: stock cannot become negative.", "error")
    return redirect(url_for("inventory"))

@app.get("/reports")
def reports():
    paid = Invoice.query.filter_by(status="Paid").all()
    unpaid = Invoice.query.filter_by(status="Unpaid").all()
    return render_template("reports.html", patients=Patient.query.count(), appointments=Appointment.query.count(),
        admissions=Admission.query.filter_by(status="Admitted").count(), beds=Bed.query.count(),
        occupied=Bed.query.filter_by(status="Occupied").count(),
        revenue=sum((i.amount for i in paid), Decimal("0")),
        outstanding=sum((i.amount for i in unpaid), Decimal("0")),
        low_stock=InventoryItem.query.filter(InventoryItem.quantity <= InventoryItem.reorder_level).all())

@app.get("/reports/patients.csv")
def export_patients():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["MRN", "Name", "Date of birth", "Gender", "Phone", "Email", "Status"])
    for p in Patient.query.order_by(Patient.id).all():
        writer.writerow([p.mrn, p.name, p.dob or "", p.gender, p.phone, p.email, p.status])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=mediflow-patients.csv"})

@app.get("/activity")
def activity():
    return render_template("activity.html", entries=ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(200).all())

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

def seed():
    if Department.query.count():
        return
    departments = [
        Department(name="Cardiology", description="Heart and cardiovascular care"),
        Department(name="Neurology", description="Brain and nervous system"),
        Department(name="Orthopaedics", description="Bones, joints and mobility"),
        Department(name="General Medicine", description="Primary and general care"),
        Department(name="Paediatrics", description="Child and adolescent care"),
        Department(name="Diagnostics", description="Laboratory and imaging services")
    ]
    db.session.add_all(departments)
    db.session.flush()
    doctors = [
        Doctor(name="Dr. Neha Kapoor", specialization="Cardiologist", department_id=departments[0].id),
        Doctor(name="Dr. Rahul Iyer", specialization="Neurologist", department_id=departments[1].id),
        Doctor(name="Dr. Priya Shah", specialization="General Physician", department_id=departments[3].id),
        Doctor(name="Dr. Meera Rao", specialization="Paediatrician", department_id=departments[4].id),
    ]
    db.session.add_all(doctors)
    db.session.add_all([
        Bed(ward="ICU", bed_number="ICU-01"), Bed(ward="ICU", bed_number="ICU-02"),
        Bed(ward="General", bed_number="GEN-101"), Bed(ward="General", bed_number="GEN-102"),
        Bed(ward="Private", bed_number="PVT-201"), Bed(ward="Emergency", bed_number="ER-01")
    ])
    log("System initialized", "MediFlow database created")
    db.session.commit()

with app.app_context():
    db.create_all()
    seed()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
