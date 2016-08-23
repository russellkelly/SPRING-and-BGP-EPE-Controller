#!/usr/bin/env python

import socket
from sys import stdout
from sys import stdin
from time import sleep
from jnpr.junos import Device
from lxml import etree
import re
import os
import copy
import re
import subprocess
import signal
import os
import yaml

labelmap = {}
ConfiguredPeerList = {}
PeerToASBRMap = {}
serviceroutes = dict()
serviceroutesold = dict()


def InitialPeerCheck():
	loadlabels()
	loadPeerToASBRMap()
	loadserviceroutes()
	ConfiguredPeerList = ReturnPeerList()
	for i in range(0,len(ConfiguredPeerList.keys())):
		if ConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys():
			return i
		else:
			while ConfiguredPeerList['peer_address'+ str(i)] not in labelmap.keys():
				loadlabels()
				loadPeerToASBRMap()
				loadserviceroutes()
				ConfiguredPeerList = ReturnPeerList()
				if ConfiguredPeerList['peer_address'+ str(i)] not in labelmap.keys() and i == int(len(ConfiguredPeerList) - 1):
					stdout.write('\n=========================================================================\n\n'"Man you ain't got nuthing going on no-how..."'\n'"Lets just keep rolling until you sort this out......")
					stdout.write('\nStart a Global EPE Peer, Bro.....''\n''Or configure another in the Global Configured Peer List File ........''\nIn "ConfiguredEPEPeerList"\n\n\n=========================================================================\n\n\n')
					stdout.flush()
					sleep(2)
					i = 0
					continue
				elif ConfiguredPeerList['peer_address'+ str(i)] not in labelmap.keys() and  i < int(len(ConfiguredPeerList.keys()) - 1):
					i += 1
					continue
				elif i == None:
					i += 1
					continue
				else:
					return i


def check_and_add_route():
	global serviceroutes
	global serviceroutesold
#Load the labels, the service routes, peers and ASBR Mappings
	loadlabels()
	loadPeerToASBRMap()
	loadserviceroutes()
	ConfiguredPeerList = {}
	ConfiguredPeerList = ReturnPeerList()
	i = InitialPeerCheck()
	CurrentPeer = 0
	while ConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys():
		for i in range(0,len(ConfiguredPeerList.keys())):
			if ConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys() and labelmap[ConfiguredPeerList['peer_address'+ str(i)]] is not '0' or None or 0:
				print('\n====================================================================================================\n\n''Here is the pertinent run-time information\n')
				print(labelmap)
				print(serviceroutes)
				print(ConfiguredPeerList)
				print('\n====================================================================================================\n\n')	
				print ('\n=================================================================================\n\n' 'Using this EPE Peer Currently ' + str(ConfiguredPeerList['peer_address'+ str(i)]) + ' address!!! --->> LABEL:' +str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]])+ '\n')
				servicerouteslist = [y for x in serviceroutes.values() for y in x]
				servicerouteslistold = [y for x in serviceroutesold.values() for y in x]
				if len(servicerouteslistold) == len(servicerouteslist) and cmp(serviceroutes, serviceroutesold) == 0 and CurrentPeer == ConfiguredPeerList['peer_address'+ str(i)]:
					print("No Change in the Route Table, still using Peer "  + str(ConfiguredPeerList['peer_address'+ str(i)]) +  "\nOn Egress ASBR "+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' with label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]]) + ']')
					pass
				elif CurrentPeer != ConfiguredPeerList['peer_address'+ str(i)]:
					v = 0
					print("Advertising all current routes "'\n')
					print("Current Prefixes Are: ")
					for route in servicerouteslist:
						print(str(route) + ' ')
					print('\n')	
					for route in servicerouteslist:
						stdout.write('announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]]) + ']''\n')
						stdout.flush()	
						v += 1	
				elif len(servicerouteslistold) == 0 and len(servicerouteslist) >= 0:
					v = 0
					print("Advertising the following newly learned routes from Egress ASBR's: ")
					for route in servicerouteslist:
						if route not in servicerouteslistold:
							print(str(route) +' ')
						print('\n')	
						if route not in servicerouteslistold:
							stdout.write('announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]]) + ']''\n')
							stdout.flush()		
						v += 1	
				elif len(servicerouteslistold) >= len(servicerouteslist):
					v = 0
					print("Removing the following routes no longer Advertised by Egress ASBR's: ")
					for route in servicerouteslistold:
						if route not in servicerouteslist:
							print(str(route) +' ')
						print('\n')
						if route not in servicerouteslist:
							stdout.write('withdraw route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [800000]''\n')
							stdout.flush()	
						v += 1
				elif len(servicerouteslistold) <= len(servicerouteslist):
					v = 0
					print("Advertising the following newly learned routes from Egress ASBR's: ")
					for route in servicerouteslist:
						if route not in servicerouteslistold:
							print(str(route) +' ')
						print('\n')
						if route not in servicerouteslistold:
							stdout.write('announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]]) + ']''\n')
							stdout.flush()	
						v += 1
				print('\n\n=================================================================================\n\n\n')
				stdout.flush()
				CurrentPeer = ConfiguredPeerList['peer_address'+ str(i)]
				loadlabels()
				loadPeerToASBRMap()
				loadserviceroutes()
				sleep(5)
				break
			elif ConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys() and labelmap[ConfiguredPeerList['peer_address'+ str(i)]] == '0' and i < int(len(ConfiguredPeerList.keys()) - 1):
				i += 1
			elif i < int(len(ConfiguredPeerList.keys()) - 1):
				i += 1
			else:
				servicerouteslist = [y for x in serviceroutes.values() for y in x]
				stdout.write('\n========================================================================================\n\n			All defined EPE Peers Are Idle.\n			Lets just remove the EPE Routes\n\n')
				v = 0
				for route in servicerouteslist:
					stdout.write('withdraw route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [800000]''\n')
					v += 1	
				stdout.write('\n\n========================================================================================\n\n\n')
				stdout.flush()
				i = 0
				sleep(5)
				CurrentPeer = 0
				check_and_add_route()



