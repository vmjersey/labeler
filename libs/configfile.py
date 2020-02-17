import wx
import time
from pathlib import Path
import configparser
import os
import getpass
import io

class ConfigFile():
    ''' 
        A class to deal with a config file
    '''
    def __init__(self,conf_dir=None):

        # Users Home directory
        self.home = str(Path.home())
        
        # Where does the user want their config files stored
        self.conf_dir = self.config_dir(conf_dir)

        #################################
        # Deal with main configurations #
        #################################
        # Where is the main config file
        self.main_conf = os.path.join(self.conf_dir,"main.conf")

        #Main Configuration object filled by main.conf
        self.main = self.config_file(self.main_conf)
        if self.main == 1:
            print("Something is wrong with main.conf configuration.")

        
        


    def config_dir(self,conf_dir):
        '''
            Make sure everything is good with the configuration directory
        '''        
        if conf_dir == None:
            conf_dir = os.path.join(self.home, ".labeler")

        # Create directory if it does not already exist
        Path(conf_dir).mkdir(parents=True, exist_ok=True) 

        return conf_dir

    def config_file(self,conf_file):
        '''
            Make sure configuration file is good.
        '''
        # Check if path exists        
        if os.path.exists(conf_file):
            # Make sure it is a file, not a directory or symlink
            if os.path.isfile(conf_file):
                # Now create object
                read_result = self.read_conf(conf_file)
                if read_result == 1: # Make sure read was sucessful
                    return 1
                else:
                    return read_result
            else:
                # Something is not quite right with this path
                print("Error: Main Configuration file is not a file, ", conf_file)
                return 1
        # Lets create it
        else:
            write_result=1
            #Routine for creating new main.conf
            if conf_file.find("main.conf"):    
                write_result = self.create_main_conf(conf_file)

            if write_result == 1:
                print("Write of file was unsucessful: ", conf_file)
                return 1
            else:
                return 0            

            # Now create object
            read_result = self.read_conf(conf_file)
            if read_result == 1:
                print("Read of file was unsucessful: ", conf_file)
                return 1
            else:
                return read_result

    def create_main_conf(self,conf_file):
        '''
            Create a new conf file
        '''

        print("Info: Creating new ",conf_file)

        # Create the configuration file as it doesn't exist yet

        # Add content to the file
        Config = configparser.ConfigParser()
        Config.add_section('global')
        Config.set('global', 'user', getpass.getuser())

        try:
            cfgfile = open(conf_file, 'w')
            # write the configuration file
            Config.write(cfgfile)
            cfgfile.close()
            return 0
        except:
            print("Could not create configuration file: ",conf_file)
            return 1


    def read_conf(self,conf_file):
        '''
            Read main configuration file into object
        '''

        # Parse Configs
        try:
            config = configparser.ConfigParser()
            config.read(conf_file)
        except:
            print("Could not parse configuration file: ", conf_file)
            return 1

        return config


