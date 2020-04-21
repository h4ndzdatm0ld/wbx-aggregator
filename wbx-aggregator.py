#!/usr/bin/env python3

import re, os, glob, sys


vpls = re.compile(r'(vpls\s\d.+\n.*\n.*\n.*\n.*\n.*\n.*)')

# This program will locate a .log file under the PWD and process it to extract a list of VPLS ID's. Once the list is extracted,
# It will filter through the list using regular expressions and removing and re-formating as necesssary to create a list of VPLSs.
# Once the list is created a loop is ran through the list, splitting the list into sub-lists by VPLS's and once again converting the list
# to dictionaries. Once the final dictionary is generated, the loop continues to generate a script to remove the VPLS and the SAPs and 
# re-create them in the new, correct aggregate VPLS (300/400). A final script is generated and saved as a text file to use during the 
# Maintenance Window # 1.

def exhostid():
    '''Extract the system name from a read log file of 'admin displayconfig'
    The return output of this function is the system hostname of a log file.
    A nested function is in place to read the .log file inside the PWD.
    The re-match is processed to remove the outerqoutes it returns with.
    '''
    sysname = re.compile(r'((?<=system\s........name\s)(.*))')

    def globfindfilez(regex):
        ''' This function will simply locate a file in the DIR by passing the regex value (ie:(*.log))
            The returned value by calling the function is the file.
        '''
        try:
            if len(glob.glob(regex)) == 0:
                sys.exit(f"No {regex} file found.")
            else:
                for file in glob.glob(regex):
                    if len(glob.glob(regex)) > 1:
                        sys.exit(f"Err.. found too many {regex} files")
                    else:
                        # print(f"Found a configuration file: {file}\n")
                        return file
        except Exception as e:
            print(f"Something went wrong, {e}")
    

    with open((globfindfilez("*.log")), 'r+', encoding='utf-8') as f_rd:
        contents = f_rd.read()

    # Finditer to match the first match against the read file.
    name = re.finditer(sysname,contents)

    rem_qtz = ['"']
    for match in name:
        try:
            system = (match.group(0))
            # print(system)
        except UnboundLocalError:
            print("Err.. regex failed to find system name")

    for i in rem_qtz:
        try:
            system = system.replace(i, '')
            f_rd.close()
            return system
        except UnboundLocalError:
            print("Err.. regex failed to find system name")
            # At this point, the node system name is captured as a variable.
            # named 'system'


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def globfindfile(regex):
    ''' This function will simply locate a file in the DIR by passing the regex value (ie:(*.log))
        The returned value by calling the function is the file.
    '''
    try:
        if len(glob.glob(regex)) == 0:
            sys.exit(f"No {regex} file found.")
        else:
            for file in glob.glob(regex):
                if len(glob.glob(regex)) > 1:
                    sys.exit(f"Err.. found too many {regex} files")
                else:
                    print(f"Found a configuration file: {file}\n")
                    return file
    except Exception as e:
        print(f"Something went wrong, {e}")

def dictconvert(lst):
    ''' Convert a list to dict
    '''
    try:
        res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
        return res_dct
    except Exception as e:
        print(f"found an issue with dictconvert function. {e}")

def vplsextract(compiledregex, file):
    '''
    Utilizes re.findall to extract values and strip space and split with the 'no shutdown' keyword
    at the end of the regex match for each vpls instance, including saps and descriptions.
    '''
    try:
        valuextract = re.findall(compiledregex, file)
        list = ([l.strip() for l in valuextract])
        return list
    except Exception as e:
        print(f"found an issue with vplsextract function. {e}")

