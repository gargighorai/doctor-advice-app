# Doctor Advice System

A Flask web application for managing doctor-patient advice, prescriptions, and digital records.

## 🔧 Features

- Multi-doctor login/register
- Add/edit patient advice
- Prescribe multiple drugs with autocomplete
- Download PDF with QR code, signature, and dynamic layout
- Admin panel to manage drugs (add/remove/import/export JSON)

## 🚀 Live Demo

[🌐 Render Deployment Link](#) – _(Add your link here)_

## 🛠️ Tech Stack

- Flask
- Jinja2
- Bootstrap 5
- SQLite / PostgreSQL
- Flask-Login
- XHTML2PDF + QR Code
- Select2 (autocomplete)

## 📦 Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/doctor-advice-app.git
cd doctor-advice-app
```

2. Create and activate virtual environment

### On Windows (CMD)
```bash
python -m venv venv
venv\Scripts\activate
```

### On Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### On macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Copy the environment file

```bash
cp .env.example .env
```

5. Run the app

```bash
python app.py
```

6. Admin login

```
Username: admin
Password: admin123
```

## ⚙️ Deployment (Render.com)

- Add `Procfile`
- Set environment variables:
  - `SECRET_KEY`
  - `DATABASE_URL`

## 📄 License

MIT License – Feel free to use and extend.
