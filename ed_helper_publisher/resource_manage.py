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
import jinja2

from ed_helper_publisher.loggerly import ElasticDevLogger
from ed_helper_publisher.utilities import print_json
from ed_helper_publisher.utilities import to_json
from ed_helper_publisher.utilities import get_hash
from ed_helper_publisher.shellouts import execute3
from ed_helper_publisher.shellouts import execute4
from ed_helper_publisher.utilities import id_generator
from ed_helper_publisher.templating import list_template_files

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

        # by default, we set template_dir relative to the app_dir
        # this can be over written by the inheriting class
        if hasattr(self,"app_dir") and self.app_dir:
            self.template_dir = "{}/_ed_templates".format(self.app_dir)
        else:
            self.template_dir = None

        self._set_docker_settings(**kwargs)
        self._set_destroy_env_vars(**kwargs)

        self._set_os_env_prefix(**kwargs)

        self.output = []

        # e.g.
        # run_dir - current run directory - e.g. /tmp/ondisktmp/abc123/
        # share_dir - share directory with docker or execution container - e.g. /var/tmp/share
        # run_share_dir - share directory with stateful_id - e.g. /var/tmp/share/ABC123
        # app_dir - app directory is run_dir + working directory - e.g. /tmp/ondisktmp/abc123/var/tmp/ansible

    def _set_os_env_prefix(self,**kwargs):

        self.os_env_prefix = kwargs.get("os_env_prefix")
        if self.os_env_prefix: return

        if not self.app_name: return

        if self.app_name == "terraform":
            self.os_env_prefix = "TF_VAR"
        elif self.app_name == "ansible":
            self.os_env_prefix = "ANS_VAR"

    def _get_template_vars(self):

        if os.environ.get("ED_TEMPLATE_VARS"):
            return [ _var.strip() for _var in os.environ.get("ED_TEMPLATE_VARS").split(",") ]

        if not self.app_name: return 

        _key = "{}_TEMPLATE_VARS".format(self.app_name)

        if os.environ.get(_key):
            return [ _var.strip() for _var in os.environ.get(_key).split(",") ]

        if not self.os_env_prefix: return

        # get template_vars e.g. "ANS_VAR_<var>"
        _template_vars = []
        for _var in os.environ.keys():
            if self.os_env_prefix not in _var: continue
            _template_vars.append(_var)

        return _template_vars

    def _set_destroy_env_vars(self,**kwargs):

        try:
            self.destroy_env_vars = eval(os.environ.get("DESTROY_ENV_VARS"))
        except:
            self.destroy_env_vars = None

        self.destroy_execgroup = os.environ.get("DESTROY_EXECGROUP")

    def _set_docker_settings(self,**kwargs):

        self.use_docker = os.environ.get("USE_DOCKER",True)

        if not self.app_name: return

        self.docker_image = os.environ.get("DOCKER_EXEC_ENV",
                                           "elasticdev/{}-run-env".format(self.app_name))

    def _set_stateful_params(self,**kwargs):
     
        self.share_dir = os.environ.get("SHARE_DIR","/var/tmp/share")
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
        # ref 453646
        self.app_dir = os.path.join(self.share_dir,self.stateful_id)

    def _set_app_params(self,**kwargs):

        self.working_subdir = kwargs.get("working_subdir")

        self.app_name = kwargs.get("app_name")
        if not self.app_name: return 

        # below app_name must be defined
        # set working_subdir
        if not self.working_subdir: 
            self.working_subdir = os.environ.get("{}_DIR".format(self.app_name.upper()),
                                                 "/var/tmp/{}".format(self.app_name))

        if self.working_subdir[0] == "/": self.working_subdir = self.working_subdir[1:]

        # ref 453646
        # overide the app_dir set from _set_stateful_params
        # e.g. /var/tmp/share/ABC123/var/tmp/ansible
        self.app_dir = os.path.join(self.run_dir,self.working_subdir)

        # this can be overided by inherited class
        self.shelloutconfig = "elasticdev:::{}::resource_wrapper".format(self.app_name)

    # referenced and related to: dup dhdskyeucnfhrt2634521 
    def get_env_var(self,variable,default=None,must_exists=None):
    
        _value = os.environ.get(variable)
        if _value: return _value

        if self.os_env_prefix: 

            _value = os.environ.get("{}_{}".format(self.os_env_prefix,variable))
            if _value: return _value
    
            _value = os.environ.get("{}_{}".format(self.os_env_prefix,variable.lower()))
            if _value: return _value
    
            _value = os.environ.get("{}_{}".format(self.os_env_prefix,variable.upper()))
            if _value: return _value
    
        if default: return default
    
        if not must_exists: return
        raise MissingEnvironmentVariable("{} does not exist".format(variable))

    def print_json(self,values):
        print_json(values)

    def templify(self,**kwargs):

        _template_vars = self._get_template_vars()

        if not _template_vars:
            self.logger.warn("ED_TEMPLATE_VARS not set - skipping templating")
            return

        if not self.template_dir: 
            self.logger.warn("template_dir not set (None) - skipping templating")
            return

        template_files = list_template_files(self.template_dir)
        if not template_files: 
            self.logger.warn("template_files is empty - skipping templating")
            return

        for _file_stats in template_files:

            template_filepath = _file_stats["file"]
            file_dir = os.path.join(self.app_dir,_file_stats["directory"])
            file_path = os.path.join(self.app_dir,_file_stats["directory"],_file_stats["filename"].split(".ja2")[0])

            if not os.path.exists(file_dir): 
                os.system("mkdir -p {}".format(file_dir))

            if os.path.exists(file_path) and not self.clobber:
                self.logger.warn("destination templated file already exists at {} - skipping templifying of it".format(file_path))
                continue

            self.logger.debug("creating templated file file {} from {}".format(file_path,template_filepath))

            templateVars = {}

            if self.os_env_prefix:
                _split_char = "{}_".format(self.os_env_prefix)
            else:
                _split_char = None

            for _var in _template_vars:

                if _split_char and _split_char in _var:
                    key = _var.strip().split(_split_char)[-1]
                else:
                    key = _var.strip().upper()

                var = _var.strip()

                if not os.environ.get(var): 
                    self.logger.warn("cannot find {} to templify".format(var))
                    continue

                value = os.environ[var].replace("'",'"')
                templateVars[key] = value
                templateVars[key.upper()] = value

            templateLoader = jinja2.FileSystemLoader(searchpath="/")
            templateEnv = jinja2.Environment(loader=templateLoader)
            template = templateEnv.get_template(template_filepath)
            outputText = template.render( templateVars )
            writefile = open(file_path,"wb")
            writefile.write(outputText)
            writefile.close()

    def add_resource_tags(self,resource):

        tags = self.get_env_var("RESOURCE_TAGS")
        if not tags: return

        tags = [ tag.strip() for tag in tags.split(",") ]
        if not isinstance(resource.get("tags"),list): resource["tags"] = []
        resource["tags"].extend(tags)

        if self.app_name: 
            resource["tags"].append(self.app_name)

        # remove duplicates
        resource["tags"] = list(set(resource["tags"]))
 
        return resource

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