def vplslistmodify():
    try:
        # Passing the globfindfile function, to find the file and read it.
        with open((globfindfile("*.log")), 'r+', encoding='utf-8') as f_rd:
            contents = f_rd.read()

            hostname = exhostid()
            # Change into temp folder and create an empty file to offload the vpls info
            # and manipulate the file with regex.
            BASE = os.getcwd()
            createFolder('Temp')
            TEMPFILE = BASE+'/Temp/vplsinfo-temp.txt'
            tempfl=open(TEMPFILE, 'w+')

            #Run the vplsextract and loop through it. Write the contents to a temp file.
            vplsinfo = vplsextract(vpls,contents)


            for line in vplsinfo:
                tempfl.writelines(line+'\n')
            # Close the temp file.
            tempfl.close()
            
            # Pass over the  temp file and remove items which we need to eliminate to create a
            # working dictionary. Once the list is able to be split and converted into a dictionary, loop through it and extract the values to create the script
            # to remove all the saps and shut down and remove the vpls.

            with open(TEMPFILE, 'r+', encoding='utf-8') as f_rd:
                passover = f_rd.read()

                xt = re.compile(r'(exit)')
                crt = re.compile(r'(create)')
                lb = re.compile(r'(\n)')
                nsht = re.compile(r'(no shutdown)')
                sp = re.compile(r'(\s+)')
                lagsap = re.compile(r'(sap\slag)') # Replace the second sap in the VPLS, to avoid overwritting key when converting to dictionary.
                # -----------------
                PASS1 = re.sub(xt,'', passover)
                PASS2 = re.sub(crt,'',PASS1)
                PASS3 = re.sub(lb,'',PASS2)
                PASS4 = re.sub(sp,' ', PASS3)
                PASS5 = re.sub(lagsap,'lag-out lag', PASS4)

                PASS6 = list(PASS5.split('no shutdown')) # Splits all the extracted VPLS's by the 'no shutdown' found inside the text str
                
                #Splitting leaves 1 empty list at the end, simply pop it out.
                PASS6.pop()

                BASE = os.getcwd()
                TEMPFILE = BASE+'/Temp/''SOW-'+hostname+'.txt'
                tempfl=open(TEMPFILE, 'w+')

                try:
                    for x in PASS6:
                        vplsdict = (dictconvert(x.split()))
                        # print(vplsdict)
                        if '1' in vplsdict['customer']:
                            # print(f"echo Migrating service-id {vplsdict['vpls']}")
                            # print(f"/configure service vpls {vplsdict['vpls']} shutdown")
                            # print(f"/configure service vpls {vplsdict['vpls']} no description")
                            # print(f"/configure service vpls {vplsdict['vpls']} sap {vplsdict['sap']} shutdown")
                            # print(f"/configure service vpls {vplsdict['vpls']} no sap {vplsdict['sap']}")
                            # print(f"/configure service vpls {vplsdict['vpls']} sap {vplsdict['lag-out']} shutdown")
                            # print(f"/configure service vpls {vplsdict['vpls']} no sap {vplsdict['lag-out']}")
                            # print(f"/configure service no vpls {vplsdict['vpls']}")
                            # print(f"/configure service vpls 300")
                            # print(f"/configure service vpls 300 sap {vplsdict['sap']} create")
                            # print(f"/configure service vpls 300 sap {vplsdict['sap']} no shutdown")
                            # print(f"/configure service vpls 300 sap lag-31:300 create") # Pass variable  of chosen LAG with openpyxl / excel(cq)
                            # print(f"/configure service vpls 300 sap lag-31:300 no shutdown\n")
                            tempfl.write(f"echo Migrating service-id {vplsdict['vpls']}\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} shutdown\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} no description\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} sap {vplsdict['sap']} shutdown\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} no sap {vplsdict['sap']}\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} sap {vplsdict['lag-out']} shutdown\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} no sap {vplsdict['lag-out']}\n")
                            tempfl.write(f"/configure service no vpls {vplsdict['vpls']}\n")
                            tempfl.write(f"/configure service vpls 300\n")
                            tempfl.write(f"/configure service vpls 300 sap {vplsdict['sap']} create\n")
                            tempfl.write(f"/configure service vpls 300 sap {vplsdict['sap']} no shutdown\n")
                            tempfl.write(f"/configure service vpls 300 sap lag-31:300 create\n") # Pass variable  of chosen LAG with openpyxl / excel(cq)
                            tempfl.write(f"/configure service vpls 300 sap lag-31:300 no shutdown\n")
                        elif '4' in vplsdict['customer']:
                            # print(f"echo Migrating service-id {vplsdict['vpls']}")
                            # print(f"/configure service vpls {vplsdict['vpls']} shutdown")
                            # print(f"/configure service vpls {vplsdict['vpls']} no description")
                            # print(f"/configure service vpls {vplsdict['vpls']} sap {vplsdict['sap']} shutdown")
                            # print(f"/configure service vpls {vplsdict['vpls']} no sap {vplsdict['sap']}")
                            # print(f"/configure service vpls {vplsdict['vpls']} sap {vplsdict['lag-out']} shutdown")
                            # print(f"/configure service vpls {vplsdict['vpls']} no sap {vplsdict['lag-out']}")
                            # print(f"/configure service no vpls {vplsdict['vpls']}")
                            # print(f"/configure service vpls 400")
                            # print(f"/configure service vpls 400 sap {vplsdict['sap']} create")
                            # print(f"/configure service vpls 400 sap {vplsdict['sap']} no shutdown")
                            # print(f"/configure service vpls 400 sap lag-31:400 create") #  Pass variable  of chosen LAG with openpyxl / excel(cq)
                            # print(f"/configure service vpls 400 sap lag-31:400 no shutdown\n")
                            tempfl.write(f"echo Migrating service-id {vplsdict['vpls']}\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} shutdown\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} no description\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} sap {vplsdict['sap']} shutdown\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} no sap {vplsdict['sap']}\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} sap {vplsdict['lag-out']} shutdown\n")
                            tempfl.write(f"/configure service vpls {vplsdict['vpls']} no sap {vplsdict['lag-out']}\n")
                            tempfl.write(f"/configure service no vpls {vplsdict['vpls']}\n")
                            tempfl.write(f"/configure service vpls 400\n")
                            tempfl.write(f"/configure service vpls 400 sap {vplsdict['sap']} create\n")
                            tempfl.write(f"/configure service vpls 400 sap {vplsdict['sap']} no shutdown\n")
                            tempfl.write(f"/configure service vpls 400 sap lag-31:400 create\n") #  Pass variable  of chosen LAG with openpyxl / excel(cq)
                            tempfl.write(f"/configure service vpls 400 sap lag-31:400 no shutdown\n")

                except Exception as e:
                    print(e)

                tempfl.close()

    except Exception as e:
        print(f"Something went wrong with vplslist modify, {e}")

vplslistmodify()
