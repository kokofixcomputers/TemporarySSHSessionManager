def get_image(distro):
    images = {"ubuntu": "kokofixcomputers/docker-openssh-server-fork-ubuntu:latest", "alpine": "kokofixcomputers/docker-openssh-server-fork:latest"}
    return images.get(distro, None)

def validate_distro(distro):
    return distro in ["ubuntu", "alpine"]