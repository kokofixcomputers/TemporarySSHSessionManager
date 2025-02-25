import configurationlib
import secrets
import string


def init():
    config = configurationlib.Instance(
        "config.json", format=configurationlib.Format.JSON
    )
    detect_already_configured = configurationlib.Instance(
        "DELETE_THIS_FILE_TO_RESET_CONFIGURATION.py",
        format=configurationlib.Format.PYTHON,
    )
    try:
        detect_already_configured.get()["CONFIGURED"]
        exit(0)
    except BaseException:
        pass
    detect_already_configured.save()["CONFIGURED"] = True
    detect_already_configured.save()["INFORMATION"] = (
        "This file does not contain configuration. Configuration is stored in config.json. It is safe to delete this file to restore default configruation."
    )
    detect_already_configured.save()

    # Define the set of allowed characters
    chars = string.ascii_letters + string.digits + "!@#$%"

    # Generate a random 6-character string
    app_string = "".join(secrets.choice(chars) for _ in range(9))

    allow_access = ["put user kokoauth account email addresses here"]

    config.save()["REQUIRE_AUTH"] = True
    config.save()["ALLOW_ALL_VALID_KOKOAUTH_ACCOUNTS_TO_CREATE_SESSIONS"] = True
    config.save()["ALLOWED_KOKOAUTH_ACCOUNTS_EMAIL"] = allow_access
    config.save()["ADMIN_KOKOAUTH_ACCOUNT_EMAIL_ADDRESS"] = [
        "put admin kokoauth account email addresses here"
    ]
    config.save()["ALLOW_ADMIN_TO_ACCESS_USER_CONTAINERS"] = True
    config.save()["APP_SECRET"] = str(app_string)
    config.save()["DEBUG_MODE"] = False
    config.save()["WEB_DASHBORD_PORT"] = 2271
    config.save()["STARTING_PORT_FOR_CONTAINERS"] = 2280
    config.save()["ENDING_PORT_FOR_CONTAINERS"] = 2599
    config.save()["AGENT_PORT"] = 8765
    config.save()["INSTALL_AGENT_INTO_CONTAINERS_FOR_MANAGEMENT"] = True
    config.save()["MAX_CONTAINERS_PER_USER"] = 10
    config.save()
