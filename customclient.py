import keyring
import requests
from InquirerPy import prompt
from InquirerPy.base.control import Choice
import os
import printedcolors
import argparse

colors = printedcolors.Color
fg = printedcolors.Color.fg

api_key = keyring.get_password("stmclient", "api_key")
host = keyring.get_password("stmclient", "host")
if api_key is None:
    api_key = input("Enter API key: ")
    host = input("Enter base URL for your instance: ")
    keyring.set_password("stmclient", "api_key", api_key)
    keyring.set_password("stmclient", "host", host)

parser = argparse.ArgumentParser(description="Process some options.", add_help=False)

parser.add_argument('--credential-reset', action='store_true', help='Reset credentials')
parser.add_argument('container', nargs='?', default=None, help='The optional token argument')

args = parser.parse_args()
if getattr(args, 'credential_reset'):
    keyring.delete_password("stmclient", "api_key")
    keyring.delete_password("stmclient", "host")
    api_key = input("Enter API key: ")
    host = input("Enter base URL for your instance: ")
    keyring.set_password("stmclient", "api_key", api_key)
    keyring.set_password("stmclient", "host", host)
    print("Credentials reset successfully.")
    exit(0)
    
containers = requests.get(host + "/api/get_user_containers", headers={"Authorization": api_key})
if containers.status_code == 404:
    print("A Incorrect API URL Has been provided. Please check your url. Make sure it includes https:// or http:// and the port number.")
    exit(1)
containers = containers.json()

container_connect = args.container

if container_connect:
    container_info = next((container for container in containers if container["name"] == container_connect), None)
    if not container_info:
        print(f"{fg.red}Container '{container_connect}' not found.{colors.reset}")
        exit(1)
    print("Connecting to container: ", container_info["name"])
    os.system(f"ssh -o LogLevel=ERROR -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {container_info['username']}@{container_info['hostname']} -p {container_info['port']}")
    exit(0)

choices = [Choice(name=f"{container['name']} ({container['username']}@{container['hostname']})", value=container) for container in containers if container['active'] == 1]
try:
    selected_container = prompt([
        {
            "type": "fuzzy",
            "name": "selected_container",
            "message": "Select a container:",
            "choices": choices
        }
    ])["selected_container"]
except KeyboardInterrupt:
    print(f"{fg.red}Operation cancelled by user.{colors.reset}")
    exit(0)


# Check if the container is running
container_name = selected_container["name"]

container_info = next((container for container in containers if container["name"] == container_name), None)

print("Connecting to container: ", container_info["name"])

os.system(f"ssh -o LogLevel=ERROR -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {container_info['username']}@{container_info['hostname']} -p {container_info['port']}")