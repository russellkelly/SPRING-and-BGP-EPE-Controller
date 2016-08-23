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
import subprocess
import signal
import requests
from netaddr import *
		

labelmap = {}
ImptApplicationsConfiguredPeerList = {}
PeerToASBRMap = {}
ActiveImptApplicationsPrefixesOld = []
ActiveImptApplicationsPrefixes = []	
serviceroutes = dict()
serviceroutesold = dict()
UserEnteredInformation = dict()
VeryImportantApplicationsSRPaths = dict()
VeryImportantApplicationsSRPathsOld = {}

CurrentPeer = 0
CurrentIValue = 0



def exit_gracefully(signum, frame):
	global CurrentIValue
	# restore the original signal handler as otherwise evil things will happen
	# in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
	signal.signal(signal.SIGINT, original_sigint)
	print('\n========================================================================================\n\n			OK Bye.....Lets just remove the EPE Routes\n\n')
	v = 0
	for route in ActiveImptApplicationsPrefixes:
		r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'withdraw route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(CurrentIValue)])][0])+' label [800000]')})
		sleep(.2) # Give the API time to process - avoid the HTTP socket error(Max Retries exceeded with url)
		print('withdraw route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(CurrentIValue)])][0])+' label [800000]')
		v += 1	
	print('\n\n========================================================================================\n\n\n')
	sleep(1)
	main()
	# restore the exit gracefully handler here    
	signal.signal(signal.SIGINT, exit_gracefully)
	

def add_more_specific_routes():
	# In this program we identify a subset of the active service prefixes for Important Applications (Defined by Subnet) and advertise them to VMX1 only to a set of EPE Peers.  If these peers go down we just fall back to the
	# default EPE routing in the BGP EPE program
	
	global serviceroutes
	global serviceroutesold
	global CurrentPeer
	global ActiveImptApplicationsPrefixes
	global ActiveImptApplicationsPrefixesOld
	global VeryImportantApplicationsSRPaths
	global VeryImportantApplicationsSRPathsOld
	global CurrentIValue

	#Load the labels, the service routes, peers and ASBR Mappings
	loadlabels()
	loadVeryImportantApplicationsSRPaths()
	loadserviceroutes()
	loadPeerToASBRMap()
	loadconfiguredEPEPeers()
	FindActiveServicePrefixes()
	
	
	# OK Lets run the program to advertise this stuff
	CurrentPeer = 0
	i = 0
	while ImptApplicationsConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys():
		for i in range(0,len(ImptApplicationsConfiguredPeerList.keys())):
			if ImptApplicationsConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys() and labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]] is not '0' or None or 0:
				print('\n====================================================================================================\n\n''Here is the pertinent Important Application run-time information\n')
				print(ActiveImptApplicationsPrefixes)
				print(ImptApplicationsConfiguredPeerList)
				print("Here is the SR Path we're using: " + str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) +']')
				print('\n====================================================================================================\n\n')
				print ('\n====================================================================================================\n\n' 'Saving the Label (BGP-LU) for  ' + str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]) + ' address!!! --->> LABEL:' +str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]])+ '\n')
				servicerouteslist = [y for x in serviceroutes.values() for y in x]
				servicerouteslistold = [y for x in serviceroutesold.values() for y in x]
				if len(ActiveImptApplicationsPrefixesOld) == len(ActiveImptApplicationsPrefixes) and cmp(ActiveImptApplicationsPrefixes, ActiveImptApplicationsPrefixesOld) == 0 and CurrentPeer == ImptApplicationsConfiguredPeerList['peer_address'+ str(i)] and VeryImportantApplicationsSRPathsOld == VeryImportantApplicationsSRPaths:
					print("No Change in the Route Table, still using Peer "  + str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]) +  "\nOn Egress ASBR "+ str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])+' with label [' + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')
					pass
				elif CurrentPeer != ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]:
					v = 0
					print("Advertising all current Important Applications' routes For new EPE Peer's ASBR"'\n')
					print("Current Prefixes Are: ")
					for route in ActiveImptApplicationsPrefixes:
						print(str(route) + ' ')
					for route in ActiveImptApplicationsPrefixes:
						r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'announce route ' + str(route) +' next-hop 172.20.2.2 label '+ str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')})
						sleep(.2) # Give the API time to process - avoid the HTTP socket error(Max Retries exceeded with url)
						print('announce route ' + str(route) +' next-hop 172.20.2.2 label '+ str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')
						v += 1
				elif VeryImportantApplicationsSRPathsOld != VeryImportantApplicationsSRPaths:
					v = 0
					print("Advertising all current Important Applications' routes For new EPE Peer's ASBR"'\n')
					print("Current Prefixes Are: ")
					for route in ActiveImptApplicationsPrefixes:
						print(str(route) + ' ')
					for route in ActiveImptApplicationsPrefixes:
						r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'announce route ' + str(route) +' next-hop 172.20.2.2 label '+ str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')})
						sleep(.2) # Give the API time to process - avoid the HTTP socket error(Max Retries exceeded with url)
						print('announce route ' + str(route) +' next-hop 172.20.2.2 label '+ str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')
						v += 1				
				elif len(ActiveImptApplicationsPrefixesOld) == 0 and len(ActiveImptApplicationsPrefixes) >= 0:
					v = 0
					print("Advertising the following newly learned Important Application routes from Egress ASBR: ")
					for route in ActiveImptApplicationsPrefixes:
						if route not in ActiveImptApplicationsPrefixesOld:
							print(str(route) +' ')
						if route not in ActiveImptApplicationsPrefixesOld:
							r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'announce route ' + str(route) +' next-hop 172.20.2.2 label '+ str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')})
							sleep(.2) # Give the API time to process - avoid the HTTP socket error(Max Retries exceeded with url)
							print('announce route ' + str(route) +' next-hop 172.20.2.2 label '+ str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')
						v += 1
				elif len(ActiveImptApplicationsPrefixesOld) >= len(ActiveImptApplicationsPrefixes):
					v = 0
					print("Removing the following Important Application routes no longer Advertised by Egress ASBR's: ")
					for route in ActiveImptApplicationsPrefixesOld:
						if route not in ActiveImptApplicationsPrefixes:
							print(str(route) +' ')
						if route not in ActiveImptApplicationsPrefixes:
							r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'withdraw route ' + str(route) +' next-hop 172.20.2.2 label [800000]')})
							print('withdraw route ' + str(route) +' next-hop 172.20.2.2 label [800000]')
							sleep(.2) # Give the API time to process - avoid the HTTP socket error(Max Retries exceeded with url)
						v += 1
				elif len(ActiveImptApplicationsPrefixesOld) <= len(ActiveImptApplicationsPrefixes):
					v = 0
					print("Advertising the following newly learned Important Applications' routes from Egress ASBR's: ")
					for route in ActiveImptApplicationsPrefixes:
						if route not in ActiveImptApplicationsPrefixesOld:
							print(str(route) +'\n')
						if route not in ActiveImptApplicationsPrefixesOld:
							r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'announce route ' + str(route) +' next-hop 172.20.2.2 label '+ str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')})
							sleep(.2) # Give the API time to process - avoid the HTTP socket error(Max Retries exceeded with url)
							print('announce route ' + str(route) +' next-hop 172.20.2.2 label '+ str(VeryImportantApplicationsSRPaths[str(PeerToASBRMap[str(ImptApplicationsConfiguredPeerList['peer_address'+ str(i)])][0])]) + str(labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]]) + ']')
						v += 1
				print('\n\n================================================================================================\n\n\n')
				CurrentPeer = ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]
				CurrentIValue = i
				VeryImportantApplicationsSRPathsOld = copy.deepcopy(VeryImportantApplicationsSRPaths)
				loadlabels()
				loadVeryImportantApplicationsSRPaths()
				loadserviceroutes()
				loadPeerToASBRMap()
				loadconfiguredEPEPeers()
				FindActiveServicePrefixes()
				sleep(2)
				break
			elif ImptApplicationsConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys() and labelmap[ImptApplicationsConfiguredPeerList['peer_address'+ str(i)]] == '0' and i < int(len(ImptApplicationsConfiguredPeerList.keys()) - 1):
				i += 1

			elif ImptApplicationsConfiguredPeerList['peer_address'+ str(i)] not in labelmap.keys():
				i += 1
				sleep(5)
				if i == len(ImptApplicationsConfiguredPeerList):
					print('\n========================================================================================\n\n'"Man you ain't got nuthing going on no-how..."'\n'"Lets just keep rolling until you sort this out......")
					print('\n''Start a configured EPE Peer for this Customer, Bro.....''\n''Or start again and Enter Correctly........''\n\n\n========================================================================================\n\n\n')
					VeryImportantApplicationsSRPathsOld = {}
					FindActiveServicePrefixes()
					add_more_specific_routes()
			else:
				print('\n========================================================================================\n\n		All defined EPE Peers For Important Applications Are Idle.\n			Lets just remove the EPE Routes\n\n')
				v = 0
				for route in ActiveImptApplicationsPrefixes:
					r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'withdraw route ' + str(route) +' next-hop 172.20.2.2 label [800000]')})
					print('withdraw route ' + str(route) +' next-hop 172.20.2.2 label [800000]')
					sleep(.2) # Give the API time to process - avoid the HTTP socket error(Max Retries exceeded with url)
					v += 1	
				print('\n\n========================================================================================\n\n\n')
				CurrentIValue = i
				VeryImportantApplicationsSRPathsOld = {}
				loadlabels()
				loadVeryImportantApplicationsSRPaths()
				loadserviceroutes()
				loadPeerToASBRMap()
				loadconfiguredEPEPeers()
				FindActiveServicePrefixes()
				i = 0
				sleep(5)




