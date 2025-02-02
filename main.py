from flask import Flask, jsonify, render_template, request, redirect, session, url_for, Response
import handler
import requests
import sqlite3
import base64
import server
from jinja2 import Environment, FileSystemLoader # Don't need to put into requirements file because it's required by flask already.
from urllib.parse import urlparse
from waitress import serve
import configurationlib
import time
import configuration_manager
import secrets
import printedcolors
import network_setup
import random

colors = printedcolors.Color

def debug_print(message, color=""):
    if color == "":
        reset = ""
    else:
        reset = colors.reset
    if DEBUG:
        print(color + message + reset)
        
print(colors.fg.cyan + "Temporary SSH Session Manager" + colors.reset)
print("")

print(colors.fg.lightblue + "Testing Docker Connection..." + colors.reset)
if not handler.test_docker_connection():
    print(colors.fg.red + "Docker is not running. Please start Docker and try again." + colors.reset)
    exit(1) # Non-zero exit code indicates an error
else:
    print(colors.fg.green + "Docker is running. Proceeding with the application." + colors.reset)

network_setup.setup_network()

config = configurationlib.Instance("config.json", format=configurationlib.Format.JSON)
detect_already_configured = configurationlib.Instance("DELETE_THIS_FILE_TO_RESET_CONFIGURATION.py", format=configurationlib.Format.PYTHON)

try:
    CONFIGURED = detect_already_configured.get()['CONFIGURED']
except:
    print(colors.fg.red + "Configuration file not found. Creating one..." + colors.reset)
    print(colors.fg.green + "Using default configuration." + colors.reset)
    configuration_manager.init()
    CONFIGURED = False
    print(colors.fg.green + "Configuration file created. Please restart the application." + colors.reset)
    exit(0)
    
# Define Jinja2 Env
env = Environment(loader=FileSystemLoader('templates'))

try:    
    DEBUG = config.get()['DEBUG_MODE']
except:
    print(colors.fg.red + "Error: Configuration missing. Things may go very wrong." + colors.reset)
if DEBUG:
    print(colors.fg.yellow + "Debug mode enabled." + colors.reset)

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

def sync_database_with_docker_containers_state():
    debug_print("Syncing database with Docker containers state...", colors.fg.green)
    conn = sqlite3.connect('containers.db')
    cursor = conn.cursor()
    # Iterate over all containers and check if they are: (running, stopped, exists).
    containers = cursor.execute("SELECT * FROM containers")
    # Check if container exist.
    for container in containers:
        # Check if container exists
        exist = handler.check_container_existence(container[1])
        if exist:
            handler.check_container_existence(container[1])
        else:
            # Container does not exist
            debug_print(f"Container {container[1]} does not exist. Deleting...", colors.fg.red)
            cursor.execute("DELETE FROM containers WHERE name=?", (container[1],))
            conn.commit()
            continue
    # Refresh containers
    containers = cursor.execute("SELECT * FROM containers")
    # Check container's state (running, stopped).
    for container in containers:
        state = handler.fetch_container_state(container[1])
        bool_state = True if state == "running" else False
        if container[6] != bool_state:
            debug_print(f"Container {container[1]} state changed from {container[6]} to {bool_state}.", colors.fg.green)
            if state == True:
                cursor.execute("UPDATE containers SET active = ? WHERE name = ?", (True, container[1]))
                conn.commit()
            else:
                cursor.execute("UPDATE containers SET active = ? WHERE name = ?", (False, container[1]))
                conn.commit()
                
sync_database_with_docker_containers_state()

def create_database():
    debug_print("Creating database if not exists...", colors.fg.green)
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    #c.execute("ALTER TABLE containers ADD COLUMN active INTEGER;") # TODO: add pre-script and post-script to run before and after running this
    c.execute('''CREATE TABLE IF NOT EXISTS containers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  username TEXT,
                  password TEXT,
                  user TEXT,
                  port INTEGER,
                  active INTEGER,
                  dev_port INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS session
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               user TEXT,
               session TEXT)
               ''')
    c.execute('''CREATE TABLE IF NOT EXISTS api_key (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT,
                user TEXT)''')
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
    
