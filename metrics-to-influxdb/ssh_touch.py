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

with open("userauth","r") as authfile:
	auth_string = authfile.read().replace("\n","")

hostname = "dev-hn1.nubes.rl.ac.uk"
server = xmlrpclib.ServerProxy("https://"+hostname+"/RPC2")
response = server.one.user.login(auth_string, "testgroup", "dontleaveblank", 1000)
session_id = response[1]
one_auth = "testgroup:" + session_id

vm_xml = server.one.vmpool.info(one_auth, -1, -1, -1, 3)[1]
vm_pool = ET.fromstring(vm_xml)

def get_vm_ip(vm_id):
	for vm in vm_pool.findall("VM"):
		if int(vm_id) == int(vm.find("ID").text):
			ip = vm.find("TEMPLATE/NIC/IP").text
			break
		else:
			ip = "err"

	return ip

def ssh_touch(ip):
	start = time.time()
	command = subprocess.call(["ssh", "testgroup@" + str(ip), "touch", "testfile"])
	elapsed = str(time.time() - start)[0:4]

	return elapsed

if __name__ == "__main__":
	vm_id = sys.argv[1]
	print ssh_touch(get_vm_ip(vm_id))
