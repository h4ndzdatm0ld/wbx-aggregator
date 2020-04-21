import glob, os, re

def exhostid():
    '''Extract the system name from a read log file of 'admin displayconfig'
    The return output of this function is the system hostname of a log file.
    A nested function is in place to read the .log file inside the PWD.
    The re-match is processed to remove the outerqoutes it returns with.
    '''
    sysname = re.compile(r'((?<=system\s........name\s)(.*))')

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
                        # print(f"Found a configuration file: {file}\n")
                        return file
        except Exception as e:
            print(f"Something went wrong, {e}")
    

    with open((globfindfile("*.log")), 'r+', encoding='utf-8') as f_rd:
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

print(exhostid())