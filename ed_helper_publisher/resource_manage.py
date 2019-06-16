#!/usr/bin/env python
#
#Project: elasticdev_publisher: ElasticDev is a SaaS for building and managing 
#software and DevOps automation. This particular packages is a python
#helper for publishing stacks, hostgroups, shellouts/scripts and other
#assets used for automation
#
#Examples include cloud infrastructure, CI/CD, and data analytics
#
#Copyright (C) Gary Leong - All Rights Reserved
#Unauthorized copying of this file, via any medium is strictly prohibited
#Proprietary and confidential
#Written by Gary Leong  <gary@elasticdev.io, May 11,2019

import os

from ed_helper_publisher.loggerly import ElasticDevLogger
from ed_helper_publisher.utilities import print_json
from ed_helper_publisher.utilities import convert_str2json
from ed_helper_publisher.utilities import get_hash
from ed_helper_publisher.shellouts import execute3

class ResourceCmdHelper(object):

    def __init__(self,**kwargs):

        self.classname = 'ResourceCmdHelper'
        self.logger = ElasticDevLogger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)

    def get_hash(self,_object):
        return get_hash(_object)

    def _print_output(self,**kwargs):

        output_to_json = kwargs.get("output_to_json",True)
        output = kwargs.get("output")
        if not output: output = "There is no output from the command"

        print ''
        print ''
        
        if output_to_json:
            try:
                print_json(output)
            except:
                print output
        print ''
        print ''
        print '_ed_begin_output'
        print output
        print '_ed_end_output'

    def successful_output(self,**kwargs):
        self._print_output(**kwargs)
        exit(0)

    def execute(self,cmd,**kwargs):
        #output_to_json = kwargs.get("output_to_json",True)
        return execute3(cmd,**kwargs)

    def cmd_failed(self,**kwargs):
         
        failed_message = kwargs.get("failed_message")

        if not failed_message: 
            failed_message = "No failed message to outputted"

        self.logger.error(message=failed_message)
        exit(9)

    def set_inputargs(self,**kwargs):

        if kwargs.get("inputargs"):
            self.inputargs = kwargs["inputargs"]
        elif kwargs.get("json_input"):
            self.inputargs = convert_str2json(kwargs["json_input"],exit_error=True)
        elif kwargs.get("set_env_vars"):
            self.parse_set_env_vars(kwargs["set_env_vars"])

    # This can be replaced by the inheriting class
    def parse_set_env_vars(self,set_env_vars):

        self.inputargs = {}

        for env_var in set_env_vars:
            if not os.environ.get(env_var.upper()): continue
            self.inputargs[env_var] = os.environ[env_var.upper()]

    def check_required_inputargs(self,**kwargs):

        status = True
        required_keys = []

        for key in kwargs["keys"]:
            if key not in self.inputargs: 
                required_keys.append(key)
                status = None

        if status: return True

        self.logger.aggmsg("These keys need to be set:",new=True)
        self.logger.aggmsg("")

        for key in required_keys:
            self.logger.aggmsg("\t{} or Environmental Variable {}".format(key,key.upper()))

        failed_message = self.logger.aggmsg("")
        self.cmd_failed(failed_message=failed_message)

    def check_either_inputargs(self,**kwargs):
      
        for key in kwargs["keys"]:
            if key in self.inputargs: return 

        self.logger.aggmsg("one of these keys need to be set:",new=True)
        self.logger.aggmsg("")

        for key in kwargs["keys"]:
            self.logger.aggmsg("\t{} or Environmental Variable {}".format(key,key.upper()))

        failed_message = self.logger.aggmsg("")
        self.cmd_failed(failed_message=failed_message)
