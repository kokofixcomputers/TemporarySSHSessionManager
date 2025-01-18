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
    "happy", "bright", "bold", "chill", "zesty",
    "fierce", "mellow", "sneaky", "witty", "zany",
    "quirky", "spunky", "cheerful", "daring", "epic",
    "fuzzy", "glowy", "hasty", "jolly", "lively",
    "mighty", "playful", "radiant", "sassy", "tasty",
    "vivid", "wacky", "yummy", "zippy", "bubbly",
    "cuddly", "dreamy", "energetic", "frosty", "giddy",
    "hilarious", "jazzy", "kooky", "luminous", "mirthful"
]  # Expanded list of words for username generation


def create_container(web_dashboard_host, start_port=2280, end_port=2599):
    username = generate_username(word_list)
    password = generate_password()
    host_port = generate_random_port(start_port, end_port)
    outsider_port = generate_random_port(end_port + 1, end_port + 320)

    environment_vars = {
        "SUDO_ACCESS": "true",
        "PASSWORD_ACCESS": "true",
        "USER_PASSWORD": password,
        "USER_NAME": username,
        "INSTALL_SCRIPT_URL": web_dashboard_host,
        "WELCOME_MESSAGE": "\033[36mWelcome to your temporary environment.\033[0m\nTemporary SSH Server made by kokofixcomputers\nGitHub: https://github.com/kokofixcomputers/TemporarySSHSessionManager.git \nLicensed Under the Mit License.\n\n\033[32mTo access sudo, run a command with sudo and enter the password shown in the dashboard when asked for password.\033[0m\n\n\n\033[1mBy Using the Container, You agree to the conditions below. \n1. You will REFRAIN from using anything illegal or unethical.\033[0m\n2. For and under any circumstances, You allow admins to connect and execute commands in your container.\n3. You agree that you allow the security and performance monitoring applications installed automaticlly to run.\n By using this container, You agree to the above notes. Please also refrain from using any confidential information in this enviroment.\n\nPlease Consider leaving a ⭐ Star on our repo!\n\033[0mHave fun!",
    }

    # Create and run the container
    try:
        client = docker.from_env()
        time.sleep(1)
        container = client.containers.run(
            "kokofixcomputers/docker-openssh-server-fork:latest",
            detach=True, # REQUIRED for running in the background
            environment=environment_vars,
            network="stm",
            hostname=f"{username}@stm",
            ports={'2222/tcp': host_port, '80': outsider_port}  # Add ports mapping
        )
    except:
        return None, None, None, None, None
    time.sleep(5)

    return container.name, username, password, host_port, outsider_port

def restart_container(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        container.restart()
    except:
        return None
    return True

def delete_container(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        container.remove(force=True)
    except:
        return None
    return True