def loadconfiguredEPEPeers():
	script_dir = os.path.dirname(__file__)
	rel_path = "VeryImptApplicationsPeers"
	abs_file_path = os.path.join(script_dir, rel_path)
	f = open(abs_file_path,'r')
	for line in f:
		x = line.split(":")
		a = x[0]
		b = x[1]
		c = len(b)-1
		b = b[0:c] + '/32'
		ImptApplicationsConfiguredPeerList[a] = b
	f.close()


# Find the routes in Important Applications file that are actually active in a service prefix supernet
	
def FindActiveServicePrefixes():
	global ActiveImptApplicationsPrefixesOld
	global ActiveImptApplicationsPrefixes
	global serviceroutes
	servicerouteslist = [y for x in serviceroutes.values() for y in x]
	script_dir = os.path.dirname(__file__)
	rel_path = "VeryImptApplicationsPrefixes"
	abs_file_path = os.path.join(script_dir, rel_path)
	f = open(abs_file_path,'r')
	ImptApplicationsPrefixes = [line.strip() for line in f]		
	ImptApplicationsIPSet = IPSet(ImptApplicationsPrefixes)
	ImptApplicationsIPNetwork = list(ImptApplicationsIPSet.iter_cidrs())
	serviceIPSet = IPSet(servicerouteslist)
	serviceIPNetwork = list(serviceIPSet.iter_cidrs())
	ActiveImptApplicationsPrefixesOld = copy.deepcopy(ActiveImptApplicationsPrefixes)
	f.close()
	
	# Result Stored in 	ActiveimportantPrefixes
	
	ActiveImptApplicationsPrefixes = []	
	v = 0	
	for line in ImptApplicationsIPNetwork:
		if ImptApplicationsIPNetwork[v] in serviceIPSet:
			ActiveImptApplicationsPrefixes.append(str(ImptApplicationsIPNetwork[v]))
		else:	
			pass
		v +=1	


