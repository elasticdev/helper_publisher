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
from ed_helper_publisher.utilities import to_json
from ed_helper_publisher.utilities import get_hash
from ed_helper_publisher.shellouts import execute3
from ed_helper_publisher.shellouts import execute4
from ed_helper_publisher.utilities import id_generator

# Testingyoyo
class MissingEnvironmentVariable(Exception):
    pass

class ResourceCmdHelper(object):

    def __init__(self,**kwargs):

        self.classname = 'ResourceCmdHelper'
        self.logger = ElasticDevLogger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)

        self.run_dir = os.getcwd()

        # must exists as environmental variables
        self.must_exists = kwargs.get("must_exists",[])

        self._set_stateful_params(**kwargs)
        self._set_app_params(**kwargs)
        self._set_docker_settings(**kwargs)
        self._set_destroy_env_vars(**kwargs)

        self.output = []

        # e.g.
        # run_dir - current run directory - e.g. /tmp/ondisktmp/abc123/
        # share_dir - share directory with docker or execution container - e.g. /var/tmp/share
        # run_share_dir - share directory with stateful_id - e.g. /var/tmp/share/ABC123
        # app_dir - app directory is run_dir + working directory - e.g. /tmp/ondisktmp/abc123/var/tmp/ansible

    def _set_destroy_env_vars(self,**kwargs):

        try:
            self.destroy_env_vars = eval(os.environ.get("DESTROY_ENV_VARS"))
        except:
            self.destroy_env_vars = None

        self.destroy_execgroup = os.environ.get("DESTROY_EXECGROUP")

    def _set_docker_settings(self,**kwargs):

        self.use_docker = os.environ.get("USE_DOCKER",True)

        self.docker_image = os.environ.get("DOCKER_EXEC_ENV",
                                           default="elasticdev/{}-run-env".format(self.app_name))

    def _set_stateful_params(self,**kwargs):
     
        self.share_dir = os.environ.get("SHARE_DIR",default="/var/tmp/share")
        self.stateful_id = os.environ.get("STATEFUL_ID")
        self.stateful_dir = os.environ.get("STATEFUL_DIR")

        if not self.stateful_id and 'stateful_id' in self.must_exists: 
            raise MissingEnvironmentVariable("{} does not exist".format("STATEFUL_ID"))

        if not self.stateful_id: self.stateful_id = id_generator(20)

        # run_share_dir
        self.run_share_dir = os.path.join(self.share_dir,self.stateful_id)

        #if self.stateful_id:
        #    self.run_share_dir = os.path.join(self.share_dir,self.stateful_id)
        #else:
        #    self.run_share_dir = self.share_dir

        # This can be overwritten - either you run from the share directory
        # or the run_dir + app/working_subdir
        self.app_dir = os.path.join(self.share_dir,self.stateful_id)

    def _set_app_params(self,**kwargs):

        self.working_subdir = kwargs.get("working_subdir")

        app_name = kwargs.get("app_name").lower()
        if not app_name: return 

        # below app_name must be defined
        # set working_subdir
        if not self.working_subdir: 
            self.working_subdir = os.environ.get("{}_DIR".format(app_name.upper()),
                                                 default="/var/tmp/{}".format(app_name))

        if self.working_subdir[0] == "/": self.working_subdir = self.working_subdir[1:]

        self.app_name = app_name

        # set app_dir
        # e.g. /var/tmp/share/ABC123/var/tmp/ansible
        self.app_dir = os.path.join(self.run_dir,self.working_subdir)

        # this can be overided by inherited class
        self.shelloutconfig = "elasticdev:::{}::resource_wrapper".format(self.app_name)

    def get_hash(self,_object):
        return get_hash(_object)

    def add_output(self,cmd=None,remove_empty=None,**results):

        #_outputs = self.convert_to_json(results["output"])
        #if not isinstance(_outputs,dict): return 

        try:
            _outputs = to_json(results["output"])
        except:
            _outputs = None

        if not _outputs: return

        if cmd: self.output.append(cmd)

        for _output in _outputs: 
            if remove_empty and not _output: continue
            self.output.extend(_output)

    def convert_to_json(self,output):

        if isinstance(output,dict): return output

        try:
            _output = to_json(output)
            if not _output: raise
            if not isinstance(_output,dict): raise
            output = _output
        except:
            self.logger.warn("Could not convert output to json")

        return output

    def to_json(self,output):
        return self.convert_to_json(output)

    def print_output(self,**kwargs):

        output = self.convert_to_json(kwargs["output"])

        print '_ed_begin_output'
        print output
        print '_ed_end_output'
        exit(0)

    def _print_output(self,**kwargs):

        output_to_json = kwargs.get("output_to_json",True)
        output = kwargs.get("output")
        if not output: output = "There is no output from the command"
        if output_to_json: output = self.convert_to_json(output)

        print ''
        print ''
        print '_ed_begin_output'
        print output
        print '_ed_end_output'

    def successful_output(self,**kwargs):
        self._print_output(**kwargs)
        exit(0)

    def execute(self,cmd,**kwargs):
        return execute3(cmd,**kwargs)

    def execute2(self,cmd,**kwargs):
        return execute3(cmd,**kwargs)
        #return execute4(cmd,**kwargs)

    def execute4(self,cmd,**kwargs):
        return execute4(cmd,**kwargs)

    def cmd_failed(self,**kwargs):
         
        failed_message = kwargs.get("failed_message")

        if not failed_message: 
            failed_message = "No failed message to outputted"

        self.logger.error(message=failed_message)
        exit(9)

    def set_inputargs(self,upper_case=True,**kwargs):

        if kwargs.get("inputargs"):
            self.inputargs = kwargs["inputargs"]
        elif kwargs.get("json_input"):
            self.inputargs = to_json(kwargs["json_input"],exit_error=True)
        elif kwargs.get("set_env_vars"):
            self.parse_set_env_vars(kwargs["set_env_vars"],upper_case=upper_case)

        for _k,_v in self.inputargs.iteritems():
            if _v != "False": continue
            self.inputargs[_k] = False

    # This can be replaced by the inheriting class
    def parse_set_env_vars(self,env_vars,upper_case=True):

        self.inputargs = {}

        for env_var in env_vars:

            if upper_case:
                _var = env_var.upper()
            else:
                _var = env_var

            if not os.environ.get(_var): continue
            if os.environ.get(_var) == "None": continue

            if os.environ.get(_var) == "False": 
                self.inputargs[_var] = False
                continue

            if upper_case:
                self.inputargs[env_var] = os.environ[_var]
            else:
                self.inputargs[_var] = os.environ[_var]

    def check_required_inputargs(self,**kwargs):

        status = True
        required_keys = []

        _keys = kwargs.get("keys")
        if not _keys: return 

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
      
        _keys = kwargs.get("keys")
        if not _keys: return 

        for key in kwargs["keys"]:
            if key in self.inputargs: return 

        self.logger.aggmsg("one of these keys need to be set:",new=True)
        self.logger.aggmsg("")

        for key in kwargs["keys"]:
            self.logger.aggmsg("\t{} or Environmental Variable {}".format(key,key.upper()))

        failed_message = self.logger.aggmsg("")
        self.cmd_failed(failed_message=failed_message)
