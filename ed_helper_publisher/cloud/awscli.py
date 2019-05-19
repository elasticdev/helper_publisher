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
from ed_helper_publisher.resource_manage import ResourceCmdHelper

class AwsCli(ResourceCmdHelper):

    def __init__(self,**kwargs):

        ResourceCmdHelper.__init__(self)
        self.classname = 'AwsCli'
        self.logger = ElasticDevLogger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)

    def parse_set_env_vars(self,set_env_vars):

        self.inputargs = {}

        for env_var in set_env_vars:

            if not os.environ.get(env_var.upper()): continue

            if env_var == "aws_region":
                self.inputargs["region"] = os.environ[env_var.upper()]
            else:
                self.inputargs[env_var] = os.environ[env_var.upper()]

    def get_cmd_region(self,cmd):
        return "{} --region {}".format(cmd,self.region)

    def get_region(self):

        self.region = self.inputargs.get("region")

        if not self.region or self.region == "None": 
            self.region = "us-east-1"

        self.logger.debug('Region set to "{}"'.format(self.region))
