# MediFlow — Hospital Management System

A Flask hospital operations and patient-portal prototype with role-based accounts. It supports SQLite for local development and PostgreSQL for cloud hosting.

## Phase 1 features

- Separate Front Desk/staff and patient sign-in portals.
- Front Desk username can be configured as `Vibhash`; its password is loaded from a private environment variable and stored only as a password hash.
- Patient self-registration creates a linked patient record and portal account.
- Hospital registration is protected by a private invitation code configured by the operator.
- Passwords are stored as secure hashes; authenticated sessions and CSRF protection are enabled.
- Patient accounts can only view their own appointments, invoices, and admission entries.
- Hospital routes require a hospital account; patient accounts cannot access hospital operations.
- PostgreSQL support for persistent cloud data; SQLite remains available locally.

## Existing hospital features

- **Dashboard:** live totals, bed utilisation, outstanding invoice value, upcoming appointments and recent activity.
- **Patient records:** create, search, view and edit patient profiles; automatic medical record numbers.
- **Appointments:** schedule visits, link patients and doctors, prevent exact-time doctor conflicts, and update appointment status.
- **Admissions & beds:** add beds, admit active patients, prevent duplicate active admissions, discharge patients and release beds.
- **Doctors & departments:** seeded departments and doctors; add doctors to the directory.
- **Billing:** create patient invoices, calculate totals and mark invoices paid.
- **Inventory:** maintain stock counts, reorder thresholds, low-stock warnings and stock adjustments.
- **Reports:** operational summaries and CSV export of the patient directory.
- **Activity log:** records important actions for traceability.
- **Persistent storage:** SQLite database is created automatically in `instance/mediflow.db`.

## Requirements

- Windows 10/11, macOS or Linux
- Python 3.10 or newer
- Internet connection only for the first installation of Python packages (Google Fonts are optional at runtime)

## Run on Windows 11

1. Extract the ZIP.
2. Open the extracted `mediflow-hospital-system` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

5. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt terminal and run:

   ```cmd
   .venv\Scripts\activate.bat
   ```

6. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

7. Start the server:

   ```powershell
   py app.py
   ```

8. Open **http://127.0.0.1:5000** in your browser.

Stop the server with `Ctrl + C`.

## Publish to GitHub

1. Create a new empty repository on GitHub (do not add a README if you already have this one).
2. In VS Code, open the project folder.
3. Open the terminal and run:

   ```powershell
   git init
   git add .
   git commit -m "Initial MediFlow hospital management system"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   git push -u origin main
   ```

   Replace the URL with your repository URL. GitHub Desktop is also an option: **Add Existing Repository** → choose this folder → **Publish repository**.

## Project structure

```text
mediflow-hospital-system/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── instance/                 # created automatically; ignored by Git
├── templates/                # Jinja2 HTML pages
│   ├── base.html
│   ├── dashboard.html
│   ├── patients.html
│   ├── patient_form.html
│   ├── patient_detail.html
│   ├── appointments.html
│   ├── beds.html
│   ├── doctors.html
│   ├── billing.html
│   ├── inventory.html
│   ├── reports.html
│   ├── activity.html
│   └── 404.html
└── static/
    ├── style.css
    └── app.js
```

## Tech stack

- Python 3 / Flask — backend and routing
- Flask-SQLAlchemy / SQLAlchemy — data models and database operations
- SQLite — persistent relational database
- HTML5 + Jinja2 — server-rendered pages
- CSS3 — responsive interface
- JavaScript — small client-side interactions
- CSV — report export

## Important safety and deployment note

This is a working educational/local prototype, **not certified hospital software**. It does not include authenticated user accounts, role-based access control, encryption at rest, secure backups, consent workflows, clinical decision support validation, or jurisdiction-specific privacy/regulatory compliance. Do not store real patient or medical information in it or expose it to the public internet. Before any real-world deployment, have qualified healthcare IT/security professionals add and test those controls and complete the required legal and clinical review.

The app seeds department, doctor and bed reference records on first launch. It does not seed fake patient records or fake financial transactions; you can create your own test records through the interface.


## Phase 1 setup (Windows 11 / local development)

1. Create and activate a virtual environment as described above.
2. Install packages: `py -m pip install -r requirements.txt`.
3. Set a development secret and hospital invitation code in PowerShell:

   ```powershell
   $env:SECRET_KEY = "replace-with-a-long-random-development-secret"
   $env:HOSPITAL_REGISTRATION_CODE = "your-private-hospital-invite-code"
   $env:FRONTDESK_USERNAME = "Vibhash"
   $env:FRONTDESK_PASSWORD = "choose-a-unique-password-of-12-or-more-characters"
   $env:COOKIE_SECURE = "0"
   py app.py
   ```

4. Open `http://127.0.0.1:5000/login`. Sign in to Front Desk with username `Vibhash` and the private password configured above. Patients create separate accounts using their own email addresses and passwords.

Patient registration creates a patient profile in this prototype. Hospital registration is intentionally invitation-only; do not publish the invitation code. Existing pre-Phase-1 SQLite databases are retained because the new account table is additive. Back up the database before upgrading.

## Cloud deployment (Render + PostgreSQL)

This repository includes `render.yaml`, `Procfile`, and `Dockerfile`. The blueprint provisions a PostgreSQL database and web service. In Render, review the blueprint, set a strong private `HOSPITAL_REGISTRATION_CODE`, and deploy. `SECRET_KEY` is generated by Render; HTTPS-only secure cookies are enabled. Keep the database credentials private. The free/temporary SQLite filesystem is not suitable for persistent cloud data; use the provisioned PostgreSQL database.

## Desktop distribution status

The Flask application remains browser-accessible locally and is cloud-ready at the application layer. A signed Windows installer / standalone desktop package is a later packaging phase; it is not included in Phase 1. The same Flask codebase is being kept for both deployment targets.

## Important safety and deployment note

**This is an educational prototype, not production hospital software.** Do not enter real patient information or expose it for clinical use. Before real deployment, obtain professional security, privacy, clinical, and legal review; implement verified identity, consent and guardian workflows, tenant isolation, audit controls, backups, encryption, monitoring, incident response, and applicable healthcare compliance. Patient self-registration currently creates a demo patient record; family/guardian access, prescriptions, and lab reports are not implemented in Phase 1.
