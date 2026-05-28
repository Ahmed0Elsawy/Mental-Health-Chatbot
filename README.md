# Mental Health Support App

A bilingual (Arabic/English) Flask web app for student mental health check-ins. Students can sign up, log in, and complete a mental health questionnaire. All personal data is encrypted in the database.

---

## Features

- Bilingual support: English and Arabic interfaces
- Secure user registration and login
- Password hashing with PBKDF2-SHA256 + salt
- Fernet encryption for all stored personal data
- Mental health questionnaire with encrypted responses
- Session management with login required protection

---

## Project Structure

```
menteal_health/
├── app.py                        # Main Flask application
├── notebook67dc1c41f2.ipynb      # ML fine-tuning notebook (Falcon-7B with LoRA)
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .gitignore                    # Files excluded from Git
└── templates/
    ├── Arabicorenglish.html      # Language selection page
    ├── home.html                 # English home page
    ├── Arabic_Home.html          # Arabic home page
    ├── login.html                # English login
    ├── signup.html               # English signup
    ├── questionnaire.html        # English questionnaire
    ├── Arabic_login.html         # Arabic login
    ├── Arabic_signup.html        # Arabic signup
    ├── Arabic_questionnaire.html # Arabic questionnaire
    ├── 404.html                  # Not found error page
    └── 500.html                  # Server error page
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/menteal_health.git
cd menteal_health
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
copy .env.example .env      # Windows
# or
cp .env.example .env        # Mac/Linux
```

Edit `.env`:

```
SECRET_KEY=your-very-secret-random-key-here
```

### 5. Run the app

```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000`

---

## Security Notes

- `secret.key` is auto-generated on first run and is listed in `.gitignore` — **never upload it**
- `mental_health.db` contains real user data — **never upload it**
- Passwords are never stored in plain text; they use PBKDF2-SHA256 with a random salt
- All personal fields (name, email, phone, etc.) are Fernet-encrypted

---

## Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Language selection |
| `/Home` | GET | English home |
| `/Arabic_Home` | GET | Arabic home |
| `/signup` | GET, POST | English registration |
| `/login` | GET, POST | English login |
| `/questionnaire` | GET, POST | English questionnaire (login required) |
| `/Arabic_signup` | GET, POST | Arabic registration |
| `/Arabic_login` | GET, POST | Arabic login |
| `/Arabic_questionnaire` | GET, POST | Arabic questionnaire (login required) |
| `/logout` | GET | Logout and clear session |

---

## Requirements

- Python 3.8+
- Flask
- cryptography
# Mental-Health-Chatbot
