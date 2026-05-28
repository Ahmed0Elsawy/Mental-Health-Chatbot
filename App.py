from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from cryptography.fernet import Fernet
import uuid
import hashlib
import os
import re
from functools import wraps

app = Flask(__name__, template_folder=('B:\\menteal_health\\templates'))
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)  # Improved secret key management


# Load the key from the file for encryption (still needed for non-password fields)
def load_key():
    try:
        return open("secret.key", "rb").read()
    except FileNotFoundError:
        # Generate a key if it doesn't exist
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
        return key


key = load_key()
cipher_suite = Fernet(key)


# Password hashing function
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(32)  # Generate a random salt

    # Use SHA-256 with salt for secure password hashing
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    # Return both the salt and the hash
    return salt + pwdhash


# Verify password
def verify_password(stored_password, provided_password):
    # Extract the salt (first 32 bytes)
    salt = stored_password[:32]

    # Hash the provided password with the extracted salt
    new_hash = hash_password(provided_password, salt)

    # Compare the result with the stored password hash
    return new_hash == stored_password


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def init_db():
    try:
        conn = sqlite3.connect('mental_health.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY NOT NULL,          
                name TEXT NOT NULL,
                cgpa REAL,
                college TEXT,
                email TEXT,
                gender TEXT,
                phone TEXT UNIQUE,
                username TEXT UNIQUE NOT NULL,
                password BLOB,  # Changed to BLOB for binary hash storage
                emotional_state TEXT,
                main_concerns TEXT,
                coping_strategies TEXT,
                support_type TEXT,
                distress_level INTEGER,
                academic_challenges TEXT,
                physical_wellbeing TEXT,
                support_network TEXT,
                daily_routine TEXT,
                setback_handling TEXT,
                help_seeking TEXT,
                health_challenges TEXT,
                substance_use TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()


init_db()


# Database connection with error handling
def get_db_connection():
    try:
        conn = sqlite3.connect('mental_health.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


# Form validation
def validate_signup_form(form):
    errors = []

    # Validate username (alphanumeric, 3-20 chars)
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', form['username']):
        errors.append("Username must be 3-20 characters and contain only letters, numbers, and underscores")

    # Validate password (at least 8 chars, one upper, one lower, one digit)
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', form['password']):
        errors.append("Password must be at least 8 characters and include uppercase, lowercase, and numbers")

    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', form['email']):
        errors.append("Please enter a valid email address")

    # Validate phone number
    if not re.match(r'^\+?[0-9]{10,15}$', form['phone']):
        errors.append("Please enter a valid phone number")

    return errors


@app.route('/')
def home():
    return render_template('Arabicorenglish.html')


@app.route('/Arabic_Home')
def arabic_home():
    return render_template('Arabic_Home.html')


@app.route('/Home')
def english_home():
    return render_template('home.html')


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Generate a unique ID if not provided
        id = request.form.get('id', str(uuid.uuid4()))
        name = request.form.get('name', '')
        cgpa = request.form.get('cgpa', '')
        college = request.form.get('college', '')
        email = request.form.get('email', '')
        gender = request.form.get('gender', '')
        phone = request.form.get('phone', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # Validate form inputs
        validation_errors = validate_signup_form(request.form)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('signup.html')

        # Encrypt user fields except password
        try:
            encrypted_name = cipher_suite.encrypt(name.encode())
            encrypted_cgpa = cipher_suite.encrypt(cgpa.encode())
            encrypted_college = cipher_suite.encrypt(college.encode())
            encrypted_email = cipher_suite.encrypt(email.encode())
            encrypted_gender = cipher_suite.encrypt(gender.encode())
            encrypted_phone = cipher_suite.encrypt(phone.encode())

            # Hash password instead of encrypting
            hashed_password = hash_password(password)

            conn = get_db_connection()
            if conn:
                try:
                    conn.execute('''
                        INSERT INTO users (id, name, cgpa, college, email, gender, phone, username, password) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (id, encrypted_name, encrypted_cgpa, encrypted_college, encrypted_email, encrypted_gender,
                          encrypted_phone, username, hashed_password))
                    conn.commit()
                    flash('Account created successfully. Please log in.', 'success')
                    return redirect(url_for('login'))
                except sqlite3.IntegrityError as e:
                    if "username" in str(e):
                        flash('Username already exists. Try a different one.', 'error')
                    elif "phone" in str(e):
                        flash('Phone number already registered.', 'error')
                    else:
                        flash(f'Registration error: {e}', 'error')
                finally:
                    conn.close()
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # Input validation
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')

        conn = get_db_connection()
        if conn:
            try:
                user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

                if user and verify_password(user['password'], password):
                    # Update last login timestamp
                    conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
                    conn.commit()

                    # Store user info in session
                    session['user_id'] = user['id']
                    session['username'] = username

                    flash('Login successful!', 'success')
                    return redirect(url_for('questionnaire'))
                else:
                    # Use generic error message for security
                    flash('Invalid username or password', 'error')
            except Exception as e:
                flash(f'Login error: {e}', 'error')
            finally:
                conn.close()

    return render_template('login.html')


@app.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    user_id = session.get('user_id')

    if request.method == 'POST':
        try:
            # Collect form data with default values
            emotional_state = request.form.get('emotional_state', '')
            main_concerns = request.form.get('main_concerns', '')
            coping_strategies = request.form.get('coping_strategies', '')
            support_type = request.form.get('support_type', '')
            distress_level = request.form.get('distress_level', 0)
            academic_challenges = request.form.get('academic_challenges', '')
            physical_wellbeing = request.form.get('physical_wellbeing', '')
            support_network = request.form.get('support_network', '')
            daily_routine = request.form.get('daily_routine', '')
            setback_handling = request.form.get('setback_handling', '')
            help_seeking = request.form.get('help_seeking', '')
            health_challenges = request.form.get('health_challenges', '')
            substance_use = request.form.get('substance_use', '')

            # Validate distress_level is an integer
            try:
                distress_level = int(distress_level)
                if distress_level < 0 or distress_level > 10:
                    raise ValueError("Distress level must be between 0 and 10")
            except ValueError:
                flash('Distress level must be a number between 0 and 10', 'error')
                return render_template('questionnaire.html', user_id=user_id)

            # Encrypt questionnaire responses
            encrypted_emotional_state = cipher_suite.encrypt(emotional_state.encode())
            encrypted_main_concerns = cipher_suite.encrypt(main_concerns.encode())
            encrypted_coping_strategies = cipher_suite.encrypt(coping_strategies.encode())
            encrypted_support_type = cipher_suite.encrypt(support_type.encode())
            encrypted_academic_challenges = cipher_suite.encrypt(academic_challenges.encode())
            encrypted_physical_wellbeing = cipher_suite.encrypt(physical_wellbeing.encode())
            encrypted_support_network = cipher_suite.encrypt(support_network.encode())
            encrypted_daily_routine = cipher_suite.encrypt(daily_routine.encode())
            encrypted_setback_handling = cipher_suite.encrypt(setback_handling.encode())
            encrypted_help_seeking = cipher_suite.encrypt(help_seeking.encode())
            encrypted_health_challenges = cipher_suite.encrypt(health_challenges.encode())
            encrypted_substance_use = cipher_suite.encrypt(substance_use.encode())

            # Update the database with encrypted responses
            conn = get_db_connection()
            if conn:
                try:
                    conn.execute('''
                        UPDATE users SET 
                            emotional_state = ?, 
                            main_concerns = ?, 
                            coping_strategies = ?,
                            support_type = ?, 
                            distress_level = ?, 
                            academic_challenges = ?, 
                            physical_wellbeing = ?,
                            support_network = ?, 
                            daily_routine = ?, 
                            setback_handling = ?,
                            help_seeking = ?, 
                            health_challenges = ?, 
                            substance_use = ? 
                        WHERE id = ?
                    ''', (encrypted_emotional_state, encrypted_main_concerns, encrypted_coping_strategies,
                          encrypted_support_type, distress_level, encrypted_academic_challenges,
                          encrypted_physical_wellbeing, encrypted_support_network, encrypted_daily_routine,
                          encrypted_setback_handling, encrypted_help_seeking, encrypted_health_challenges,
                          encrypted_substance_use, user_id))
                    conn.commit()
                    flash('Responses recorded successfully.', 'success')
                    return redirect(url_for('home'))
                except Exception as e:
                    flash(f'Error saving responses: {e}', 'error')
                finally:
                    conn.close()
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')

    return render_template('questionnaire.html', user_id=user_id)


# Arabic routes with similar improvements
@app.route('/Arabic_login', methods=['GET', 'POST'])
def Alogin():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # Input validation
        if not username or not password:
            flash('الرجاء إدخال اسم المستخدم وكلمة المرور', 'error')
            return render_template('Arabic_login.html')

        conn = get_db_connection()
        if conn:
            try:
                user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

                if user and verify_password(user['password'], password):
                    # Update last login timestamp
                    conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
                    conn.commit()

                    # Store user info in session
                    session['user_id'] = user['id']
                    session['username'] = username

                    flash('تم تسجيل الدخول بنجاح!', 'success')
                    return redirect(url_for('Aquestionnaire'))
                else:
                    flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            except Exception as e:
                flash(f'خطأ في تسجيل الدخول: {e}', 'error')
            finally:
                conn.close()

    return render_template('Arabic_login.html')


@app.route('/Arabic_questionnaire', methods=['GET', 'POST'])
@login_required
def Aquestionnaire():
    user_id = session.get('user_id')

    if request.method == 'POST':
        try:
            # Collect form data with default values
            emotional_state = request.form.get('emotional_state', '')
            main_concerns = request.form.get('main_concerns', '')
            coping_strategies = request.form.get('coping_strategies', '')
            support_type = request.form.get('support_type', '')
            distress_level = request.form.get('distress_level', 0)
            academic_challenges = request.form.get('academic_challenges', '')
            physical_wellbeing = request.form.get('physical_wellbeing', '')
            support_network = request.form.get('support_network', '')
            daily_routine = request.form.get('daily_routine', '')
            setback_handling = request.form.get('setback_handling', '')
            help_seeking = request.form.get('help_seeking', '')
            health_challenges = request.form.get('health_challenges', '')
            substance_use = request.form.get('substance_use', '')

            # Validate distress_level is an integer
            try:
                distress_level = int(distress_level)
                if distress_level < 0 or distress_level > 10:
                    raise ValueError("Distress level must be between 0 and 10")
            except ValueError:
                flash('مستوى الضغط يجب أن يكون رقمًا بين 0 و 10', 'error')
                return render_template('Arabic_questionnaire.html', user_id=user_id)

            # Encrypt questionnaire responses
            encrypted_emotional_state = cipher_suite.encrypt(emotional_state.encode())
            encrypted_main_concerns = cipher_suite.encrypt(main_concerns.encode())
            encrypted_coping_strategies = cipher_suite.encrypt(coping_strategies.encode())
            encrypted_support_type = cipher_suite.encrypt(support_type.encode())
            encrypted_academic_challenges = cipher_suite.encrypt(academic_challenges.encode())
            encrypted_physical_wellbeing = cipher_suite.encrypt(physical_wellbeing.encode())
            encrypted_support_network = cipher_suite.encrypt(support_network.encode())
            encrypted_daily_routine = cipher_suite.encrypt(daily_routine.encode())
            encrypted_setback_handling = cipher_suite.encrypt(setback_handling.encode())
            encrypted_help_seeking = cipher_suite.encrypt(help_seeking.encode())
            encrypted_health_challenges = cipher_suite.encrypt(health_challenges.encode())
            encrypted_substance_use = cipher_suite.encrypt(substance_use.encode())

            # Update the database with encrypted responses
            conn = get_db_connection()
            if conn:
                try:
                    conn.execute('''
                        UPDATE users SET 
                            emotional_state = ?, 
                            main_concerns = ?, 
                            coping_strategies = ?,
                            support_type = ?, 
                            distress_level = ?, 
                            academic_challenges = ?, 
                            physical_wellbeing = ?,
                            support_network = ?, 
                            daily_routine = ?, 
                            setback_handling = ?,
                            help_seeking = ?, 
                            health_challenges = ?, 
                            substance_use = ? 
                        WHERE id = ?
                    ''', (encrypted_emotional_state, encrypted_main_concerns, encrypted_coping_strategies,
                          encrypted_support_type, distress_level, encrypted_academic_challenges,
                          encrypted_physical_wellbeing, encrypted_support_network, encrypted_daily_routine,
                          encrypted_setback_handling, encrypted_help_seeking, encrypted_health_challenges,
                          encrypted_substance_use, user_id))
                    conn.commit()
                    flash('تم تسجيل الإجابات بنجاح.', 'success')
                    return redirect(url_for('arabic_home'))
                except Exception as e:
                    flash(f'خطأ في حفظ الإجابات: {e}', 'error')
                finally:
                    conn.close()
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'error')

    return render_template('Arabic_questionnaire.html', user_id=user_id)


@app.route('/Arabic_signup', methods=['GET', 'POST'])
def Asignup():
    if request.method == 'POST':
        # Generate a unique ID if not provided
        id = request.form.get('id', str(uuid.uuid4()))
        name = request.form.get('name', '')
        cgpa = request.form.get('cgpa', '')
        college = request.form.get('college', '')
        email = request.form.get('email', '')
        gender = request.form.get('gender', '')
        phone = request.form.get('phone', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # Validate form inputs (could add Arabic-specific validation if needed)
        validation_errors = validate_signup_form(request.form)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('Arabic_signup.html')

        # Encrypt user fields except password
        try:
            encrypted_name = cipher_suite.encrypt(name.encode())
            encrypted_cgpa = cipher_suite.encrypt(cgpa.encode())
            encrypted_college = cipher_suite.encrypt(college.encode())
            encrypted_email = cipher_suite.encrypt(email.encode())
            encrypted_gender = cipher_suite.encrypt(gender.encode())
            encrypted_phone = cipher_suite.encrypt(phone.encode())

            # Hash password instead of encrypting
            hashed_password = hash_password(password)

            conn = get_db_connection()
            if conn:
                try:
                    conn.execute('''
                        INSERT INTO users (id, name, cgpa, college, email, gender, phone, username, password) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (id, encrypted_name, encrypted_cgpa, encrypted_college, encrypted_email, encrypted_gender,
                          encrypted_phone, username, hashed_password))
                    conn.commit()
                    flash('تم إنشاء الحساب بنجاح. الرجاء تسجيل الدخول.', 'success')
                    return redirect(url_for('Alogin'))
                except sqlite3.IntegrityError as e:
                    if "username" in str(e):
                        flash('اسم المستخدم موجود بالفعل. جرب اسمًا آخر.', 'error')
                    elif "phone" in str(e):
                        flash('رقم الهاتف مسجل بالفعل.', 'error')
                    else:
                        flash(f'خطأ في التسجيل: {e}', 'error')
                finally:
                    conn.close()
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'error')

    return render_template('Arabic_signup.html')
# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=False)  # Set to False in production