import configurationlib
import secrets
import string

def init():
    config = configurationlib.Instance("config.json", format=configurationlib.Format.JSON)
    detect_already_configured = configurationlib.Instance("DELETE_THIS_FILE_TO_RESET_CONFIGURATION.py", format=configurationlib.Format.PYTHON)
    try:
        CONFIGURED = detect_already_configured.get()['CONFIGURED']
        exit(0)
    except:
        pass
    detect_already_configured.save()['CONFIGURED'] = True
    detect_already_configured.save()['INFORMATION'] = "This file does not contain configuration. Configuration is stored in config.json. It is safe to delete this file to restore default configruation."
    detect_already_configured.save()
    
    # Define the set of allowed characters
    chars = string.ascii_letters + string.digits + "!@#$%"

    # Generate a random 6-character string
    app_string = ''.join(secrets.choice(chars) for _ in range(9))
    
    allow_access = ['put user kokoauth account email addresses here']
    
    config.save()['REQUIRE_AUTH'] = True
    config.save()['ALLOW_ALL_VALID_KOKOAUTH_ACCOUNTS_TO_CREATE_SESSIONS'] = True
    config.save()['ALLOWED_KOKOAUTH_ACCOUNTS_EMAIL'] = allow_access
    config.save()['ADMIN_KOKOAUTH_ACCOUNT_EMAIL_ADDRESS'] = ['put admin kokoauth account email addresses here']
    config.save()['ALLOW_ADMIN_TO_ACCESS_USER_CONTAINERS'] = True
    config.save()['APP_SECRET'] = str(app_string)
    config.save()['DEBUG_MODE'] = False
    config.save()