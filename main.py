from flask import Flask, jsonify, render_template, request, redirect, session, url_for, Response
import handler
import requests
import sqlite3
import base64
import server
from urllib.parse import urlparse
from waitress import serve
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
    

try:    
    DEBUG = config.get()['DEBUG_MODE']
except:
    print(colors.fg.red + "Error: Configuration missing. Things may go very wrong." + colors.reset)
if DEBUG:
    print(colors.fg.yellow + "Debug mode enabled." + colors.reset)
    
def debug_print(message, color=""):
    if color == "":
        reset = ""
    else:
        reset = colors.reset
    if DEBUG:
        print(color + message + reset)

debug_print("Loading configuration...", colors.fg.green)

try:
    REQUIRE_AUTH = config.get()["REQUIRE_AUTH"]
except:
    debug_print("Error: Configuration missing. Things may go very wrong.", colors.fg.red)
    REQUIRE_AUTH = True # To avoid errors
    
debug_print("Configuration loaded.", colors.fg.green)


if config.get()['INSTALL_AGENT_INTO_CONTAINERS_FOR_MANAGEMENT']:
    debug_print("Initializing websocker server...", colors.fg.green)
    server.start()
    debug_print("Websocket server initialized.", colors.fg.green)
    
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
        return render_template('home.html', username=session['username'], authorized=is_authorized(session['username']), admin=is_admin(session['username']))
    else:
        return redirect(url_for('auth'))
    
@app.route('/install')
def install():
    url = request.url_root
    script = f'''#!/bin/sh

BASH_PROFILE="/config/.bash_profile"
BASH_RC="/config/.bashrc"

# Update the package index
apk update

# Install Python 3, pip, and curl
apk add --no-cache python3 py3-pip curl

# Verify the installation
python3 --version
pip3 --version
curl --version

# Create the directory for the virtual environment if it doesn't exist
mkdir -p /etc/venv

# Create a virtual environment in /etc/venv
python3 -m venv /etc/venv

# Activate the virtual environment
. /etc/venv/bin/activate

if [ ! -f "$BASH_RC" ]; then
    echo "Creating $BASH_RC and adding 'echo \"hi\"'"
    echo '. /etc/venv/bin/activate' > "$BASH_RC"
    echo 'nohup python3 /etc/agent/agent.py > /dev/tty 2>&1 &' >> "$BASH_RC"
    echo 'echo "hi"' >> "$BASH_RC"
else
    echo "$BASH_RC already exists."
fi

if [ ! -f "$BASH_PROFILE" ]; then
    echo "Creating $BASH_PROFILE and adding sourcing for .bashrc"
    echo 'if [ -f /config/.bashrc ]; then' > "$BASH_PROFILE"
    echo '    . /config/.bashrc' >> "$BASH_PROFILE"
    echo 'fi' >> "$BASH_PROFILE"
else
    echo "$BASH_PROFILE already exists."
fi

# Verify that the virtual environment is activated and pip is available
pip --version
pip install websockets requests psutil

# Create the directory for the agent if it doesn't exist
mkdir -p /etc/agent

curl -o /etc/agent/agent.py {url}/agent/download

echo "Virtual environment 'venv' created and activated at /etc/venv."
echo "Downloaded content from {url}/agent/download to /etc/agent/agent.py."'''
    return Response(script, mimetype='text/plain')

@app.route('/create_container', methods=['POST'])
def create_container_route():
    time.sleep(5)
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    if not is_authorized(session['username']):
        return jsonify({"error": "You are not authorized to create containers."}), 403
    # Assuming request.url_root is defined
    url = request.url_root
    parsed_url = urlparse(url)

    # Constructing the base URL without scheme and port
    base_url_no_scheme = parsed_url.hostname + parsed_url.path.rstrip('/')
    name, username, password, port = handler.create_container(url + "/install", start_port=int(config.get()['STARTING_PORT_FOR_CONTAINERS']), end_port=int(config.get()['ENDING_PORT_FOR_CONTAINERS']))
    if name is not None:
        conn = sqlite3.connect('containers.db')
        c = conn.cursor()
        c.execute("INSERT INTO containers (name, username, password, user, port) VALUES (?, ?, ?, ?, ?)", (name, username, password, session['username'], port))
        conn.commit()
        conn.close()
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