@app.route('/apikey/generate', methods=['POST'])
def generate_api_key():
    if authenticated(session):
        conn = sqlite3.connect('containers.db')
        c = conn.cursor()
        ## Make sure the user has not already generated an API key
        #c.execute('SELECT * FROM api_key WHERE user=?', (session['username'],))
        #if c.fetchone() is not None:
        #    # Get the user's API Key
        #    api = c.execute('SELECT api_key FROM api_key WHERE user=?', (session['username'],)).fetchone()[0]
        #    return f"<p>{api}</p>"
        #else:
        # Generate a new API key
        new_api_key = "stm_" + str(secrets.token_hex(32))
        c.execute('INSERT INTO api_key (api_key, user) VALUES (?, ?)', (new_api_key, session['username']))
        conn.commit()
        conn.close()
        return "<p>" + str(new_api_key) + "</p>"
    else:
        return "<p>You are not authorized to access this page.</p>"
    
@app.route('/apikey/delete', methods=['POST'])
def delete_api_key():
    if authenticated(session):
        api_key = request.json.get('api_key')
        if api_key:
            conn = sqlite3.connect('containers.db')
            c = conn.cursor()
            c.execute('DELETE FROM api_key WHERE api_key=?', (api_key,))
            conn.commit()
            conn.close()
            return "API key deleted successfully."
        else:
            return "API key not provided."
    
@app.route('/apikey/get')
def get_api_key():
    if authenticated(session):
        conn = sqlite3.connect('containers.db')
        c = conn.cursor()
        # Get all of the user's API Keys
        c.execute('SELECT api_key FROM api_key WHERE user=?', (session['username'],))
        api_keys = [row[0] for row in c.fetchall()]
        conn.close()
        return jsonify(api_keys)
    else:
        return "You are not authorized to access this page."
    
@app.route('/apikey/dashboard')
def api_key_dashboard():
    if authenticated(session):
        return render_template('api_key.html', username=session['username'])
    else:
        return redirect(url_for('auth'))
    
def validate_api_key(key):
    # Check if the API key is valid
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    c.execute('SELECT * FROM api_key WHERE api_key=?', (key,))
    result = c.fetchone()
    conn.close()
    if result is None:
        return False
    else:
        return True
    
@app.route('/api/get_user_containers', methods=['GET'])
def get_user_containers_api():
    # Get the API key from the request headers
    api_key = request.headers.get('Authorization')
    
    # Validate the API key
    if not validate_api_key(api_key):
        return jsonify({"error": "Invalid API key"}), 401
    
    # Assuming request.url_root is defined
    url = request.url_root
    parsed_url = urlparse(url)

    # Constructing the base URL without scheme and port
    base_url_no_scheme = parsed_url.hostname + parsed_url.path.rstrip('/')
    
    # Get the username from the API key
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    
    c.execute('SELECT user FROM api_key WHERE api_key=?', (api_key,))
    result = c.fetchone()
    if result is None:
        return jsonify({"error": "Invalid API key"}), 401
    username = result[0]
    # Get the user's containers
    c.execute('SELECT * FROM containers WHERE user=?', (username,))
    containers = c.fetchall()
    conn.close()
    container_list = []
    for container in containers:
        container_details = {
            "name": container[1],
            "username": container[2],
            "password": container[3],
            "port": container[5],
            "exposed_port": container[6],
            "hostname": base_url_no_scheme,
            "active": container[7]
        }
        container_list.append(container_details)
    return jsonify(container_list)
    
    
@app.route('/install/alpine')
def install_alpine():
    #if not str(request.args.get('token')) == "stm_NDbBshvFzKZLlOuhY1OPcS": # TODO: add non-static token
    #    return jsonify({"error": "Unauthorized"}), 401
    url = request.url_root
    template = env.get_template('install_script.sh.j2')
    rendered_script = template.render(url=url) # Render the script.
    return Response(rendered_script, mimetype='text/plain')

