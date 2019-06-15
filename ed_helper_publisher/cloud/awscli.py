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
import json

from ed_helper_publisher.loggerly import ElasticDevLogger
from ed_helper_publisher.utilities import OnDiskTmpDir
from ed_helper_publisher.resource_manage import ResourceCmdHelper

class AwsCli(ResourceCmdHelper):

    def __init__(self,**kwargs):

        ResourceCmdHelper.__init__(self)
        self.classname = 'AwsCli'
        self.logger = ElasticDevLogger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)
        self.file_config = None
        self.file_config_loc = None
        self.tempdir = None

    def set_ondisktmp(self):
        self.tempdir = OnDiskTmpDir()

    def write_file_config(self):

        with open(self.file_config_loc, 'w') as _file:
            _file.write(json.dumps(self.file_config,indent=4))

    def parse_set_env_vars(self,set_env_vars):

        self.inputargs = {}

        for env_var in set_env_vars:

            if not os.environ.get(env_var.upper()): continue

            if env_var == "aws_default_region":
                self.inputargs["aws_default_region"] = os.environ[env_var.upper()]
            else:
                self.inputargs[env_var] = os.environ[env_var.upper()]

    def get_cmd_region(self,cmd):
        return "{} --region {}".format(cmd,self.aws_default_region)

    def get_region(self):

        self.aws_default_region = self.inputargs.get("aws_default_region")

        if not self.aws_default_region or self.aws_default_region == "None": 
            self.aws_default_region = "us-east-1"

        self.logger.debug('Region set to "{}"'.format(self.aws_default_region))
