
from datafs.config.parser import ConfigFile

def get_api(profile=None):
    config = ConfigFile()
    config.read_config()

    if profile is None:
        profile = config.config['default-profile']

    api = config.generate_api_from_config(profile=profile)
    
    config.attach_manager_from_config(api, profile=profile)
    config.attach_services_from_config(api, profile=profile)
    config.attach_cache_from_config(api, profile=profile)

    return api