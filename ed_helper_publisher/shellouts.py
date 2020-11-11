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
import string
import os
import random
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT 
from ed_helper_publisher.loggerly import ElasticDevLogger   

def id_generator(size=6,chars=string.ascii_uppercase+string.digits):

    '''generates id randomly'''

    return ''.join(random.choice(chars) for x in range(size))

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
        print '0'*32
        print '0'*32
        print '0'*32
        try:
            output = json.loads(output)
        except:
            print '1'*32
            print '1'*32
            print '1'*32
            print '1'*32
            logger.warn("Could not convert output to json")

    print '2'*32
    print '2'*32
    print output
    print '2'*32
    print '2'*32
    results = {"status":True}
    results["output"] = output

    # Testingyoyo
    print '3'*32
    print '3'*32
    print '3'*32

    if output_queue: 
        print '4'*32
        print '4'*32
        logger.debug("Attempting to place results in the output_queue")
        try:
            print '5'*32
            print '5'*32
            output_queue.put(results)
        except:
            print '6'*32
            print '6'*32
            logger.error("Could not append the results to the output_queue")

    print '7'*32
    print '7'*32
    print '7'*32
    print '7'*32
    print results
    return results

def execute2(cmd,print_error=True,**kwargs):
    return execute4(cmd,print_error=True,**kwargs)

def execute4(cmd,print_error=True,**kwargs):

    logger = ElasticDevLogger("execute3")
    output_to_json = kwargs.get("output_to_json",True)
    #cmd = 'cd {}; (./run_order 2>&1 ; echo $? > {}) | tee -a {}; exit `cat {}`'.format(link,exit_file,logfile,exit_file)

    exit_file = "/tmp/{}".format(id_generator(10,chars=string.ascii_lowercase))
    logfile = "/tmp/{}".format(id_generator(10,chars=string.ascii_lowercase))

    cmd = '({} 2>&1 ; echo $? > {}) | tee -a {}; exit `cat {}`'.format(cmd,exit_file,logfile,exit_file)

    exitcode = os.system(cmd)

    status = None
    if exitcode == 0: status = True

    output = open(logfile,"r").readlines()

    if output_to_json and not isinstance(output,dict):
        try:
            output = json.loads(output)
        except:
            logger.warn("Could not convert output to json")

    results = { "output":output,
                "status":status }

    exit_error = kwargs.get("exit_error")

    if exit_error and not status:
        print output
        exit(exitcode)

    return results
