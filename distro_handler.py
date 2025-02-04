import exception_handler as exception
distros = { # Defines all the distros
    "ubuntu": {
        "name": "Ubuntu",
        "id": "ubuntu",
        "default": False,
        "install_file": "install_script_ubuntu.sh.j2",
        "image": "kokofixcomputers/docker-openssh-server-fork-ubuntu:latest"
    },
    "alpine": {
        "name": "Alpine",
        "id": "alpine",
        "default": True, # Default because of small file size
        "install_file": "install_script.sh.j2",
        "image": "kokofixcomputers/docker-openssh-server-fork:latest"
    }
}

def get_install_file(distro):
    try:
        return distros[distro]["install_file"]
    except:
        return None
def validate_distros():
    # Check if there are any distros
    if not distros:
        raise exception.NoDistrosError()

    # Initialize a variable to track the count of defaults
    default_count = 0

    # Iterate through each distro in the dictionary
    for key, value in distros.items():
        # Check for required fields
        if 'name' not in value or not value['name']:
            raise exception.MissingFieldError('name', key)
        if 'id' not in value or not value['id']:
            raise exception.MissingFieldError('id', key)
        if 'image' not in value or not value['image']:
            raise exception.MissingFieldError('image', key)
        
        # Check the default flag
        if value.get('default', False):
            default_count += 1

    # Ensure that only one distro is marked as default
    if default_count != 1:
        raise exception.DefaultDistroError(default_count)

    return True

def get_image(distro):
    distro_info = distros.get(distro)
    if distro_info is not None:
        return distro_info.get("image")
    return None  # Return None if distro is not found

def validate_distro(distro):
    return distro in distros

def get_distro_friendly_name(distro):
    distro_info = distros.get(distro)
    if distro_info is not None:
        return distro_info.get("name")
    return None  # Return None if distro is not found

def get_distro_friendly_name_list():
    return [distro_info.get("name") for distro_info in distros.values()]

def get_distro_list():
    return distros