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
from test import *
from ping_vm import *

with open("userauth","r") as authfile:
	auth_string = authfile.read().replace("\n","")

hostname = "dev-hn1.nubes.rl.ac.uk"
server = xmlrpclib.ServerProxy("https://"+hostname+"/RPC2")
response = server.one.user.login(auth_string, "testgroup", "dontleaveblank", 1000)
session_id = response[1]
one_auth = "testgroup:" + session_id

vm_id = sys.argv[1]

vm_xml = server.one.vmpool.info(one_auth, -1, -1, -1, 3)[1]
vm_pool = ET.fromstring(vm_xml)

template_xml = server.one.templatepool.info(one_auth, -1, -1, -1)[1]
template_pool = ET.fromstring(template_xml)

user_xml = server.one.user.info(one_auth, -1)[1]
user_pool = ET.fromstring(user_xml)

def update_vm_pool():
	vm_xml = server.one.vmpool.info(one_auth, -1, -1, -1, 3)[1]
	vm_pool = ET.fromstring(vm_xml)

	return vm_pool

def delete_vm(vm_id):
	delete = server.one.vm.action(one_auth, "delete", vm_id)[0]

	return delete

def get_vm_ip(vm_id):
	vm_pool = update_vm_pool()

	for vm in vm_pool.findall("VM"):
		if vm_id == int(vm.find("ID").text):
			ip = vm.find("TEMPLATE/NIC/IP").text
			break
		else:
			ip = "unknown"

	return ip

def instantiate_vm(template_id, template_name):
	instantiate = server.one.template.instantiate(one_auth, int(template_id), template_id + "-" + template_name, False, "")

	status = instantiate[0]
	vm_id = instantiate[1]
	error_code = instantiate[2]

	return status, vm_id, error_code

def run():
	for vm_template in template_pool.findall("VMTEMPLATE"):
		template_id = vm_template.find("ID").text
		template_name = vm_template.find("NAME").text

		print time.ctime() + ": Creating template " + template_id + " for " + template_name
		status, vm_id, error_code = instantiate_vm(template_id, template_name)

		if not status:
			print time.ctime() + ": \033[0;31mCouldn't create template " + template_id + "(error " + str(error_code) + ")\033[1;m"
			print time.ctime() + ": \033[0;31m" + vm_id + "\033[1;m"
		else:
			time.sleep(240)

			ip = get_vm_ip(vm_id)
			ping = get_average_ping(ip)
			ssh = ssh_touch(ip)

			send_to_influxdb(ping, "time_to_pingable", ip, template_id, tempalte_name)
			send_to_influxdb(ssh, "time_to_sshable", ip, template_id, template_name)

			delete_vm(vm_id)

			if not delete:
				time.ctime() + ": \033[0;31mCouldn't delete vm " + vm_id + " \033[1;m"

			time.sleep(15)

run()