@app.route('/agent/handshake')
def agent_handshake():
    # TODO: Add port and scheme changing from config
    return jsonify({"message": "OK", "code": 200, "port": 8765, "scheme": "ws"})

@app.route('/agent/download')
def download_agent():
    # Assuming request.url_root is defined
    url = request.url_root
    parsed_url = urlparse(url)

    # Constructing the base URL without scheme and port
    base_url_no_scheme = parsed_url.hostname + parsed_url.path.rstrip('/')

    script = '''import asyncio
import websockets
import requests
import subprocess
import os
import json
import psutil

host = "'''+base_url_no_scheme+'''"
schemed_host = "''' + url +'''"

async def report_status(websocket):
    # Gather system status
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv

    # Create a status message in JSON format
    status_message = {
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv,
    }

    # Send the status to the server as a JSON string
    await websocket.send(json.dumps(status_message))

async def listen_for_commands():
    uri = scheme + "://" + host + ":" + str(port)
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                command = await websocket.recv()
                if command == '{"message": "request_report_status"}':
                    await report_status(websocket)
                else:
                    print(f"{command}")
    except websockets.exceptions.ConnectionClosedError:
                print("Agent disconnected. Reconnecting...")

if __name__ == "__main__":
    response = requests.get(schemed_host + "agent/handshake").json()
    if response['message'] == "OK" and response['code'] == 200:
        # Awesome! Ready to connect.
        port = int(response['port'])
        scheme = response['scheme']
    else:
        print("Error: Agent handshake failed.")
        exit(1)
    asyncio.run(listen_for_commands())'''
    
    return Response(script, mimetype='text/plain')

@app.route('/get_user_containers', methods=['GET'])
def get_user_containers():
    user = session.get('username')
    if not authenticated(session):
        return "UNAUTHENTICATED", 401
    
    url = request.url_root
    parsed_url = urlparse(url)

    # Constructing the base URL without scheme and port
    base_url_no_scheme = parsed_url.hostname + parsed_url.path.rstrip('/')
        
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
        return jsonify([{"name": container[0], "username": container[1], "password": container[2], "port": container[3], "hostname": base_url_no_scheme} for container in containers])
    else:
        return jsonify([])
    
@app.route('/get_connection_details', methods=['GET'])
def get_connection_details():
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    url = request.url_root
    parsed_url = urlparse(url)

    # Constructing the base URL without scheme and port
    base_url_no_scheme = parsed_url.hostname + parsed_url.path.rstrip('/')
    id = request.args.get('id')
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    c.execute("SELECT name, username, password, port FROM containers WHERE name=? AND user=?",(id, session['username']))
    container = c.fetchone()
    conn.close()
    if container:
        return jsonify({"name": container[0], "username": container[1], "hostname": base_url_no_scheme, "password": container[2], "ssh_command": f"ssh {container[1]}@{base_url_no_scheme} -p {container[3]}", "port": container[3]})
    else:
        return jsonify({"error": "Container not found."}), 404


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

@app.route('/admin')
def admin():
    if not authenticated(session):
        return redirect(url_for('auth'))
    if not is_admin(session['username']):
        return redirect(url_for('home'))
    return render_template('admin.html', username=session['username'])

@app.route('/admin/danger/session/clear', methods=['DELETE'])
def clear_sessions():
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    if not is_admin(session['username']):
        return jsonify({"error": "You are not authorized to clear sessions."}), 403
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    c.execute("DELETE FROM session")
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
if DEBUG:
    debug_print("WARNING: DEBUG mode is enabled. Non-Production WSGI server will be used.", colors.fg.yellow)
    app.run(host='0.0.0.0', port=config.get()['WEB_DASHBORD_PORT'], debug=DEBUG)
else:
    print("Dashboard server started on 0.0.0.0:" + str(config.get()['WEB_DASHBORD_PORT']))
    serve(app, host='0.0.0.0', port=config.get()['WEB_DASHBORD_PORT'])
