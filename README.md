# SPRING-and-BGP-EPE-Controller

A Python Based SPRING and BGP Route Controller focused on the EPE use case.

To run the demo install EXABGP (version 3.4.16) along with Python 2.7.

For details on installing EXABGP refer to this link:

https://github.com/Exa-Networks/exabgp

All files should be located in the same directory of your choice.

Below is some detail of what each file does:

app.py - Fires up a simple HTTP portal on port 5000 so one can post via the EXABGP API.

ConfiguredEPEPeerList - This is a file you can amend before running the demo, it defines the list of peers used in the demo.  Note!! This can be all of the EPE enabled peers, or a subset of them.  Add them each in a new line with the format: [peeraddress'x']:[IP of EPE Peer]

exabgp-bgp-lu.conf - this is the configuration file for one of the exabgp processes.  Namely the process peering with the egress ASBR's and receiving the BGP family inet and labeled-unicast routes from the egress ASBR in JSON format.  It calls a script routes.sh (detailed below).  NOTE:  In this conf file you will have to ammend the BGP AS and Neighbor entries to fit your topology

exabgp.env - this is the environemtnal file exabgp uses to set logging level, tcp ports, reactor times, etc etc.  The main environmental options set in this file is the logging level and disabling a lot of the messages, so the user can see whats happeniing while running the demo.  When first installing be sure to set this .env file by running the following:

              sudo exabgp --fi > /usr/local/etc/exabgp/exabgp.env
              sudo cp exabgp.env /usr/local/etc/exabgp/exabgp.env
              
getlabelsandserviceprefixes.py - this is the main script that the createsfiles PeerToLabelMapping, ServicePrefixes, and bgplog.json and then parses the JSON formated messages received by EXABGP which itself is writing the updates to bgplog.json.  It stores the learned labels and the service prefixes in the files above.  It is continually running and updating said files.

ImportantApplications.py - this python script runs atop of the base "new-epe-controller-bgp-label-only.py" script.  This particular script reads the file ImptApplicationsPrefixes and advertises these if and only if the supernet of the prefixi esist in ServicePrefixes (the file getlabelsandserviceprefixes.py creates dynamically from the received routes from the peering routers).  it uses a different set of prioritized EPE peers the user inputs manually upon starting the script.

ImptApplicationsPrefixes - this is the file where the Important application prefixes are added by the operator.  Each prefix on a new line.

new-epe-controller-bgp-label-only.py - this is the base pyhton script that routes to the recieved service prefixes (in the ServicePrefixes file) using the file ConfiguredEPEPeerList as the prioritized list of EPE peers.

new-epe-demo.py - This is a base start up file, providing noting more than instaructions on what the demo is doing, and the ability to start up different parts of the demo from user input.  This really provides the menu for running the demo and just calls the other pyhton programs/scripts.

new-exabgp-bgp-label-only.conf - this is the configuration file for EXABGP process peering with the ingress routers and pushing the labeled routes to the routers.  NOTE:  In this conf file you will have to ammend the BGP AS and Neighbor entries to fit your topology

routes.sh - this is the shell script called in the exabgp-bgp-lu.conf file.  This script simply writes the route updates that EXABGP is receiving and exporting in JSON format to the file bgplog.json.  Be sure to make the file executable by running:
  sudo chmod +x routes.sh

VeryImportantApplications.py - Much like ImportantApplications.pyabove this is a program that can run a top of "new-epe-controller-bgp-label-only.py", again checking the VeryImptApplicationsPrefixes file and advertising them if, and only if, the supernet of the prefixi esist in ServicePrefixes (the file getlabelsandserviceprefixes.py creates dynamically from the received routes from the peering routers).  An important difference here is the ability of the script to advertise the subnet within the supernet along with a user-provisioned SPRING label stack.  The label stack is configureed in the file "VeryImportantApplicationsSRPaths".  This path is updated depending on what Egress ASBR EPE label being used.  That is; if and EPE label from ASBR1 is being used (due to the priority configured by the user when first running VeryImportantApplications.py), then SRPATH1 will be used.  If the EPE peer being used movesto say ASBR2, then the SRPATH2 will be used.  The SRPATHs can be updated on the fly in the file "VeryImportantApplicationsSRPaths", and the python program will pick up the new path

VeryImportantApplicationsSRPaths - A above this is the file where one definesthe path for each Egress ASBR.  This file must identify the ASBR by the IP it's setting in it NH advertisement.  In this case the loopback.  Now when the NH is identified, the appropriate SR path is added to the labeled route being advertised..

VeryImptApplicationsPrefixes - this is the file where the very Important application prefixes are added by the operator.  Each prefix on a new line.


Running the demo
================

Once all files are copied to the directory and the peers for the base EPE are added to ConfiguredEPEPeerList one can run 

python new-epe-demo.py

Choose option "2"

To run the overlay  programs, make sure option "2" is running.  Now add the prefixes you weant for Important and VeryImportant applications in the files ImptApplicationsPrefixes and VeryImptApplicationsPrefixes respectively.

To run importnat applications simply run:  python ImportantApplications.py.  Choose "1" - then choose the Peers available.  Program will run.


To run important applications simply run:  python ImportantApplications.py.  Choose "1" - then choose the Peers available.  Program will run.

To run very important applications add the paths into the file "VeryImportantApplicationsSRPaths" then simply run:  
  python VeryImportantApplications.py.  Choose "1" - then choose the Peers available.  Program will run.
