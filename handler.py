# Handler.py
# For handling docker operation.

import docker
import random
import string
import time
import paramiko
import distro_handler
import logging
paramiko_logger = logging.getLogger("paramiko.transport")
paramiko_logger.addHandler(logging.NullHandler())


# Function to generate a random username from a list of words
def generate_username(word_list, length=2):
    return '_'.join(random.choices(word_list, k=length))

# Function to generate a random password with letters and numbers
def generate_password(length=12):
    characters = string.ascii_letters + string.digits  # Include both letters and digits
    return ''.join(random.choices(characters, k=length))

# Function to generate a random port number in the specified range
def generate_random_port(start=2280, end=2599):
    return random.randint(start, end)

# Define environment variables
word_list = [
    "demo", "awesome", "crazy", "rod", "cool",
    "funny", "smart", "quick", "jumpy", "silly",
    "happy", "bright", "bold", "chill", "zesty",
    "fierce", "mellow", "sneaky", "witty", "zany",
    "quirky", "spunky", "cheerful", "daring", "epic",
    "fuzzy", "glowy", "hasty", "jolly", "lively",
    "mighty", "playful", "radiant", "sassy", "tasty",
    "vivid", "wacky", "yummy", "zippy", "bubbly",
    "cuddly", "dreamy", "energetic", "frosty", "giddy",
    "hilarious", "jazzy", "kooky", "luminous", "mirthful"
]  # Expanded list of words for username generation

def is_container_running(container_name: str):
    """Verify the status of a container by its name.

    :param container_name: The name of the container.
    :return: True if running, False if stopped, None if not found.
    """
    RUNNING = "running"
    
    # Connect to Docker
    docker_client = docker.from_env()

    try:
        # Get the container by name
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
        return None

    # Check the status of the container
    container_state = container.attrs["State"]
    return container_state["Status"] == RUNNING

def check_container_existence(container_name):
    """Check if a container exists."""
    try:
        client = docker.from_env()
        client.containers.get(container_name)
    except docker.errors.NotFound:
        return False
    return True

def fetch_container_state(container_name):
    """Fetch the state of the container. stopped or running Returns True if running, False if stopped, None if not found."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container_state = container.attrs["State"]
        return container_state["Status"] == "running"
    except docker.errors.NotFound:
        return None
    
def test_docker_connection():
    try:
        client = docker.from_env()
        client.containers.list()
        return True
    except:
        return False
    
def check_ssh_connection(username, hostname, port=22, password=None):
    """
    Check if an SSH connection can be established to a server.

    Args:
        username (str): The username for SSH authentication.
        hostname (str): The hostname or IP address of the server.
        port (int): The port number for SSH (default is 22).
        password (str): The password for SSH authentication.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        
        # Automatically add the server's host key (this is not recommended for production)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the server
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # If successful, return True
        return True
        
    except paramiko.AuthenticationException:
        return False
    except paramiko.SSHException as e:
        return False
    except:
        return False
    finally:
        # Close the connection if it was established
        ssh.close()

def create_container(web_dashboard_host, port, outsider_port, distro="alpine"):
    username = generate_username(word_list)
    password = generate_password()

    environment_vars = {
        "SUDO_ACCESS": "true",
        "PASSWORD_ACCESS": "true",
        "USER_PASSWORD": password,
        "USER_NAME": username,
        "INSTALL_SCRIPT_URL": web_dashboard_host,
        "WELCOME_MESSAGE": "\033[36mWelcome to your temporary environment.\033[0m\nTemporary SSH Server made by kokofixcomputers\nGitHub: https://github.com/kokofixcomputers/TemporarySSHSessionManager.git \nLicensed Under the Mit License.\n\n\033[32mTo access sudo, run a command with sudo and enter the password shown in the dashboard when asked for password.\033[0m\n\n\n\033[1mBy Using the Container, You agree to the conditions below. \n1. You will REFRAIN from using anything illegal or unethical.\033[0m\n2. For and under any circumstances, You allow admins to connect and execute commands in your container.\n3. You agree that you allow the security and performance monitoring applications installed automaticlly to run.\n By using this container, You agree to the above notes. Please also refrain from using any confidential information in this enviroment.\n\nPlease Consider leaving a ⭐ Star on our repo!\n\033[0mHave fun!",
    }
    
    # Find image of distro
    image = distro_handler.get_image(distro)

    # Create and run the container
    try:
        client = docker.from_env()
        time.sleep(1)
        container = client.containers.run(
            image,
            detach=True, # REQUIRED for running in the background
            environment=environment_vars,
            network="stm",
            #user=1000,
            mem_limit="612m",
            hostname=f"{username}@stm",
            ports={'2222/tcp': port, '80': outsider_port},  # Add ports mapping
            cpu_count=1
        )
    except:
        return None, None, None, None, None
        
    restart_container(container.name)
    can_connect = False
    while not can_connect:
        can_connect = check_ssh_connection(username=username, password=password, hostname="localhost", port=port)
        time.sleep(2)

    return container.name, username, password, port, outsider_port

def restart_container(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        container.restart()
        time.sleep(1)
    except docker.errors.NotFound:
        return True # No such container. May have been removed already. Return True to update database.
    except:
        return None
    return True

def stop_container(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        container.stop()
    except docker.errors.NotFound:
        return True # No such container. May have been removed already. Return True to update database.
    except:
        return None
    return True

def start_container(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        container.start()
        time.sleep(1)
    except docker.errors.NotFound:
        return True # No such container. May have been removed already. Return True to update database.
    except:
        return None
    return True

def delete_container(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        container.remove(force=True)
    except docker.errors.NotFound:
        return True # No such container. May have been removed already. Return True to update database.
    except:
        return None
    return True
