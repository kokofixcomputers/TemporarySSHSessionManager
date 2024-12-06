from flask import Flask, jsonify, render_template, request, redirect, session, url_for
import handler
import requests
import sqlite3
import base64
import configurationlib

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

config = configurationlib.Instance("config.json", format=configurationlib.Format.JSON)

try:
    REQUIRE_AUTH = config.get()["REQUIRE_AUTH"]
except:
    REQUIRE_AUTH = True

def authenticated(session):
    if REQUIRE_AUTH:
        return session.get('username') is not None
    return True

def create_database():
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS containers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  username TEXT,
                  password TEXT,
                  user TEXT,
                  port INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS session
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               user TEXT,
               session TEXT)
               ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    if authenticated(session):
        return render_template('home.html')
    else:
        return redirect(url_for('auth'))

@app.route('/create_container', methods=['POST'])
def create_container_route():
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."})
    name, username, password, port = handler.create_container()
    if name is not None:
        conn = sqlite3.connect('containers.db')
        c = conn.cursor()
        c.execute("INSERT INTO containers (name, username, password, user, port) VALUES (?, ?, ?, ?, ?)", (name, username, password, session['username'], port))
        conn.commit()
        conn.close()
    base_url_no_scheme = request.url_root.replace(request.scheme + '://', '', 1).rstrip('/')
    return jsonify({"name": name, "username": username, "hostname": base_url_no_scheme, "port": f"{port}", "password": password, "ssh_command": f"ssh {username}@{base_url_no_scheme} -p {port}"})

@app.route('/auth')
def auth():
    base_url = url_for('auth_callback', _external=True)
    encoded_data = base64.b64encode(base_url.encode()).decode()
    return redirect("https://kokoauth.kokodev.cc/auth?name=TemporarySSHSessionManager&callback=" + encoded_data)

@app.route('/auth/callback')
def auth_callback():
    # Print incoming request arguments for debugging
    print(f"Received args: {request.args}")  # Log incoming arguments
    code = request.args.get('session')
    
    if code:
        print(f"Session code found: {code}")  # Print the session code
        # Process the code and retrieve the user's username
        response = requests.get(f'https://kokoauth.kokodev.cc/api/v1/get-user-info?session={code}')
        
        if response.status_code == 200:
            user_info = response.json()
            username = user_info.get('email')
            print(f"Username retrieved: {username}")  # Print the username
            
            # Store the username in the database
            if username:
                conn = sqlite3.connect('containers.db')
                c = conn.cursor()
                c.execute("SELECT username FROM users WHERE username=?", (username,))
                
                if c.fetchone() is None:
                    c.execute("INSERT INTO users (username) VALUES (?)", (username,))
                
                c.execute("INSERT INTO session (user, session) VALUES (?, ?)", (username, code))
                conn.commit()
                conn.close()
                
                session['username'] = username
                session['session'] = code
                
                return redirect(url_for('home'))
    
    print("No valid session code found; redirecting to auth.")  # Print warning message
    return redirect(url_for('auth'))


@app.route('/logout')
def logout():
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    c.execute("DELETE FROM session WHERE session=?", (session['session'],))
    conn.commit()
    conn.close()
    session.pop('username', None)
    session.pop('session', None)
    return redirect(url_for('home'))

create_database()
app.run(host='0.0.0.0', port=2271, debug=True)
