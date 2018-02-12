#!/usr/bin/env python
import json
import os
import subprocess
import tempfile
import boto3



class SSMParameterEnv(object):
    """ Retrives SSM parameters from a prefix and converts them to environmental variables """

    parameters = {}
    def __init__(self, prefix, destination=False):
        self.ssm_prefix = prefix + "env/"

        client = boto3.client('ssm')

        get_params_by_path_args = {
            "Path" : self.ssm_prefix,
            "Recursive" : True,
            "WithDecryption" : True
        }

        while True:
            response = client.get_parameters_by_path(**get_params_by_path_args)

            for parameter in response['Parameters']:
                name = self.path_to_env(parameter['Name'])
                self.parameters[name] = parameter['Value']
            if 'NextToken' not in response.keys():
                break
            else:
                 get_params_by_path_args["NextToken"] = response["NextToken"]

        if destination:
            self.write_variables(self.parameters, destination)

    def path_to_env(self, path):
        """ Converts a SSM path to environmental variable names for DotNet core"""
        path = path[path.startswith(self.ssm_prefix) and len(self.ssm_prefix):]
        path = path.replace("/", "__")
        return path

    def write_variables(self, variables, path):
        """ writes a file containing the enviromental variables to path """
        with open(path, "w") as envfile:
            for name, value in variables.iteritems():
                text = "{}=\"{}\"\n".format(name, value.replace("\"","\\\""))
                envfile.write(text)

class SSMParameterFiles(object):
    """ Retrieves file contents from SSM parameter store and setup files """

    files = {}

    def __init__(self, prefix, write_files=False):
        self.ssm_prefix = prefix + "files/"

        client = boto3.client('ssm')

        get_params_by_path_args = {
            "Path" : self.ssm_prefix,
            "Recursive" : True,
            "WithDecryption" : True
        }

        while True:
            response = client.get_parameters_by_path(**get_params_by_path_args)


            for parameter in response['Parameters']:
                path = parameter['Name']
                path = path[path.startswith(self.ssm_prefix) and len(self.ssm_prefix):]
                path = "/" + path
                contents = parameter['Value']
                self.files[path] = contents
                if write_files:
                    self.write_file(path, contents)

            if 'NextToken' not in response.keys():
                break
            else:
                 get_params_by_path_args["NextToken"] = response["NextToken"]

    def write_file(self, path, contents):
        """ writes a file containing the contents to path """
        with open(path, "w") as envfile:
            envfile.write(contents)
class SSMParameterCmds(object):
    """ Retrieves file contents from SSM parameter store and setup files """

    cmds = {}

    def __init__(self, prefix, run=False):
        self.ssm_prefix = prefix + "cmds/"

        client = boto3.client('ssm')


        get_params_by_path_args = {
            "Path" : self.ssm_prefix,
            "Recursive" : True,
            "WithDecryption" : True
        }

        while True:
            response = client.get_parameters_by_path(**get_params_by_path_args)

            for parameter in response['Parameters']:
                path = parameter['Name']
                contents = parameter['Value']
                self.cmds[path] = contents
                if run:
                    self.run_cmds(self.cmds)

            if 'NextToken' not in response.keys():
                break
            else:
                 get_params_by_path_args["NextToken"] = response["NextToken"]


    def run_cmds(self, cmds):
        """ Runs each script by copying it to a temp file and executing bash with popen and the temp file"""
        for index in sorted(cmds.keys()):
            cmd = cmds[index]
            (temp_fd, temp_path) = tempfile.mkstemp()
            os.write(temp_fd, cmd)
            os.chmod(temp_path, 1909) # chmod 775 but in decimal
            os.close(temp_fd)
            process = subprocess.Popen(temp_path, shell=True, stdout=subprocess.PIPE)
            process.wait()


if __name__ == '__main__':
    #load config from userdata
    CONFIG = json.load(open("/var/lib/cloud/instance/user-data.txt"))
    SSM_PREFIX = CONFIG['ssm']['prefix']
    SSM_DESINATION = CONFIG['ssm']['destination']
    SSMParameterEnv(SSM_PREFIX, SSM_DESINATION)
    SSMParameterFiles(SSM_PREFIX, write_files=True)
    SSMParameterCmds(SSM_PREFIX, run=True)
