
from __future__ import absolute_import
from datafs.core.data_api import DataAPI
import yaml
import os
import importlib

try:
    PermissionError
except NameError:
    from datafs.core.data_api import PermissionError

#All of this is handled through command line arguments or via setting it up manually and 
#reading it on subsequent loads of datafs. 

#We have this config object that does all the necessary config logic. It connects the command line with the api
class Config(object):

    #we need some sort of environmnent seed so we know what the parameters are when we start this thing up. 
    CONFIG_FILE_LIST = ['~/.datafs/config.yml', '/env/datafs/config.yml']

    #initialize the config object with the appropriate settings
    #these are global settings internally but can be specified at the user level
    #We see we create a default setting and then give the option for alternative profiles
    def __init__(self):
        self.config = {'default-profile': 'default', 'profiles': {}}


    #now lets actually do the logic that reads the seeds
    #sets the state of config object 
    def read_config(self, additional_fps = []):

        #this generates a path as string to help us locate where the config file is
        #we map a function os.path.expanduser to a set of input directory path strings
        #we can add addtional file paths and concat those to our list of config file
        for fp in map(os.path.expanduser, self.CONFIG_FILE_LIST+additional_fps):
            try:
                #read in the file
                with open(fp, 'r') as y:
                    #read the config.yml file with our yaml lib
                    config = yaml.load(y)

                    #this checks for the the keys of the config to see if you've set up different profiles
                    if not 'profiles' in config:
                        #If you do not have profiles, it creates a profiles and default setting
                        config = {'profiles': {'default': config}}

                    #set default config for Config object with the values in yaml file
                    #if none exist default to current values
                    self.config['default-profile'] = config.get('default-profile', self.config['default-profile'])
                    #Update the config object profile values with the values in the config files
                    self.config['profiles'].update(config['profiles'])

            except IOError:
                pass



    #you should play with yaml to generate and write yaml files on the fly
    def write_config(self, fp=None):

        read_fp = self.CONFIG_FILE_LIST[0]

        if fp is not None:
            read_fp = fp

        #if there is nothing in the path ~/.datafs/config.yml create a dir and write to it. 
        if not os.path.isdir(os.path.dirname(os.path.expanduser(read_fp))):
            os.makedirs(os.path.dirname(os.path.expanduser(read_fp)))

        #in that directory write a yaml file with the spec in self.config
        with open(os.path.expanduser(read_fp), 'w+') as f:
            f.write(yaml.dump(self.config))


    #this is to get the contents from your config
    def get_profile_config(self, profile=None):
        #use the default if none given
        if profile is None:
            profile = self.config['default-profile']

        #if given an unknown profile then create a point to it
        if profile not in self.config['profiles']:
            self.config['profiles'][profile] = {}


        profile_config= self.config['profiles'][profile]

        #this just writes out the additional structure for a config file
        #It returns an empty config but now you have the actually structure
        for kw in ['api', 'manager', 'authorities', 'cache']:
            profile_config[kw] = profile_config.get(kw, {})

        return profile_config


    #this allows us to set up specific parameters in the confg.yml via the command line
    #this is launched from command line via 

    #api = DataAPI(username='Justin', contact='j@rhg.com')
    #config = Config()
    #config.get_default_config_from_api(api)
    #this is basically, read all the values from api and put them in our config.yml
    def get_default_config_from_api(self, api, profile=None):
        profile_config = self.get_profile_config(profile)

        #this creates an empty dict in the [api][userconfig] space
        if not 'user_config' in profile_config['api']:
            profile_config['api']['user_config'] = {}

        #since we pass api as an object, we have access to its attributes
        #read the user_config attrs and set the values in the config file to the values the api user provides
        for kw in api.user_config.keys():
            profile_config['api']['user_config'][kw] = profile_config['api']['user_config'].get(kw, api.user_config[kw])
            
        #set the module and class values of config.yml with api.config values
        #what happens if this is none
        if not 'constructor' in profile_config['api']:
            profile_config['api']['constructor'] = {
                'module': api.__class__.__module__, 
                'class': api.__class__.__name__
            }

        #this sets the config data structure for the manager based on the api values
        #if there are values in the api put them in here
        manager_cfg = {
            'module': api.manager.__class__.__module__,
            'class': api.manager.__class__.__name__,
            'args': [],
            'kwargs': api.manager.config
        }

        #pull those values and write them to the config.yml
        for kw in ['module', 'class', 'args', 'kwargs']:
            profile_config['manager'][kw] = profile_config['manager'].get(kw, manager_cfg[kw])

        #create the data structure for the authorities section
        #dict comprehension
        authorities_cfg = {
            service_name: {
                'module': service.fs.__class__.__module__,
                'class': service.fs.__class__.__name__,
                'args': [],
                'kwargs': {}
            }
        for service_name, service in api._authorities.items()}

        #go through the keys in the authorities config and create an empty structure 
        for service_name in authorities_cfg.keys():
            if service_name not in profile_config['authorities']:
                profile_config['authorities'][service_name] = {}

            for kw in ['module', 'class', 'args', 'kwargs']:
                profile_config['authorities'][service_name][kw] = profile_config['authorities'][service_name].get(kw, authorities_cfg[service_name][kw])

        #if there is an api cache
        #use those values in this datastructure
        if api.cache:
            cache_cfg = {
                'module': api.cache.fs.__class__.__module__,
                'class': api.cache.fs.__class__.__name__,
                'args': [],
                'kwargs': {}
            }

            #load that information from api into config.yml
            for kw in ['module', 'class', 'args', 'kwargs']:
                profile_config['cache'][kw] = profile_config['cache'].get(kw, cache_cfg[kw])


    #this is called by a command line utility operation
    #this 
    def generate_api_from_config(self, profile=None):
        profile_config = self.get_profile_config(profile)

        #if the current state of the config does not have user config settings create a place for them in config.yml
        for kw in ['user_config', 'constructor']:
            if not kw in profile_config['api']:
                profile_config['api'][kw] = {}

        #read the config file and load those settings
        #we get an DataAPI object from this
        try:
            api_mod = importlib.import_module(profile_config['api']['constructor']['module'])
            api_cls = api_mod.__dict__[profile_config['api']['constructor']['class']]

        except KeyError:
            api_cls = DataAPI

        #this is pretty cool 
        api = api_cls(**profile_config['api']['user_config'])

        return api

    #this is a command line utility that loads manager settings when 'datafs is called'
    #this is analagous to calling api.attach_manger(Manager)
    def attach_manager_from_config(self, api, profile=None):
        profile_config = self.get_profile_config(profile)

        if 'manager' in profile_config:

            try:
                manager = self._generate_manager(profile_config['manager'])
                api.attach_manager(manager)

            except (PermissionError, KeyError):
                pass

    #analagous to calling api.attach_authorit(Authority)
    def attach_services_from_config(self, api, profile=None):
        profile_config = self.get_profile_config(profile)

        for service_name, service_config in profile_config.get('authorities', {}).items():

            try:
                service = self._generate_service(service_config)
                api.attach_authority(service_name, service)

            except PermissionError:
                pass

    #analagous to saying attache cache
    def attach_cache_from_config(self, api, profile=None):
        profile_config = self.get_profile_config(profile)

        if 'cache' in profile_config:

            try:
                service = self._generate_service(profile_config['cache'])
                api.attach_cache(service)

            except (PermissionError, KeyError):
                pass


    def _generate_manager(self, manager_config):

        mgr_module = importlib.import_module(manager_config['module'])
        mgr_class = mgr_module.__dict__[manager_config['class']]

        manager = mgr_class(*manager_config.get('args',[]), **manager_config.get('kwargs',{}))

        return manager

    def _generate_service(self, service_config):

        svc_module = importlib.import_module(service_config['module'])
        svc_class = svc_module.__dict__[service_config['class']]
        service = svc_class(*service_config.get('args',[]), **service_config.get('kwargs',{}))

        return service
