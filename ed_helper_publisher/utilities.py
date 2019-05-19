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
import os
import hashlib

from ed_helper_publisher.loggerly import ElasticDevLogger

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

def convert_str2json(_object,exit_error=None):

    if isinstance(_object,dict): return _object
    if isinstance(_object,list): return _object
    logger = ElasticDevLogger("convert_str2json")

    try:
        _object = json.loads(_object)
        return _object
    except:
        logger.error("Cannot convert str to a json.  Will try to eval")

    try:
        _object = eval(_object)
        return _object
    except:
        logger.error("Cannot eval str to a json.")

        if exit_error: exit(13)
        return False

    return _object

def shellout_hash(string):

    try:
        cmd = os.popen('echo "%s" | md5sum | cut -d " " -f 1' % string, "r")
        ret = cmd.read().rstrip()
    except: 
        print "Failed to calculate the md5sum of a string %s" % string
        return False
    return ret

def get_hash(data):

    '''determines the hash of a data object'''

    logger = ElasticDevLogger("get_hash")

    try:
        calculated_hash = hashlib.md5(data).hexdigest()
    except:
        logger.warn("Falling back to shellout md5sum for hash")
        calculated_hash = shellout_hash(data)

    if not calculated_hash:
        logger.error("Could not calculate hash for %s" % data)
        return False

    return calculated_hash