#Load the SR Paths in the file VeryImportantApplicationsSRPaths (See file for Format)


def loadVeryImportantApplicationsSRPaths():
	global VeryImportantApplicationsSRPaths
	script_dir = os.path.dirname(__file__)
	rel_path = "VeryImportantApplicationsSRPaths"
	abs_file_path = os.path.join(script_dir, rel_path)
	with open(abs_file_path) as f_in:
		 data = list(line for line in (l.strip().split() for l in f_in) if line)
	for d in data[0::1]:
		h = d[0].split('=', 1)[-1]
		d[0] = d[0].replace(d[0],h)
	keys = []
	for line in data[0::2]:
		temp  =  ''.join(line)
		keys.append(temp)
	values = []	
	for line in data[1::2]:
		temp1  =  ' '.join(line)
		temp2 = "[" + temp1 +' '
		values.append(temp2)
	i = iter(keys)
	j = iter(values)
	k = list(zip(i, j))
	VeryImportantApplicationsSRPaths = {}
	for (x,y) in k:
		VeryImportantApplicationsSRPaths[x] = y



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
			b = x[1]
			c = len(b)-1
			b = b[0:c]
			try:
				PeerToASBRMap[a].append(b)
			except KeyError:
				PeerToASBRMap[a] = [b]
		g.close()
		add_more_specific_routes()
	else:
		PeerToASBRMap = {}
		for line in g:
			x = line.split(":")
			a = x[0]
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
			b = x[1]
			c = len(b)-2
			b = b[1:c]
			labelmap[a] = b
		f.close()
		add_more_specific_routes()
	else:
		f=open(abs_file_path, "r")
		for line in f:
			x = line.split(":")
			a = x[0]
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
		add_more_specific_routes()
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
	global CurrentIValue
	script_dir = os.path.dirname(__file__)
	rel_path = "VeryImptApplicationsPeers"
	abs_file_path = os.path.join(script_dir, rel_path)
	f = open(abs_file_path,'w') #Clear the file or Create the file if it doesn't exist
	f.close()
	loadconfiguredEPEPeers()
	CurrentIValue = 0
	print ("\n\n			WELCOME TO THE VERY IMPORTANT APPLICATION PART OF THE EPE DEMO.....!!!\n\n")
	sleep(1)
	print ("\n====================================================================================================\n\nHave you started option 4 in the EPE demo program!!!???.............  \n\nIf not, open a new window and run 'python new-epe-demo.py' and select option 4......\n\n====================================================================================================\n\n")
	print ("\nPress 1 to start this Part of the demo.......\n\n")
	print ("\nOr press q (..yes small q) to Quit this program.......\n\n")
	os.system("stty erase '^H'")
	m = raw_input("Make your selection.........:  ")
	if m == "1":
		print ('\n====================================================================================================\n\n	All Right Lets Get the Information for the Two EPE Peers For This Part!!\n\nNote:  We can take as many peers as there are active! We have just limited to 2 for this test.....\n')
		print ('Make Sure you have added your Important Applications specific prefixes to the file:\n''......"VeryImptApplicationsPrefixes".....!!!\n\n====================================================================================================\n\n')
		pass
	elif m == "q":
		print ("\n\nLater Gators........\n\n\n")
		sleep(1)
		exit(0)
	else:
		print("\n\n\nCome on!!! 1,2,3 or q only.......:  \n\n")
		sleep(0.5)
		main()
	script_dir = os.path.dirname(__file__)
	rel_path = "PeerToASBRMapping"
	abs_file_path = os.path.join(script_dir, rel_path)
	g=open(abs_file_path, "r")
	PeerToASBRMap = {}
	for line in g:
		x = line.split(":")
		a = x[0]
		b = x[1]
		d = len(a)-3
		a = a[0:d]
		c = len(b)-1
		b = b[0:c]
		try:
			PeerToASBRMap[a].append(b)
		except KeyError:
			PeerToASBRMap[a] = [b]
	g.close()	
	print("Your choice of Active EPE Enabled External Peers are:......\n")
	print(str(PeerToASBRMap.keys()))
	os.system("stty erase '^H'")
	n="peer_address0"
	m=raw_input("\nEnter the IP Address of the Primary Peer for your VERY Important Applications: ")
	UserEnteredInformation[n]=m
	n1="peer_address1"
	m1=raw_input("\nEnter the IP Address of the Secondary Peer for your VERY Important Applications: ")
	UserEnteredInformation[n1]=m1
	script_dir = os.path.dirname(__file__)
	rel_path = "VeryImptApplicationsPeers"
	abs_file_path = os.path.join(script_dir, rel_path)
	with open(abs_file_path, 'w') as f:
		for key, value in UserEnteredInformation.items():
			f.write('%s:%s\n' % (key, value))
	f.close()
	sleep(2)
	print ('\n===========================================================================\n\n		All Right Lets Rock & Roll!!\n\n	PRESS CTRL+C TO RETURN TO THIS MENU AT ANY TIME\n\n===========================================================================\n\n')
	print("starting........")
	add_more_specific_routes()
	


if __name__ == "__main__":
	original_sigint = signal.getsignal(signal.SIGINT)
	signal.signal(signal.SIGINT, exit_gracefully)
	main()

				






				

				

				
		
