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

import datetime
import json

class DateTimeJsonEncoder(json.JSONEncoder):

    def default(self,obj):

        if isinstance(obj,datetime.datetime):
            #newobject = str(obj.timetuple())
            newobject = '-'.join([ str(element) for element in list(obj.timetuple())][0:6])
            return newobject

        return json.JSONEncoder.default(self,obj)

def print_json(results):
    print json.dumps(results,sort_keys=True,cls=DateTimeJsonEncoder,indent=4)

def nice_json(results):
    return json.dumps(results,sort_keys=True,cls=DateTimeJsonEncoder,indent=4)
