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

import base64
import json

from jwcrypto import jwt as jwt2
from jwcrypto import jwk

from Crypto import Random
from Crypto.Random import atfork
from Crypto.Cipher import AES

from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT

class ObjSerialize(object):

    def __init__(self):

        self._block_size=16
        self._default_passphrase = 'reoTiJuFc440173r'

    def _set_eparams(self,**kwargs):

        self.iv = kwargs.get("iv")
        self.passphrase = kwargs.get("passphrase")
        if not self.passphrase: self.passphrase = self._default_passphrase

    def _byteify(self,input):

        if isinstance(input, dict):
            values = {self._byteify(key): self._byteify(value)
                      for key, value in input.iteritems()}
        elif isinstance(input, list):
            values = [self._byteify(element) for element in input]
        elif isinstance(input, unicode):
            values = input.encode('utf-8')
        else:
            values = input

        return values

    def set(self,obj,**kwargs):

        atfork()

        self._set_eparams(**kwargs)

        if not self.iv: 
            iv = Random.new().read(self._block_size)
        else:
            iv = self.iv

        aes = AES.new(str(self.passphrase), AES.MODE_CFB, iv)

        return base64.b64encode(iv + aes.encrypt(obj.encode('ascii', 'ignore')))

    def unset(self,encrypted,**kwargs):

        atfork()
        self._set_eparams(**kwargs)

        encrypted = base64.b64decode(encrypted)
        iv = encrypted[:self._block_size]
        aes = AES.new(str(self.passphrase), AES.MODE_CFB, iv)

        result = aes.decrypt(encrypted[self._block_size:])

        if not kwargs.get("convert2json"): return result

        return self._byteify(json.loads(result))

class PermJWE(object):

    def __init__(self,**kwargs):

        self.obj_serialize = ObjSerialize()
        self.algor = kwargs.get("algor","HS256")
        self._symmetric_key = "hKJpfMMKPUkv3LuLYrI/HqJ8k3OWthXH+UXhE25+K738Zg2NFVskn8sqIERvACAcIMMShCJwPqma83fhuPBqKDnRdKNRxOq+Y7NTcTYT9g=="
        self.classname = "PermJWE"

    def _get_md5sum(self,hash_object):
    
        '''determines the md5sum of a string through the use of the unix shell'''
    
        cmd = 'echo "%s" | md5sum | cut -d " " -f 1' % hash_object
    
        try:
            process = Popen(cmd,shell=True,bufsize=0,stdout=PIPE,stderr=STDOUT)
            out,error = process.communicate()
            exitcode = process.returncode
            ret = out.rstrip()
            if exitcode == 0: return ret
    
            print "Failed to calculate the md5sum of a string %s" % hash_object
        except:
            print "Failed to calculate the md5sum of a string %s" % hash_object
    
        return False

    def _get_key(self,**kwargs):

        key = kwargs.get("key")
        
        if key and not isinstance(key,dict): 
            key = eval(key)
        else:
            key = dict(self.obj_serialize.unset(self._symmetric_key,convert2json=False))
            print "using default symmetric key"

        return key

    def encrypt(self,**kwargs):

        values = kwargs.get("values")
        filename = kwargs.get("filename")

        if not values and not filename:
            print "We need values or a filename to encrypt data"

        if not values and filename:
            with open(filename) as json_file:
                values = json.load(json_file)

        key = self._get_key(**kwargs)

        secret = kwargs.get("secret")
        if not secret: secret = self._get_md5sum(key)
        header = kwargs.get("header",{"alg": "A256KW", "enc": "A256CBC-HS512"})

        emessage = self.obj_serialize.set(values,passphrase=secret)

        payload = {"emessage":emessage}

        _key = jwk.JWK(**key)

        _token = jwt2.JWT(header={"alg": self.algor},
                          claims=payload)

        _token.make_signed_token(_key)

        etoken = jwt2.JWT(header=header,
                          claims=_token.serialize())

        etoken.make_encrypted_token(_key)

        return etoken.serialize()

    def decrypt(self,**kwargs):

        filename = kwargs.get("filename")
        etoken = kwargs["token"]
        key = self._get_key(**kwargs)
        secret = kwargs.get("secret",self._get_md5sum(key))

        key = jwk.JWK(**key)
        ET = jwt2.JWT(key=key,jwt=etoken)
        ST = jwt2.JWT(key=key,jwt=ET.claims)

        emessage = eval(ST.claims)["emessage"]

        data = self.obj_serialize.unset(emessage,passphrase=secret,convert2json=True)

        if not filename: return data

        with open("/tmp/test.json", 'w') as json_file:

            json_string = json.dumps(etoken.serialize(), 
                                     default=lambda o: o.__dict__, 
                                     sort_keys=True, 
                                     indent=2)

            json_file.write(json_string)

        return data
