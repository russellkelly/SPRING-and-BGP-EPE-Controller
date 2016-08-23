# SPRING-and-BGP-EPE-Controller

A Python Based SPRING and BGP Route Controller focused on the EPE use case.

To run the demo install EXABGP (version 3.4.16) along with Python 2.7.

For details on installing EXABGP refer to this link:

https://github.com/Exa-Networks/exabgp

All files should be located in the same directory of your choice.

Below is some details on what each file does:


CONFIGURATION FILES
===================

RuntimeVariables.yaml
---------------------
          VeryImportantApplicationsSRPaths - A above this is the section where one defines the path for each Egress ASBR.  This file must identify the ASBR by the IP it's setting in it NH advertisement.  In this case the loopback.  Now when the NH is identified, the appropriate SR path is added to the labeled route being advertised..

          VeryImptApplicationsPrefixes - This is the section where the very Important application prefixes are added by the operator.  Each prefix on a new line.

          ConfiguredEPEPeerList - This is a section you can amend before running the demo, it defines the list of peers used in the demo.  Note!! This can be all of the EPE enabled peers, or a subset of them.  Add them each in a new line with the format: [peeraddress'x']:[IP of EPE Peer]

          ImptApplicationsPrefixes - this is the file where the Important application prefixes are added by the operator.  Each prefix on a new line.



TopologyVariables.yaml
---------------------
          home_directory - This is the section where all the files are located.  This is really ONLY needed for building the EXABGP configuration files

          egress_peering_routers - This is the section where the egress router(s) are defined.  This is the router, or routers, that send the routes to EXABGP, the routes are family inet (Internet service routes) and labeled-unicast (EPE Labels) routes

          ingress_peering_routers - This is the section where the ingress router(s) are defined.  These are the routers that receive the BGP labeled routes from EXABGP

          exabgp - This is the IP, or VIP, of the EXABGP process.

          Local_as - The local AS for the EXABGP process.


exabgp.env
----------
          This is the environemtnal file exabgp uses to set logging level, tcp ports, reactor times, etc etc.  The main environmental options set in this file is the logging level and disabling a lot of the messages, so the user can see whats happeniing while running the demo.  When first installing be sure to set this .env file by running the following:

                        sudo exabgp --fi > /usr/local/etc/exabgp/exabgp.env
                        sudo cp exabgp.env /usr/local/etc/exabgp/exabgp.env


SYSTEM RUNTIME FILES
====================


exabgp-ingress-receiving-peer-conf.j2
-------------------------------------

      The JINJA2 template to build the exabgp-ingress-receiving-peer.conf file for EXABGP to use on startup


exabgp-ingress-advertising-peer-conf.j2
-------------------------------------

      The JINJA2 template to build the exabgp-ingress-advertising-peer.conf file for EXABGP to use on startup

app.py
------
        Fires up a simple HTTP portal on port 5000 so one can post via the EXABGP API.


getlabelsandserviceprefixes.py
------------------------------
          This is the main script that the createsfiles PeerToLabelMapping, ServicePrefixes, and bgplog.json and then parses the JSON formated messages received by EXABGP which itself is writing the updates to bgplog.json.  It stores the learned labels and the service prefixes in the files above.  It is continually running and updating said files.

ImportantApplications.py
------------------------
          This python script runs atop of the base "new-epe-controller-bgp-label-only.py" script.  This particular script reads the file ImptApplicationsPrefixes and advertises these if and only if the supernet of the prefixi esist in ServicePrefixes (the file getlabelsandserviceprefixes.py creates dynamically from the received routes from the peering routers).  it uses a different set of prioritized EPE peers the user inputs manually upon starting the script.



epe-controller-base-prefixes.py
-------------------------------
          This is the base python script that routes to the received service prefixes (in the ServicePrefixes file) using the file ConfiguredEPEPeerList as the prioritized list of EPE peers.

new-epe-demo.py
---------------
          This is a base start up file, providing noting more than instructions on what the demo is doing, and the ability to start up different parts of the demo from user input.  This really provides the menu for running the demo and just calls the other python programs/scripts.


routes.sh
---------
          This is the shell script called in the exabgp-bgp-lu.conf file.  This script simply writes the route updates that EXABGP is receiving and exporting in JSON format to the file bgplog.json.  Be sure to make the file executable by running:
            sudo chmod +x routes.sh

VeryImportantApplications.py
----------------------------
          Much like ImportantApplications.pyabove this is a program that can run a top of "new-epe-controller-bgp-label-only.py", again checking the VeryImptApplicationsPrefixes file and advertising them if, and only if, the supernet of the prefixi esist in ServicePrefixes (the file getlabelsandserviceprefixes.py creates dynamically from the received routes from the peering routers).  An important difference here is the ability of the script to advertise the subnet within the supernet along with a user-provisioned SPRING label stack.  The label stack is configureed in the file "VeryImportantApplicationsSRPaths".  This path is updated depending on what Egress ASBR EPE label being used.  That is; if and EPE label from ASBR1 is being used (due to the priority configured by the user when first running VeryImportantApplications.py), then SRPATH1 will be used.  If the EPE peer being used movesto say ASBR2, then the SRPATH2 will be used.  The SRPATHs can be updated on the fly in the file "VeryImportantApplicationsSRPaths", and the python program will pick up the new path




Running the demo
================

Once all files are copied to the directory and the files RuntimeVariables.yaml and TopologyVariables.yaml are complete with the specific Topology and Runtime information one can run topology.

python epe-demo.py

Choose option "1"

To run the overlay  programs, make sure option "1" is running.  Now add the prefixes you want for Important and VeryImportant applications in the files ImptApplicationsPrefixes and VeryImptApplicationsPrefixes respectively.

To run important applications simply run:  python ImportantApplications.py.  Choose "1" - then choose the Peers available.  Program will run.


To run important applications simply run:  python ImportantApplications.py.  Choose "1" - then choose the Peers available.  Program will run.

To run very important applications add the paths into the file "VeryImportantApplicationsSRPaths" then simply run:  
  python VeryImportantApplications.py.  Choose "1" - then choose the Peers available.  Program will run.
