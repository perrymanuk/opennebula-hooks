#!/usr/bin/python
from ConfigParser import SafeConfigParser
import xmlrpclib
import urllib2
import urllib
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
import logging
import requests
import subprocess
import sys
from socket import gethostname
from requests.auth import HTTPBasicAuth
from ConfigParser import SafeConfigParser
import time

parser = SafeConfigParser()
try:
   parser.read("/usr/local/etc/influxdb.conf")
   host = parser.get("db", "host")
   database = parser.get("db", "database")
   username = parser.get("auth", "username")
   password = parser.get("auth", "password")
   instance = parser.get("cloud","instance")
except:
   print "Unable to read from config file"
   sys.exit(1)

influx_url = "http://"+host+"/write?db="+database

with open("userauth","r") as authfile:
	auth_string = authfile.read().replace("\n","")

hostname = "dev-hn1.nubes.rl.ac.uk"
server = xmlrpclib.ServerProxy("https://"+hostname+"/RPC2")
response = server.one.user.login(auth_string, "testgroup", "dontleaveblank", 1000)
session_id = response[1]
one_auth = "testgroup:" + session_id
