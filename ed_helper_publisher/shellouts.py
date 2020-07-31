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

#import contextlib
import json
import os
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT 
from ed_helper_publisher.loggerly import ElasticDevLogger   

def mkdir(directory):
    '''uses the shell to make a directory.'''

    try:
        if not os.path.exists(directory):
            os.system("mkdir -p %s" % (directory))
        return True
    except:
        return False

def chkdir(directory):

    if not os.path.exists(directory):
        print "Directory {} does not exists".format(directory)
        return False
    return True

def rm_rf(location):

    '''uses the shell to forcefully and recursively remove a file/entire directory.'''

    if not location: return False

    try:
        os.remove(location)
        status = True
    except:
        status = False

    if status is False and os.path.exists(location):
        try:
            os.system("rm -rf %s > /dev/null 2>&1" % (location))
            return True
        except:
            print "problems with removing %s" % location
            return False


def execute3(cmd,print_error=True,**kwargs):

    logger = ElasticDevLogger("execute3")
    logger.debug("Running command %s from directory %s" % (cmd,os.getcwd()))

    output_queue = kwargs.get("output_queue")
    env_vars = kwargs.get("env_vars")
    output_to_json = kwargs.get("output_to_json",True)

    if env_vars:
        env_vars = env_vars.get()

        for ek,ev in env_vars.iteritems():
            if ev is None:
                ev = "None"
            elif not isinstance(ev,str) and not isinstance(ev,unicode):
                ev = str(ev)
            logger.debug("Setting environment variable {} to {}, type {}".format(ek,ev,type(ev)))
            os.environ[ek] = ev

    exit_error = kwargs.get("exit_error")

    process = Popen(cmd,shell=True,bufsize=0,stdout=PIPE,stderr=STDOUT)
    output = process.communicate()[0]

    if process.returncode != 0: 

        logger.aggmsg('exit code {}'.format(process.returncode,new=True))
        logger.aggmsg(output,prt=True,cmethod="error")

        results = {"status":False}
        results["failed_message"] = output
        results["output"] = output
        results["exitcode"] = process.returncode
        if output_queue: output_queue.put(results)
        if exit_error: exit(process.returncode)
        return results

    if output_to_json and not isinstance(output,dict):
        try:
            output = json.loads(output)
        except:
            logger.warn("Could not convert output to json")

    results = {"status":True}
    results["output"] = output

    if output_queue: 
        logger.debug("Attempting to place results in the output_queue")
        try:
            output_queue.put(results)
        except:
            logger.error("Could not append the results to the output_queue")

    return results
