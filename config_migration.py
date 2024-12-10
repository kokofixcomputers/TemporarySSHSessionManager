import configurationlib
config = configurationlib.Instance("config.json", format=configurationlib.Format.JSON)
detect_already_configured = configurationlib.Instance("DELETE_THIS_FILE_TO_RESET_CONFIGURATION.py", format=configurationlib.Format.PYTHON)

try:
    CONFIGURED = detect_already_configured.get()['CONFIGURED']
except:
    print("Configuration not found. No migration is required. Please run the main.py file to configure and add the default configuration.")
    exit(0)
    
if config.get()['PORT']:
    config.save()['WEB_DASHBORD_PORT'] = config.get()['PORT']
    config.save()['PORT'] = None
    config.save()['STARTING_PORT_FOR_CONTAINERS'] = config.get()['WEB_DASHBORD_PORT'] + 10
    config.save()['ENDING_PORT_FOR_CONTAINERS'] = config.get()['WEB_DASHBORD_PORT'] + 610
    config.save()
    
try:
    HAS = config.get()['INSTALL_AGENT_INTO_CONTAINERS_FOR_MANAGEMENT']
except:
    config.save()['INSTALL_AGENT_INTO_MANAGEMENT_CONTAINERS'] = True
    config.save()