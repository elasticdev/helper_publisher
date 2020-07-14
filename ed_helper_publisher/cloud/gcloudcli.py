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
#Written by Gary Leong  <gary@elasticdev.io, May 11,2020

import os
import json

from ed_helper_publisher.loggerly import ElasticDevLogger
from ed_helper_publisher.utilities import OnDiskTmpDir
from ed_helper_publisher.resource_manage import ResourceCmdHelper

class GcloudCli(ResourceCmdHelper):

    def __init__(self,**kwargs):

        ResourceCmdHelper.__init__(self)
        self.classname = 'GcloudCli'
        self.logger = ElasticDevLogger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)
        self.file_config = None
        self.file_config_loc = None
        self.tempdir = None
        self.resource_tags_keys = [ "tags", 
                                    "name", 
                                    "schedule_id", 
                                    "job_instance_id",
                                    "job_id" ]

    def get_tags(self):

        tags = [ self.gcloud_region, 
                 self.product, 
                 self.provider ]

        for key_eval in self.resource_tags_keys:
            if not self.inputargs.get(key_eval): continue
            tags.append(self.inputargs[key_eval])

        return tags

    def set_ondisktmp(self):
        self.tempdir = OnDiskTmpDir()

    def write_file_config(self):

        with open(self.file_config_loc, 'w') as _file:
            _file.write(json.dumps(self.file_config,indent=4))

    def parse_set_env_vars(self,set_env_vars):

        self.inputargs = {}

        for env_var in set_env_vars:

            if not os.environ.get(env_var.upper()): continue

            if env_var == "gcloud_region":
                self.inputargs["gcloud_region"] = os.environ[env_var.upper()]
            else:
                self.inputargs[env_var] = os.environ[env_var.upper()]

    def get_resource_tags(self,**kwargs):

        name = kwargs.get("name")
        if not name: name = self.inputargs.get("name")
        
        tags = "["
        if name: tags = tags + "{"+"Key={},Value={}".format("Name",name)+"}"
        
        for key_eval in self.resource_tags_keys:
            if not self.inputargs.get(key_eval): continue
            tags = tags + ",{"+"Key={},Value={}".format(key_eval,self.inputargs[key_eval])+"}"
        tags = tags + "]"

        return tags

    def get_region(self):

        self.gcloud_region = self.inputargs.get("gcloud_region")

        if not self.gcloud_region or self.gcloud_region == "None": 
            self.gcloud_region = "us-west1"

        self.logger.debug('Region set to "{}"'.format(self.gcloud_region))

    def set_credentials(self):

        #self.google_application_credentials = self.inputargs.get("google_application_credentials")
        self.google_application_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS","/tmp/credentials.json")

        return self.google_application_credentials

    def get_init_credentials_cmds(self):

        self.set_credentials()
        self.set_project()

        cmds = [ "gcloud auth activate-service-account --key-file={}".format(self.google_application_credentials) ]
        cmds.append("gcloud config set project {}".format(self.gcloud_project))

        return cmds

    def set_project(self):

        self.gcloud_project = os.environ.get["GCLOUD_PROJECT"]

        return self.gcloud_project
