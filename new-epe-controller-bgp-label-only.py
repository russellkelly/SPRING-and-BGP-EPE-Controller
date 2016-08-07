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

labelmap = {}
ConfiguredPeerList = {}
PeerToASBRMap = {}
serviceroutes = dict()
serviceroutesold = dict()
CurrentPeer = 0



def check_and_add_route():
	global serviceroutes
	global serviceroutesold
	global CurrentPeer
	loadlabels()
	loadPeerToASBRMap()
	loadserviceroutes()
	i = 0
	for i in range(0,len(ConfiguredPeerList.keys())):
		if ConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys() and labelmap[ConfiguredPeerList['peer_address'+ str(i)]] is not '0' or None or 0:
			print('\n====================================================================================================\n\n''Here is the pertinent run-time information\n')
			print(labelmap)
			print(serviceroutes)
			print(ConfiguredPeerList)
			print('\n====================================================================================================\n\n')
			sleep(5)
			while ConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys() and labelmap[ConfiguredPeerList['peer_address'+ str(i)]] is not '0' or None or 0:
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
				check_and_add_route()
		elif ConfiguredPeerList['peer_address'+ str(i)] in labelmap.keys() and labelmap[ConfiguredPeerList['peer_address'+ str(i)]] == '0':
			print('\n====================================================================================================\n\n''Here is the pertinent run-time information\n')
			print(labelmap)
			print(serviceroutes)
			print(ConfiguredPeerList)
			print('\n====================================================================================================\n\n')
			sleep(5)
			for j in range(0,len(ConfiguredPeerList.keys())):
				while ConfiguredPeerList['peer_address'+ str(j)]  in labelmap.keys() and labelmap[ConfiguredPeerList['peer_address'+ str(j)]] != '0':
					print ('\n=================================================================================\n\n' 'Using this EPE Peer Currently ' + str(ConfiguredPeerList['peer_address'+ str(j)]) + ' address!!! --->> LABEL:' +str(labelmap[ConfiguredPeerList['peer_address'+ str(j)]])+ '\n')
					servicerouteslist = [y for x in serviceroutes.values() for y in x]
					servicerouteslistold = [y for x in serviceroutesold.values() for y in x]
					if len(servicerouteslistold) == len(servicerouteslist) and cmp(serviceroutes, serviceroutesold) == 0 and CurrentPeer == ConfiguredPeerList['peer_address'+ str(j)]:
						print("No Change in the Route Table, still using Peer "  + str(ConfiguredPeerList['peer_address'+ str(j)]) +  "\nOn Egress ASBR "+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(j)])][0])+' with label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(j)]]) + ']')
						pass
					elif CurrentPeer != ConfiguredPeerList['peer_address'+ str(j)] :
						servicerouteslist = [y for x in serviceroutes.values() for y in x]
						servicerouteslistold = [y for x in serviceroutesold.values() for y in x]
						print("Advertising all current routes "'\n')
						print("Current Prefixes Are: ")
						v = 0
						for route in servicerouteslist:
							print(str(route) +' ')
						print('\n')
						for route in servicerouteslist:
							stdout.write('announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(j)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(j)]]) + ']''\n')
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
								stdout.write('announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(j)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(j)]]) + ']''\n')
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
								stdout.write('withdraw route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(j)])][0])+' label [800000]''\n')
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
								stdout.write('announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(j)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(j)]]) + ']''\n')
								stdout.flush()	
							v += 1
					print('\n\n=================================================================================\n\n\n')
					stdout.flush()
					CurrentPeer = ConfiguredPeerList['peer_address'+ str(j)]
					check_and_add_route()
			else:
				servicerouteslist = [y for x in serviceroutes.values() for y in x]
				stdout.write('\n========================================================================================\n\n			All defined EPE Peers Are Idle.\n			Lets just remove the EPE Routes\n\n')
				v = 0
				for route in servicerouteslist:
					stdout.write('withdraw route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [800000]''\n')
					v += 1	
				stdout.write('\n\n========================================================================================\n\n\n')
				stdout.flush()
				sleep(5)
				check_and_add_route()
		elif ConfiguredPeerList['peer_address'+ str(i)] not in labelmap.keys():
			i += 1
			sleep(5)
			if i == len(ConfiguredPeerList):
				stdout.write('\n=========================================================================\n\n'"Man you ain't got nuthing going on no-how..."'\n'"Lets just keep rolling until you sort this out......")
				stdout.write('\nStart a Global EPE Peer, Bro.....''\n''Or configure another in the Global Configured Peer List File ........''\nIn "/home/rbutme/ConfiguredEPEPeerList"\n\n\n=========================================================================\n\n\n')
				stdout.flush()
				check_and_add_route()
		else:
			sleep(1)





	

def announce_withdraw_routes(i):
	global serviceroutesold
	global serviceroutes
	servicerouteslist = [y for x in serviceroutes.values() for y in x]
	servicerouteslistold = [y for x in serviceroutesold.values() for y in x]
	print ('\n=================================================================================\n\n' 'Using this EPE Peer Currently ' + str(ConfiguredPeerList['peer_address'+ str(i)]) + ' address!!! --->> LABEL:' +str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]])+ '\n')
	if len(servicerouteslistold) == 0 and len(servicerouteslist) >= 0:
		v = 0
		print("Advertising the following newly learned routes from Egress ASBR's: ")
		for route in servicerouteslist:
			if route not in servicerouteslistold:
				print(str(route) +' ')
			print('\n')	
			if route not in servicerouteslistold:
				r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]]) + ']''\n')})
				print('announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]]) + ']''\n')
			v += 1	
	elif len(servicerouteslistold) >= len(servicerouteslist):
		v = 0
		print("Removing the following routes no longer Advertised by Egress ASBR's: ")
		for route in servicerouteslistold:
			if route not in servicerouteslist:
				print(str(route) +' ')
			print('\n')
			if route not in servicerouteslist:
				r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'withdraw route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [800000]''\n')})
				print('withdraw route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [800000]''\n')
			v += 1
	elif len(servicerouteslistold) <= len(servicerouteslist):
		v = 0
		print("Advertising the following newly learned routes from Egress ASBR's: ")
		for route in servicerouteslist:
			if route not in servicerouteslistold:
				print(str(route) +' ')
			print('\n')
			if route not in servicerouteslistold:
				r = requests.post('http://10.164.1.177:5000', files={'command': (None, 'announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' label [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]]) + ']''\n')})
				print('announce route ' + str(route) +' next-hop '+ str(PeerToASBRMap[str(ConfiguredPeerList['peer_address'+ str(i)])][0])+' [' + str(labelmap[ConfiguredPeerList['peer_address'+ str(i)]]) + ']''\n')
			v += 1
	print('\n\n=================================================================================\n\n\n')
	check_and_add_route()




