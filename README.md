# wbx-aggregator
Scrape a sros configuration file and generate a script to remove individual VPLSs and aggregate the SAPs into the Telecom and OAM VPLS.

This program will support the creation and deployment of a Redundant-WBX or NON-Redundant WBX standard.

The only user input necessary is the edit the yaml file and update the LAG ID's.

This program will locate a .log file under the PWD and process it to extract a list of VPLS ID's. Once the list is extracted,
It will filter through the list using regular expressions and removing and re-formating as necesssary to create a list of VPLSs.
Once the list is created a loop is ran through the list, splitting the list into sub-lists by VPLS's and once again converting the list
to dictionaries. Once the final dictionary is generated, the loop continues to generate a script to remove the VPLS and the SAPs and 
re-create them in the new, correct aggregate VPLS (300/400). A final script is generated and saved as a text file to use during the 
Maintenance Window # 1.