def ReturnPeerList():
	script_dir = os.path.dirname(__file__)
	rel_path = "RuntimeVariables.yaml"
	abs_file_path = os.path.join(script_dir, rel_path)
	f = open(abs_file_path,'r')
	RuntimeVariables = yaml.load(f.read())
	ConfiguredPeerList = copy.deepcopy(RuntimeVariables['ConfiguredPeerList'])
	f.close()
	return ConfiguredPeerList

	
def loadPeerToASBRMap():
	global PeerToASBRMap
	script_dir = os.path.dirname(__file__)
	rel_path = "PeerToASBRMapping"
	abs_file_path = os.path.join(script_dir, rel_path)
	g=open(abs_file_path, "r")
	if PeerToASBRMap == {}:
		g.close()
		sleep(2)
		g=open(abs_file_path, "r")
		for line in g:
			x = line.split(":")
			a = x[0]
			d = len(a)-3
			a = a[0:d]
			b = x[1]
			c = len(b)-1
			b = b[0:c]
			try:
				PeerToASBRMap[a].append(b)
			except KeyError:
				PeerToASBRMap[a] = [b]
		g.close()
		check_and_add_route()
	else:
		PeerToASBRMap = {}
		for line in g:
			x = line.split(":")
			a = x[0]
			d = len(a)-3
			a = a[0:d]
			b = x[1]
			c = len(b)-1
			b = b[0:c]
			try:
				PeerToASBRMap[a].append(b)
			except KeyError:
				PeerToASBRMap[a] = [b]
		g.close()
	
	
def loadlabels():
	script_dir = os.path.dirname(__file__)
	rel_path = "PeerToLabelMapping"
	abs_file_path = os.path.join(script_dir, rel_path)
	f=open(abs_file_path, "r")
	if labelmap == {}:
		f.close()
		sleep(2)
		f=open(abs_file_path, "r")
		for line in f:
			x = line.split(":")
			a = x[0]
			d = len(a)-3
			a = a[0:d]
			b = x[1]
			c = len(b)-2
			b = b[1:c]
			labelmap[a] = b
		f.close()
		check_and_add_route()
	else:
		f=open(abs_file_path, "r")
		for line in f:
			x = line.split(":")
			a = x[0]
			d = len(a)-3
			a = a[0:d]
			b = x[1]
			c = len(b)-2
			b = b[1:c]
			labelmap[a] = b
		f.close()
	
def loadserviceroutes():
	global serviceroutesold
	global serviceroutes
	script_dir = os.path.dirname(__file__)
	rel_path = "ServicePrefixes"
	abs_file_path = os.path.join(script_dir, rel_path)
	g=open(abs_file_path, "r")
	if serviceroutes == {}:
		g.close()
		sleep(2)
		g=open(abs_file_path, "r")
		for line in g:
			x = line.split(":")
			a = x[0]
			b = x[1]
			c = len(b)-1
			b = b[0:c]
			try:
				serviceroutes[a].append(b)
			except KeyError:
				serviceroutes[a] = [b]
		g.close()
		return serviceroutes
		check_and_add_route()
	else:
		serviceroutesold = copy.deepcopy(serviceroutes)
		serviceroutes = {}
		for line in g:
			x = line.split(":")
			a = x[0]
			b = x[1]
			c = len(b)-1
			b = b[0:c]
			try:
				serviceroutes[a].append(b)
			except KeyError:
				serviceroutes[a] = [b]
		g.close()
		return serviceroutes
		return serviceroutesold



def main():
	check_and_add_route()


if __name__ == "__main__":
   main()

				