def loadconfiguredEPEPeers():
	f=open("/home/rbutme/ConfiguredEPEPeerList", "r")
	for line in f:
		x = line.split(":")
		a = x[0]
		b = x[1]
		c = len(b)-1
		b = b[0:c] + '/32'
		ConfiguredPeerList[a] = b
	f.close()
	
	
def loadPeerToASBRMap():
	global PeerToASBRMap
	g=open("/home/rbutme/PeerToASBRMapping", "r")
	if PeerToASBRMap == {}:
		g.close()
		sleep(2)
		g=open("/home/rbutme/PeerToASBRMapping", "r")
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
		check_and_add_route()
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
	global countlabel
	f=open("/home/rbutme/PeerToLabelMapping", "r")
	if labelmap == {}:
		f.close()
		sleep(2)
		f=open("/home/rbutme/PeerToLabelMapping", "r")
		for line in f:
			x = line.split(":")
			a = x[0]
			b = x[1]
			c = len(b)-2
			b = b[1:c]
			labelmap[a] = b
		f.close()
		check_and_add_route()
	else:
		f=open("/home/rbutme/PeerToLabelMapping", "r")
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
	g=open("/home/rbutme/ServicePrefixes", "r")
	if serviceroutes == {}:
		g.close()
		sleep(2)
		g=open("/home/rbutme/ServicePrefixes", "r")
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
	loadconfiguredEPEPeers()
	check_and_add_route()


if __name__ == "__main__":
   main()

				
	