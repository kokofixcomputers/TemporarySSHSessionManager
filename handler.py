import docker
import random
import string
import time

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
    "happy", "bright", "bold", "chill", "zesty"
]  # Expanded list of words for username generation

def create_container(web_dashboard_host, start_port=2280, end_port=2599):
    username = generate_username(word_list)
    password = generate_password()
    host_port = generate_random_port(start_port, end_port)

    environment_vars = {
        "SUDO_ACCESS": "true",
        "PASSWORD_ACCESS": "true",
        "USER_PASSWORD": password,
        "USER_NAME": username,
        "INSTALL_SCRIPT_URL": web_dashboard_host,
        "WELCOME_MESSAGE": "\033[36mWelcome to your temporary environment.\033[0m\nTemporary SSH Server made by kokofixcomputers\nGitHub: https://github.com/kokofixcomputers/TemporarySSHSessionManager.git \nLicensed Under the Mit License.\n\n\033[32mTo access sudo, run a command with sudo and enter the password shown in the dashboard when asked for password.\033[0m\n\n\n\033[1mPLEASE REFRAIN FROM USING CONFIDENTIAL INFORMATION IN THIS ENVIROMENT.\033[0m\nPlease note: admins can see and connect to this container.\n\033[33mPlease also refrain from using this environment for anything illegal or unethical.\n\033[0m\n\n\033[1mWARNING: By using this environment you agree not to use this container for anything illegal or unehtical and have read the above notes.\n\n\033[0mHave fun!",
    }

    # Create and run the container
    try:
        client = docker.from_env()
        time.sleep(1)
        container = client.containers.run(
            "kokofixcomputers/docker-openssh-server-fork:latest",
            detach=True,
            environment=environment_vars,
            ports={'2222/tcp': host_port}  # Map container port 2222 to a random host port
        )
    except:
        return None, None, None, None
    time.sleep(5)

    return container.name, username, password, host_port

def delete_container(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        container.remove(force=True)
    except:
        return None
    return True
