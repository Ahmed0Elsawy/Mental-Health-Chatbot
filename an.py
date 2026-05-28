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

@app.route('/', methods=['GET'])
def show_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    decrypted_users = []
    for user in users:
        try:
            decrypted_user = {
                'id': user['id'],  # ID is plain text
                'name': cipher_suite.decrypt(user['name']).decode(),
                'cgpa': cipher_suite.decrypt(user['cgpa']).decode(),
                'college': cipher_suite.decrypt(user['college']).decode(),
                'email': cipher_suite.decrypt(user['email']).decode(),
                'gender': cipher_suite.decrypt(user['gender']).decode(),
                'phone': cipher_suite.decrypt(user['phone']).decode(),
                'password': cipher_suite.decrypt(user['password']).decode(),
                'emotional_state': cipher_suite.decrypt(user['emotional_state']).decode(),
                'main_concerns': cipher_suite.decrypt(user['main_concerns']).decode(),
                'coping_strategies': cipher_suite.decrypt(user['coping_strategies']).decode(),
                'support_type': cipher_suite.decrypt(user['support_type']).decode(),
                'distress_level': user['distress_level'],  # Assuming distress_level is stored as integer
                'academic_challenges': cipher_suite.decrypt(user['academic_challenges']).decode(),
                'physical_wellbeing': cipher_suite.decrypt(user['physical_wellbeing']).decode(),
                'support_network': cipher_suite.decrypt(user['support_network']).decode(),
                'daily_routine': cipher_suite.decrypt(user['daily_routine']).decode(),
                'setback_handling': cipher_suite.decrypt(user['setback_handling']).decode(),
                'help_seeking': cipher_suite.decrypt(user['help_seeking']).decode(),
                'health_challenges': cipher_suite.decrypt(user['health_challenges']).decode(),
                'substance_use': cipher_suite.decrypt(user['substance_use']).decode()
            }
            decrypted_users.append(decrypted_user)
        except Exception as e:
            flash(f"Decryption failed for user ID {user['id']}: {str(e)}", 'error')

    return render_template('decrypted_data.html', users=decrypted_users)

if __name__ == '__main__':
    app.run(debug=True)
