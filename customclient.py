import keyring
import requests
from InquirerPy import prompt
from InquirerPy.base.control import Choice
import os


api_key = keyring.get_password("stmclient", "api_key")
host = keyring.get_password("stmclient", "host")
if api_key is None:
    api_key = input("Enter API key: ")
    host = input("Enter base URL for your instance: ")
    keyring.set_password("stmclient", "api_key", api_key)
    keyring.set_password("stmclient", "host", host)
containers = requests.get(host + "/api/get_user_containers", headers={"Authorization": api_key}).json()

# Use InquirerPy to prompt the user to select a container
#[
#  {
#    "active": 1,
#    "exposed_port": 2612,
#    "hostname": "hosting.kokodev.cc",
#    "name": "naughty_williamson",
#    "password": "mid4Xqwn1bZc",
#    "port": 2491,
#    "username": "crazy_awesome"
#  }
#]
choices = [Choice(name=f"{container['name']} ({container['username']}@{container['hostname']})", value=container) for container in containers if container['active'] == 1]
selected_container = prompt([
    {
        "type": "list",
        "name": "selected_container",
        "message": "Select a container:",
        "choices": choices
    }
])["selected_container"]


# Check if the container is running
container_name = selected_container["name"]

container_info = next((container for container in containers if container["name"] == container_name), None)

print("Connecting to container: ", container_info["name"])

os.system(f"ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {container_info['username']}@{container_info['hostname']} -p {container_info['port']}")