@app.route('/install/ubuntu')
def install_ubuntu():
    #if not str(request.args.get('token')) == "stm_NDbBshvFzKZLlOuhY1OPcS": # TODO: add non-static token
    #    return jsonify({"error": "Unauthorized"}), 401
    url = request.url_root
    template = env.get_template('install_script_ubuntu.sh.j2')
    rendered_script = template.render(url=url) # Render the script.
    return Response(rendered_script, mimetype='text/plain')

def get_random_port(starting_port=int(config.get()['STARTING_PORT_FOR_CONTAINERS']), ending_port=int(config.get()['ENDING_PORT_FOR_CONTAINERS'])):
    # Connect to the SQLite database
    conn = sqlite3.connect('containers.db')
    cursor = conn.cursor()
    
    # Fetch all existing ports from the 'containers' table
    cursor.execute("SELECT port FROM containers")
    existing_ports = {row[0] for row in cursor.fetchall()}
    
    # Close the database connection
    conn.close()

    while True:
        # Generate a random port number
        random_port = random.randint(starting_port, ending_port)
        
        # Check if the generated port is already in use
        if random_port not in existing_ports:
            return random_port
        
def get_random_outsider_port(starting_port=int(config.get()['STARTING_PORT_FOR_CONTAINERS']) + 1, ending_port=int(config.get()['ENDING_PORT_FOR_CONTAINERS']) + 319):
    # Connect to the SQLite database
    conn = sqlite3.connect('containers.db')
    cursor = conn.cursor()
    
    # Fetch all existing ports from the 'containers' table
    cursor.execute("SELECT dev_port FROM containers")
    existing_ports = {row[0] for row in cursor.fetchall()}
    
    # Close the database connection
    conn.close()

    while True:
        # Generate a random port number
        random_port = random.randint(starting_port, ending_port)
        
        # Check if the generated port is already in use
        if random_port not in existing_ports:
            return random_port

