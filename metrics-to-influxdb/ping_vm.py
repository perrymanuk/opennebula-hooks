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
import os
import re

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

def get_average_ping(ip):
	ping = subprocess.Popen(["ping", "-c", "3", ip], stdout=subprocess.PIPE)
	out = ping.communicate()

	avg_ping = re.search('mdev = \d+.\d+\/(\d+.\d+)\/', str(out))

	if avg_ping:
		return avg_ping.group(1)
	else:
		return "err"

if __name__ == "__main__":
	vm_id = sys.argv[1]
	print get_average_ping(get_vm_ip(vm_id))
