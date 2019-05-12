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
import logging
from logging import config

class ElasticDevLogger(object):

    def __init__(self,name,**kwargs):

        self.classname = 'ElasticDevLogger'

        logger = get_logger(name,**kwargs)
        self.direct = logger[0]
        self.name = logger[1]
        self.aggregate_msg = None

    def aggmsg(self,message,new=False,prt=None,cmethod="debug"):

        if not self.aggregate_msg: new = True

        if not new: 
            self.aggregate_msg = "{}\n{}".format(self.aggregate_msg,message)
        else:
            self.aggregate_msg = "\n{}".format(message)

        if not prt: self.aggregate_msg

        msg = self.aggregate_msg
        self.print_aggmsg(cmethod)

        return msg

    def print_aggmsg(self,cmethod="debug"):

        _method = 'self.{}({})'.format(cmethod,"self.aggregate_msg")
        eval(_method)
        self.aggregate_msg = ""

    def debug_highlight(self,message):
        self.direct.debug("+"*32)
        self.direct.debug(message)
        self.direct.debug("+"*32)

    def info(self,message):
        self.direct.info(message)

    def debug(self,message):
        self.direct.debug(message)

    def critical(self,message):
        self.direct.critical("!"*32)
        self.direct.critical(message)
        self.direct.critical("!"*32)

    def error(self,message):
        self.direct.error("*"*32)
        self.direct.error(message)
        self.direct.error("*"*32)

    def warn(self,message):
        self.direct.warn("-"*32)
        self.direct.warn(message)
        self.direct.warn("-"*32)

def get_logger(name,**kwargs):

    # if stdout_only is set, we won't write to file
    stdout_only = kwargs.get("stdout_only")
    
    # Set loglevel
    loglevel = kwargs.get("loglevel")
    if not loglevel: loglevel = os.environ.get("ED_LOGLEVEL")
    if not loglevel: loglevel = "DEBUG"
    loglevel = loglevel.upper()

    # Set logdir and logfile
    if not stdout_only:

        logdir = kwargs.get("logdir")
        if not logdir: logdir = os.environ.get("LOG_DIR")
        if not logdir: logdir = "/tmp/ed/log"

        logfile = "{}/{}".format(logdir,"ed_main.log")

        if not os.path.exists(logdir): os.system("mkdir -p {}".format(logdir))
        if not os.path.exists(logfile): os.system("touch {}".format(logfile))

    formatter = kwargs.get("formatter","module")
    name_handler = kwargs.get("name_handler","console,loglevel_file_handler,error_file_handler")

    # defaults for root logger
    logging.basicConfig(level=eval("logging.%s" % loglevel))
    name_handler = [ x.strip() for x in list(name_handler.split(",")) ]

    # Configure loglevel
    # Order of precedence:
    # 1 loglevel specified
    # 2 logcategory specified
    # 3 defaults to "debug"

    log_config = {"version":1}
    log_config["disable_existing_loggers"] = False

    log_config["formatters"] = {
        "simple": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": '%Y-%m-%d %H:%M:%S'
        },
        "module": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": '%Y-%m-%d %H:%M:%S'
        }
    }

    if stdout_only:

        log_config["handlers"] = {
            "console": {
                "class": "logging.StreamHandler",
                "level": loglevel,
                "formatter": formatter,
                "stream": "ext://sys.stdout"
            }
        }

    else:

        log_config["handlers"] = {
            "console": {
                "class": "logging.StreamHandler",
                "level": loglevel,
                "formatter": formatter,
                "stream": "ext://sys.stdout"
            },
            "info_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": formatter,
                "filename": logdir+"info.log",
                "maxBytes": "10485760",
                "backupCount": "20",
                "encoding": "utf8"
            },
            "loglevel_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": loglevel,
                "formatter": formatter,
                "filename": logdir+loglevel+".log",
                "maxBytes": "10485760",
                "backupCount": "20",
                "encoding": "utf8"
            },
            "error_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": formatter,
                "filename": logdir+"errors.log",
                "maxBytes": "10485760",
                "backupCount": "20",
                "encoding": "utf8"
            }
        }

    log_config["loggers"] = {
        name: {
            "level": loglevel,
            "handlers": name_handler,
            "propagate": False 
        }
    }

    log_config["root"] = {
        "level": loglevel,
        "handlers": name_handler
    }

    config.dictConfig(log_config) 
    logger = logging.getLogger(name)
    logger.setLevel(eval("logging."+loglevel))

    return logger,name