@app.route('/create_container', methods=['POST'])
def create_container_route():
    time.sleep(5)
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    if not is_authorized(session['username']):
        return jsonify({"error": "You are not authorized to create containers."}), 403
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    # Assuming request.url_root is defined
    url = request.url_root
    parsed_url = urlparse(url)
    data = request.get_json()  # Use this if sending JSON
    distro = data.get('distro')  # Access the 'distro' key
    
    c.execute("SELECT user FROM containers WHERE user=?", (session['username'],))

    # Fetch all results
    rows = c.fetchall()

    # Count the number of rows
    row_count = len(rows)
    if config.get()['MAX_CONTAINERS_PER_USER'] == 0:
        pass # No limit
    elif row_count >= config.get()['MAX_CONTAINERS_PER_USER']:
        return jsonify({"error": "You have reached the maximum number of containers per user.", "code": 1002}), 403
    
    # Constructing the base URL without scheme and port
    base_url_no_scheme = parsed_url.hostname + parsed_url.path.rstrip('/')
    name, username, password, port, exposed_port = handler.create_container(url + f'''/install/{distro}''', port=get_random_port(), outsider_port=get_random_outsider_port(), distro=distro) # TODO: Add non-static token.
    if name is not None:
        c.execute("INSERT INTO containers (name, username, password, user, port, dev_port, active) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, username, password, session['username'], port, exposed_port, True))
        conn.commit()
    conn.close()
    return jsonify({"name": name, "username": username, "hostname": base_url_no_scheme, "port": f"{port}", "exposed_port": exposed_port, "password": password, "ssh_command": f"ssh {username}@{base_url_no_scheme} -p {port}"})

@app.route('/container/restart', methods=['POST'])
def restart_container():
    user = session.get('username')
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    if not is_authorized(session['username']):
        return jsonify({"error": "You are not authorized to restart containers."}), 403
    
    # Checking if the user has access to the container using the username
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    perms_check = c.execute("SELECT user FROM containers WHERE name=? AND user=?", (request.args.get('id'),user)).fetchone()
    if perms_check is None:
        return jsonify({"error": "You are not authorized to restart this container or this container never existed."}), 403
    
    
    container_name = request.args.get('id')
    if container_name:
        c.execute("UPDATE containers SET active = ? WHERE name = ?", (False, request.args.get('id'))).fetchone()
        handler.restart_container(container_name)
        c.execute("UPDATE containers SET active = ? WHERE name = ?", (True, request.args.get('id'))).fetchone()
        conn.commit()
        conn.close()
        return jsonify({"message": "Container restarted."})
    else:
        conn.close()
        return jsonify({"error": "No container ID provided."}), 400
    
@app.route('/container/stop', methods=['POST'])
def stop_container():
    user = session.get('username')
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    if not is_authorized(session['username']):
        return jsonify({"error": "You are not authorized to stop containers."}), 403

    # Checking if the user has access to the container using the username
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    perms_check = c.execute("SELECT user FROM containers WHERE name=? AND user=?", (request.args.get('id'),user)).fetchone()
    if perms_check is None:
        return jsonify({"error": "You are not authorized to stop this container or this container never existed."}), 403

    container_name = request.args.get('id')
    if container_name:
        c.execute("UPDATE containers SET active = ? WHERE name = ?", (False, request.args.get('id'))).fetchone()
        handler.stop_container(container_name)
        conn.commit()
        conn.close()
    return jsonify({"message": "Container stopped."})

@app.route('/container/start', methods=['POST'])
def start_container():
    user = session.get('username')
    if not authenticated(session):
        return jsonify({"error": "You are not logged in."}), 401
    if not is_authorized(session['username']):
        return jsonify({"error": "You are not authorized to start containers."}), 403
    # Checking if the user has access to the container using the username
    conn = sqlite3.connect('containers.db')
    c = conn.cursor()
    perms_check = c.execute("SELECT user FROM containers WHERE name=? AND user=?", (request.args.get('id'),user)).fetchone()
    if perms_check is None:
        return jsonify({"error": "You are not authorized to start this container or this container never existed."}), 403
    container_name = request.args.get('id')
    if container_name:
        c.execute("UPDATE containers SET active = ? WHERE name = ?", (True, request.args.get('id'))).fetchone()
        handler.start_container(container_name)
        conn.commit()
        conn.close()
    return jsonify({"message": "Container started."})

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
    return jsonify({"message": "OK", "code": 200, "port": config.get()['AGENT_PORT'], "scheme": "ws"})

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
import time
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
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    command = await websocket.recv()
                    if command == '{"message": "request_report_status"}':
                        await report_status(websocket)
                    else:
                        print(f"{command}")
        except:
                    print("Agent disconnected. Reconnecting in 20 seconds...")
                    time.sleep(20)

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
            c.execute("SELECT name, username, password, port, dev_port, active FROM containers")
        else:
            c.execute("SELECT name, username, password, port, dev_port, active FROM containers WHERE user=?", (user,))
        containers = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        debug_print(f"Error while fetching user containers: {e}", colors.fg.red)
        return jsonify([]), 500

    if containers:
        return jsonify([{"name": container[0], "username": container[1], "password": container[2], "port": container[3], "exposed_port": container[4], "hostname": base_url_no_scheme, "active": container[5]} for container in containers])
    else:
        return jsonify([]), 500
    
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
    c.execute("SELECT name, username, password, port, dev_port, active FROM containers WHERE name=? AND user=?",(id, session['username']))
    container = c.fetchone()
    conn.close()
    if container:
        return jsonify({"name": container[0], "username": container[1], "exposed_port": container[4],"hostname": base_url_no_scheme, "password": container[2], "ssh_command": f"ssh {container[1]}@{base_url_no_scheme} -p {container[3]}", "port": container[3], "active": container[5]})
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
    time.sleep(2)
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
