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

    def __init__(self,passphrase=None,iv=None):

        self.BLOCK_SIZE=16
        self.iv = iv

        if not passphrase: passphrase = 'reoTiJuFc440173r'
        self.passphrase = passphrase
 
    def encrypt(self,_str,passphrase=None):

        atfork()

        if not passphrase: passphrase = self.passphrase

        if not self.iv: 
            iv = Random.new().read(self.BLOCK_SIZE)
        else:
            iv = self.iv

        aes = AES.new(str(passphrase), AES.MODE_CFB, iv)

        return base64.b64encode(iv + aes.encrypt(_str.encode('ascii', 'ignore')))

    def decrypt(self,encrypted,passphrase=None):

        atfork()

        if not passphrase: passphrase = self.passphrase
        encrypted = base64.b64decode(encrypted)
        iv = encrypted[:self.BLOCK_SIZE]
        aes = AES.new(str(passphrase), AES.MODE_CFB, iv)
        return aes.decrypt(encrypted[self.BLOCK_SIZE:])

class PermJWE(object):

    def __init__(self,**kwargs):

        self.algor = kwargs.get("algor","HS256")
        #self.secret = kwargs.get("secret","reoTiJuFc440173r")
        self.str_key = "hKJpfMMKPUkv4LuLYrI/HqJ8k9OWthXH+UXhE25+K788Zg2NFVskn9sqIERvACAcIMMShCJwPqma63fhuPBqKDnRdKNRxOq+Y7NTcTYT8g=="
        self.classname = "PermJWE"

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

    def e_serialize(self,obj,passphrase="reoTiJuFc440173r",iv=None):
    
        if isinstance(obj,dict):
            _str = json.dumps(obj)
        else:
            _str = obj 
    
        return ObjSerialize(passphrase=str(passphrase),iv=iv).encrypt(_str)

    def create_symmetric_key(self):

        symmetric_key = jwk.JWK(generate='oct',size=256).export()
        results = {"key":symmetric_key}
        results["str_key"] = self.e_serialize(symmetric_key)
        
        return results
    
    def de_serialize(self,encrypted,passphrase="reoTiJuFc440173r",convert2json=True):
        _str = ObjSerialize(passphrase=str(passphrase)).decrypt(encrypted)
        if not convert2json: return _str
        return self.byteify(json.loads(_str))

    def _get_key(self,**kwargs):

        key = kwargs.get("key")
        str_key = kwargs.get("str_key")
        
        if key and not isinstance(key,dict): 
            key = eval(key)
        elif str_key:
            key = dict(self.de_serialize(str_key,convert2json=True))
        else:
            print "using default symmetric key"
            key = dict(self.de_serialize(self.str_key,convert2json=True))

        return key

    def encrypt(self,**kwargs):

        values = kwargs["values"]
        key = self._get_key(**kwargs)

        secret = kwargs.get("secret")
        if not secret: secret = self._get_md5sum(key)
        header = kwargs.get("header",{"alg": "A256KW", "enc": "A256CBC-HS512"})

        emessage = self.e_serialize(values,passphrase=secret)

        payload = {}
        payload["emessage"] = emessage

        _key = jwk.JWK(**key)

        _token = jwt2.JWT(header={"alg": self.algor},
                          claims=payload)

        _token.make_signed_token(_key)

        etoken = jwt2.JWT(header=header,
                          claims=_token.serialize())

        etoken.make_encrypted_token(_key)

        return etoken.serialize()

    def decrypt(self,**kwargs):

        etoken = kwargs["token"]
        key = self._get_key(**kwargs)
        secret = kwargs.get("secret",self._get_md5sum(key))

        key = jwk.JWK(**key)
        ET = jwt2.JWT(key=key,jwt=etoken)
        ST = jwt2.JWT(key=key,jwt=ET.claims)

        emessage = eval(ST.claims)["emessage"]

        return self.de_serialize(emessage,passphrase=secret,convert2json=True)
