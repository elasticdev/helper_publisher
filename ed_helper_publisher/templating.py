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
#Written by Gary Leong  <gary@elasticdev.io, Dec 04,2020

import os
import re

def list_template_files(rootdir,split_dir="_ed_templates"):

    '''
    list files with .ja2 suffix for templating
    '''

    print ''
    print ''
    print ''
    print ''
    print rootdir
    print rootdir
    print rootdir
    print rootdir
    print split_dir
    print split_dir
    print split_dir
    print ''
    print ''
    print ''
    print ''
    raise

    if not os.path.exists(rootdir): return

    # get a base file lists
    base_files = []

    for _root, _subFolders, _files in os.walk(rootdir):
        tempList = []

        for _file in _files:
            f = os.path.join(_root,_file)
            tempList.append(f)

        if not tempList: continue

        for _file in tempList:
            if not re.search(".ja2$",_file): continue
            base_files.append(_file)

    # categorize files
    fileList = []

    for _file in base_files:
        _rel_file = _file.split("{}/".format(split_dir))[-1]

        filename = os.path.basename(_rel_file)

        try:
            directory = os.path.dirname(_rel_file)
        except:
            directory = None

        _finput = { "file":_file,
                    "filename":filename,
                    "directory":directory }

        fileList.append(_finput)

    return fileList
