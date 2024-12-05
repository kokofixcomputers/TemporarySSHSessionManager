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

def create_container():
    username = generate_username(word_list)
    password = generate_password()
    host_port = generate_random_port()

    environment_vars = {
        "SUDO_ACCESS": "true",
        "PASSWORD_ACCESS": "true",
        "USER_PASSWORD": password,
        "USER_NAME": username,
        "WELCOME_MESSAGE": "Welcome to your temp enviroment. SSH access is enabled with your user password."
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


    print(f"Container {container.name} created and running.")
    print(f"Generated Username: {username}")
    print(f"Generated Password: {password}")
    print(f"Mapped Host Port: {host_port} to Container Port: 2222")
    return container.name, username, password, host_port