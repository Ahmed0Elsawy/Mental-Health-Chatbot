from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Use the same key used in the encryption app
key = b'HWXRFHbS1X_KQUuOJUQ0M_clAvDZotOgN8ce2I1Zh2E='  # Replace this with your actual key
cipher_suite = Fernet(key)


def get_db_connection():
    conn = sqlite3.connect('mental_health.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=['GET', 'POST'])
def decrypt_user():
    if request.method == 'POST':
        id = request.form['id']  # Get ID from form

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
        conn.close()

        if user:
            try:
                # Decrypt the fields
                decrypted_name = cipher_suite.decrypt(user['name']).decode()
                decrypted_cgpa = cipher_suite.decrypt(user['cgpa']).decode()
                decrypted_college = cipher_suite.decrypt(user['college']).decode()
                decrypted_email = cipher_suite.decrypt(user['email']).decode()
                decrypted_gender = cipher_suite.decrypt(user['gender']).decode()
                decrypted_phone = cipher_suite.decrypt(user['phone']).decode()
                decrypted_password = cipher_suite.decrypt(user['password']).decode()
                decrypted_emotional_state = cipher_suite.decrypt(user['emotional_state']).decode()
                decrypted_main_concerns = cipher_suite.decrypt(user['main_concerns']).decode()
                decrypted_coping_strategies = cipher_suite.decrypt(user['coping_strategies']).decode()
                decrypted_support_type = cipher_suite.decrypt(user['support_type']).decode()
                decrypted_distress_level = user['distress_level']  # Assuming distress_level is stored as integer
                decrypted_academic_challenges = cipher_suite.decrypt(user['academic_challenges']).decode()
                decrypted_physical_wellbeing = cipher_suite.decrypt(user['physical_wellbeing']).decode()
                decrypted_support_network = cipher_suite.decrypt(user['support_network']).decode()
                decrypted_daily_routine = cipher_suite.decrypt(user['daily_routine']).decode()
                decrypted_setback_handling = cipher_suite.decrypt(user['setback_handling']).decode()
                decrypted_help_seeking = cipher_suite.decrypt(user['help_seeking']).decode()
                decrypted_health_challenges = cipher_suite.decrypt(user['health_challenges']).decode()
                decrypted_substance_use = cipher_suite.decrypt(user['substance_use']).decode()


                # Create a dictionary with the decrypted data
                decrypted_data = {
                    'id': user['id'],  # ID is plain text
                    'name': decrypted_name,
                    'cgpa': decrypted_cgpa,
                    'college': decrypted_college,
                    'email': decrypted_email,
                    'gender': decrypted_gender,
                    'phone': decrypted_phone,
                    'password': decrypted_password,
                    'emotional_state': decrypted_emotional_state,
                    'main_concerns': decrypted_main_concerns,
                    'coping_strategies': decrypted_coping_strategies,
                    'support_type': decrypted_support_type,
                    'distress_level': decrypted_distress_level,
                    'academic_challenges': decrypted_academic_challenges,
                    'physical_wellbeing': decrypted_physical_wellbeing,
                    'support_network': decrypted_support_network,
                    'daily_routine': decrypted_daily_routine,
                    'setback_handling': decrypted_setback_handling,
                    'help_seeking': decrypted_help_seeking,
                    'health_challenges': decrypted_health_challenges,
                    'substance_use': decrypted_substance_use
                }

                return render_template('decrypted_data.html', data=decrypted_data)
            except Exception as e:
                flash(f"Decryption failed: {str(e)}", 'error')
        else:
                flash('User not found', 'error')
    return render_template('decrypt_user.html')

if __name__ == '__main__':
    app.run(debug=True)
