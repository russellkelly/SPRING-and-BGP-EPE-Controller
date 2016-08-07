#!/usr/bin/env python


import time
from pprint import pprint
import json
import sys

def follow(thefile):
    thefile.seek(0,2)      # Go to the end of the file
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)    # Sleep briefly
            continue
        yield line


		

def main():
	f = open('PeerToLabelMapping','w')
	g = open('ServicePrefixes','w')
	h = open('bgplog.json','w')
	f.close()
	g.close()
	h.close()
	logfile = open('bgplog.json')        
	logline = follow(logfile)
	for line in logline:
		data = json.loads(line)
		#pprint(data)
		if "neighbor" in line:
			message_update_type_keys = data['neighbor']['message']['update'].keys()
			#pprint(message_update_type_keys)
			for update_type in message_update_type_keys:
				ipv4_type_keys = data['neighbor']['message']['update'][update_type].keys()
			#pprint(ipv4_type_keys)
		else:
			main()
		if "ipv4 unicast" in ipv4_type_keys and "announce" in message_update_type_keys:
			service_prefix_keys = data['neighbor']['message']['update']['announce']['ipv4 unicast'].keys()
			i = 0
			for member in service_prefix_keys:
				#pprint(member)
				prefixlist = data['neighbor']['message']['update']['announce']['ipv4 unicast'][member].keys()
				#pprint(prefixlist)
				for prefix in prefixlist:
					#pprint(prefix)
					if str(member) in open('ServicePrefixes').read():
						f = open('ServicePrefixes', "r+")
						d = f.readlines()
						f.seek(0)
						for line in d:
							if str(member) and str(prefix) not in line:
								f.write(line)
						f.truncate()
						f.close()
						f = open('ServicePrefixes','a')
						f.write(str(member) + ':' + str(prefix)+'\n')
						f.close()
					else:	
						f = open('ServicePrefixes','a')
						f.write(str(member) + ':' + str(prefix)+'\n') # python will convert \n to os.linesep
						f.close()		
			i =+ 1
		elif "ipv4 unicast" in ipv4_type_keys and "withdraw" in message_update_type_keys:
				#print('I got here to withdraw')
				prefixlist = data['neighbor']['message']['update']['withdraw']['ipv4 unicast'].keys()
				for prefix in prefixlist:
					#pprint(prefix)
					if str(member) in open('ServicePrefixes').read():
						f = open('ServicePrefixes', "r+")
						d = f.readlines()
						f.seek(0)
						for line in d:
							if str(prefix) not in line:
								f.write(line)
						f.truncate()
						f.close()
					else:	
						f = open('ServicePrefixes','a')
						f.write(str(member) + ':' + str(prefix)+'\n') # python will convert \n to os.linesep
						f.close()		
				i =+ 1
		elif "ipv4 nlri-mpls" in ipv4_type_keys and "announce" in message_update_type_keys:
			neighbor_message_update_announce_keys = data["neighbor"]["message"]["update"]["announce"]['ipv4 nlri-mpls'].keys()
			i= 0
			for announce_peer in neighbor_message_update_announce_keys:
				#pprint(announce_peer)
				external_peers = data["neighbor"]["message"]["update"]["announce"]['ipv4 nlri-mpls'][announce_peer].keys()
				i = 0
				for external_peer_ip in external_peers:
						#pprint(external_peer_ip)
						if str(external_peer_ip) in open('PeerToASBRMapping').read():
							g = open('PeerToASBRMapping', "r+")
							d = g.readlines()
							g.seek(0)
							for line in d:
								if str(external_peer_ip) not in line:
									g.write(line)
							g.truncate()
							g.close()
							g = open('PeerToASBRMapping','a')
							g.write(str(external_peer_ip) + ':' + str(announce_peer)+'\n') # python will convert \n to os.linesep
							g.close()
						else:	
							g = open('PeerToASBRMapping','a')
							g.write(str(external_peer_ip) + ':' + str(announce_peer)+'\n') # python will convert \n to os.linesep
							g.close()		
						label = data["neighbor"]["message"]["update"]["announce"]['ipv4 nlri-mpls'][announce_peer][external_peer_ip]['label']
						#pprint(label)
						if str(external_peer_ip) in open('PeerToLabelMapping').read():
							f = open('PeerToLabelMapping', "r+")
							d = f.readlines()
							f.seek(0)
							for line in d:
								if str(external_peer_ip) not in line:
									f.write(line)
							f.truncate()
							f.close()
							f = open('PeerToLabelMapping','a')
							f.write(str(external_peer_ip) + ':' + str(label)+'\n') 
							f.close()
						else:	
							f = open('PeerToLabelMapping','a')
							f.write(str(external_peer_ip) + ':' + str(label)+'\n') # python will convert \n to os.linesep
							f.close()		
						i =+ 1		
				i =+ 1
		elif "ipv4 nlri-mpls" in ipv4_type_keys and "withdraw" in message_update_type_keys:
			neighbor_message_update_withdraw_keys = data["neighbor"]["message"]["update"]["withdraw"]['ipv4 nlri-mpls'].keys()
			i= 0
			for withdraw_peer in neighbor_message_update_withdraw_keys:
				external_peer_ip = data["neighbor"]["message"]["update"]["withdraw"]['ipv4 nlri-mpls'].keys()
				i = 0
				for external_peer_ip in external_peer_ip:
						#pprint(external_peer_ip)
						label = (data["neighbor"]["message"]["update"]["withdraw"]['ipv4 nlri-mpls'][external_peer_ip]['label'])
						#pprint(label)
						if str(external_peer_ip) in open('PeerToLabelMapping').read():
							f = open('PeerToLabelMapping', "r+")
							d = f.readlines()
							f.seek(0)
							for line in d:
								if str(external_peer_ip) not in line:
									f.write(line)
							f.truncate()
							f.close()
							f = open('PeerToLabelMapping','a')
							f.write(str(external_peer_ip) + ':' + str(label)+'\n') 
							f.close()
						else:
							f = open('PeerToLabelMapping','a')
							f.write(str(external_peer_ip) + ':' + str(label)+'\n') # python will convert \n to os.linesep
							f.close()		
						i =+ 1
				i =+ 1
		else:
			pass


if __name__ == "__main__":
    main()



