#!/usr/bin/env python

import socket
from sys import stdout
from time import sleep
from jnpr.junos import Device
from lxml import etree
import re
import os
import signal
import time
from pprint import pprint
import json
import sys
import traceback



def exit_gracefully(signum, frame):
	# restore the original signal handler as otherwise evil things will happen
	# in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
	signal.signal(signal.SIGINT, original_sigint)
	main()
	# restore the exit gracefully handler here    
	signal.signal(signal.SIGINT, exit_gracefully)

def bgpandimportantapps():
	print ('\n===========================================================================\n\n		All Right Lets Rock & Roll!!\n\n	PRESS CTRL+C TO RETURN TO THIS MENU AT ANY TIME\n\n===========================================================================\n\n')
	os.system("exabgp exabgp-bgp-lu.conf new-exabgp-bgp-label-only.conf")
	
def bgpandveryimportantapps():
	print ('\n===========================================================================\n\n		All Right Lets Rock & Roll!!\n\n	PRESS CTRL+C TO RETURN TO THIS MENU AT ANY TIME\n\n===========================================================================\n\n')
	os.system("exabgp exabgp-bgp-lu.conf new-exabgp-bgp-label-only.conf")

def bgponly():
	print ('\n===========================================================================\n\n		All Right Lets Rock & Roll!!\n\n	PRESS CTRL+C TO RETURN TO THIS MENU AT ANY TIME\n\n===========================================================================\n\n')
	sleep(2)
	os.system("exabgp exabgp-bgp-lu.conf new-exabgp-bgp-label-only.conf")

def sronly():
	print ('\n===========================================================================\n\n		All Right Lets Rock & Roll!!\n\n	PRESS CTRL+C TO RETURN TO THIS MENU AT ANY TIME\n\n===========================================================================\n\n')
	sleep(2)
	os.system("exabgp exabgp-sr-only.conf")

	

def main():
	os.system("pkill -9 exabgp")
	print ("\n\n			THE SPRING & EPE DEMO!!!")
	print ("\n================================================================================================================\n\nPart 1 of the Demo Allows One to TE Traffic in AS65412 Using SPRING S-NID Labels\n\nTraffic From vMX1 & vMX8 is routed to 12.0.0.0/8 Any way you want!!\nIn this part of the Demo Using Postman - Routes are published to the i_ASBR's\n\n================================================================================================================\n")
	
	print ("Press 1 to start Part 1: ")

	print ("\n================================================================================================================\n\nPart 2 of the Demo Is to showcase EPE TE. Defining the BGP-LU Label on the route\n\nTraffic From vMX1 & vMX8 is routed to the dynamically learned BGP service prefixes using the dynamically \nlearnt via BGP-LU !!The controller dynamically updates/removes the service routes and EPE labels and\n updates the egress ESBP NH depending on the EPE peer being used!!\nYou can change the order of these EGRESS ASBR by amending /home/rbutme/ConfiguredEPEPeerList\n\n================================================================================================================\n")
	
	print ("Press 2 to start Part 2: ")
	
	print ("\n=====================================================================================================================\n\nPart 3 of the Demo Engineers Traffic for specific Important Applications prefixes from Both vmx1 and vmx8\n\nThe Important applications' Prefixes need to be defined in the file --> /home/rbutme/ImptApplicationsPrefixes\nPress 3 and then go to a new window and run --> python ImportantApplications.py\n\n=====================================================================================================================\n")
	
	print ("Press 3 to start Part 3: \n")
	
	print ("\n=====================================================================================================================\n\nPart 4 of the Demo Engineers Traffic for specific Very Important Applications prefixes from Both vmx1 and vmx8\n\nThe COMPLETE PATH is Programmed (SPRING S-NID Label Path and the EPE BGP label) for the prefixes\nThe Important applications' Prefixes need to be defined in the file --> /home/rbutme/VeryImptApplicationsPrefixes\nPress 4 and then go to a new window and run --> python VeryImportantApplications.py\n\n=====================================================================================================================\n")
	
	print ("Press 4 to start Part 4: \n")
	print ("\nOr press q (..yes small q) to Quit entire Demo.......\n\n")
	os.system("stty erase '^H'")
	m = raw_input("Make your selection.........:  ")

	
		
	if m == "2":
		bgponly()
		main()
	elif m == "3":
		bgpandimportantapps()
		main()
	elif m == "4":
		bgpandveryimportantapps()
		main()
	elif m == "1":
		sronly()
		main()
	elif m == "q":
		print ("\n\nLater Gators........\n\n\n")
		os.system("pkill -9 exabgp")
		os.system("pkill -9 python")
		sleep(1)
		exit(0)
	else:
		print("\n\n\nCome on!!! 1,2,3,4 or q only.......:  \n\n")
		sleep(1)
		main()


	
if __name__ == "__main__":
	# store the original SIGINT handler
	original_sigint = signal.getsignal(signal.SIGINT)
	signal.signal(signal.SIGINT, exit_gracefully)
	os.system("python getlabelsandserviceprefixes.py &")
	main()


	


sleep(1)

