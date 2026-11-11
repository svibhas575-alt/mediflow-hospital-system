# MediFlow — Hospital Management System

A functional Flask + SQLite hospital operations application. It is designed as a local software project you can run, inspect, extend, and publish as a GitHub repository.

## Features

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
