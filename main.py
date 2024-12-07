from flask import Flask, jsonify, render_template, request, redirect, session, url_for
import handler
import requests
import sqlite3
import base64
import configurationlib
import time
import configuration_manager
import printedcolors

colors = printedcolors.Color

config = configurationlib.Instance("config.json", format=configurationlib.Format.JSON)
detect_already_configured = configurationlib.Instance("DELETE_THIS_FILE_TO_RESET_CONFIGURATION.py", format=configurationlib.Format.PYTHON)

print(colors.fg.cyan + "Temporary SSH Session Manager" + colors.reset)

try:
    CONFIGURED = detect_already_configured.get()['CONFIGURED']
except:
    print(colors.fg.red + "Configuration file not found. Creating one..." + colors.reset)
    print(colors.fg.green + "Using default configuration." + colors.reset)
    configuration_manager.init()
    CONFIGURED = False
    print(colors.fg.green + "Configuration file created. Please restart the application." + colors.reset)
    exit(0)
    
DEBUG = config.get()['DEBUG_MODE']
if DEBUG:
    print(colors.fg.yellow + "Debug mode enabled." + colors.reset)

try:
    REQUIRE_AUTH = config.get()["REQUIRE_AUTH"]
except:
    REQUIRE_AUTH = True
    
def is_authorized(email):
    if config.get()['ALLOW_ALL_VALID_KOKOAUTH_ACCOUNTS_TO_CREATE_SESSIONS']:
        return True
    ALLOWED_EMAILS = config.get()["ALLOWED_KOKOAUTH_ACCOUNTS_EMAIL"]
    if is_admin(email):
        return True
    return email in ALLOWED_EMAILS

def is_admin(email):
    ADMIN_EMAILS = config.get()["ADMIN_KOKOAUTH_ACCOUNT_EMAIL_ADDRESS"]
    return email in ADMIN_EMAILS

def authenticated(session):
    if REQUIRE_AUTH:
        conn = sqlite3.connect('containers.db')
        c = conn.cursor()
        try:
            c.execute("SELECT session FROM session WHERE session=?", (session['session'],))
        except:
            debug_print("Session not found in database.", colors.fg.red)
            conn.close()
            return False
        session = c.fetchone()
        conn.close()
        return session is not None
    return True

def debug_print(message, color=""):
    if color == "":
        reset = ""
    else:
        reset = colors.reset
    if DEBUG:
        print(color + message + reset)

def create_database():
    debug_print("Creating database if not exists...", colors.fg.green)
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
    
app = Flask(__name__)
app.secret_key = config.get()['APP_SECRET']

@app.route('/')
def home():
    if authenticated(session):
        return render_template('home.html', username=session['username'], authorized=is_authorized(session['username']))
    else:
        return redirect(url_for('auth'))

@app.route('/create_container', methods=['POST'])
def create_container_route():
    time.sleep(5)
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    if not is_authorized(session['username']):
        return jsonify({"error": "You are not authorized to create containers."}), 403
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
    code = request.args.get('session')
    if code:
        response = requests.get(f'https://kokoauth.kokodev.cc/api/v1/get-user-info?session={code}')
        if response.status_code == 200:
            user_info = response.json()
            username = user_info.get('email')
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
            else:
                debug_print("Error: Username does not persist from kokoauth.", colors.fg.red)
        else:
            debug_print("Error: Authentication failed.", colors.fg.red)
    else:
        debug_print("Error: Authentication failed.", colors.fg.red)
    return redirect(url_for('auth'))

@app.route('/get_user_containers', methods=['GET'])
def get_user_containers():
    user = session.get('username')
    if not authenticated(session):
        return "UNAUTHENTICATED", 401
        
    try:
        conn = sqlite3.connect('containers.db')
        c = conn.cursor()
        if config.get()['ALLOW_ADMIN_TO_ACCESS_USER_CONTAINERS'] and is_admin(user):
            c.execute("SELECT name, username, password, port FROM containers")
        else:
            c.execute("SELECT name, username, password, port FROM containers WHERE user=?", (user,))
        containers = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        debug_print(f"Error while fetching user containers: {e}", colors.fg.red)
        return jsonify([]), 500

    if containers:
        return jsonify([{"name": container[0], "username": container[1], "password": container[2], "port": container[3]} for container in containers])
    else:
        return jsonify([])


@app.route('/delete_container', methods=['DELETE'])
def delete_containers():
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    debug_print(f"Deleting container with id: {request.args.get('id')}", colors.fg.green)
    id = request.args.get('id')
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    c.execute("DELETE FROM containers WHERE name=? AND user=?",(id, session['username']))
    handler.delete_container(id)
    conn.commit()
    conn.close()
    return jsonify({"success": True})

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
app.run(host='0.0.0.0', port=2271, debug=DEBUG)
