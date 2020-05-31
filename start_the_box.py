#!/bin/python3
# Created by the Pizza Processing Unit
#
#                                       -:------`                                
#                                      +ssoooo/:-.``                             
#                                    .ossssoohhhso+:-``                          
#                                  .-+s+/::++syso+sso/:..``                      
#                                .:+oosso+-.-:/+///ossooo/-.``                   
#                              `:/+oooo++:` ``.--..syysooooo:-.`                 
#                             ./soooos++/`        `:/::/ooss+/:...`              
#                            :++++///-....`.::--...`-` `.-/ooo+:-..`.`           
#                           .:/.````..-/+oooossoooo+/.    -:oyhso/:-`.``         
#                         .--//-.`..-::+ooosoooosooooo/-.```:++o+++/-....`       
#                      `://///////:-.--/osssssssssssso+`.` ``:+sssso/:-``..`     
#                    `-+/+/++ooooooooo+/:+ossoosssso+:. `..-:+ossyyyyo++.``--`   
#                    `-:osssosssoososso/``.://////:-.``:+++ossosyhyssso:..--..   
#                   `.-/osssssssssossss+:////:///:..:-:/++oosooooooo+oo//-.``    
#                 `` `.-:+oosssosssso++++/+oosoooo+-.-+///+//+o+ss+/:-..`        
#              `-/+++:... `.-:///+/:..+/+osooo+s++o+/:+//://///:--...`           
#            -/ooooo++/--.-:++++++/:.-//+ooo++/+ooo+/:.::-` `.`.``               
#          -+ooooooooo+:./++so+o+//shs///sssso+//:///:::.``                      
#        .+sssossoo+-``.+/:+osoo//s+syy++////-..:::-.``                          
#      `:osssso+/:-````.oo+osyysossssys+/-````                                   
#      `..--.`-:--...:/:sssyssyso+/::-.                                          
#    `.--....`.-.-:/++oo//::-..`                                                 
#    .----:++:..-.`                                                              
#     `-:-.``     

import os
import pwd
import subprocess
import requests
import re
import argparse
import getpass
import time

uid = int(os.environ.get('SUDO_UID'))
gid = int(os.environ.get('SUDO_GID'))
user_check = subprocess.check_output(['getent passwd "' + str(uid) + '" | cut -d: -f1'], shell=True)
print("user: " + str(user_check.decode().strip()))
user = str(user_check.decode().strip())
parser = argparse.ArgumentParser(description='A HackTheBox quickstart script.')
parser.add_argument('-n', '--name', metavar='box', action="store", required=True, help='The name of the box, i.e. Magic')
parser.add_argument('-i', '--ip', metavar='ip_address', action="store", required=True, help='The ip of the box, i.e. 10.10.10.180')
parser.add_argument('-w', '--wordlist', metavar='wordlist_path', action="store", required=False, help='The path to the wordlist. Defaults to /usr/share/dirbuster/wordlists/directory-2.3-small.txt.')
parser.add_argument( '-p', '--path', metavar='folder_path', action="store", required=False, help=f'The path for where to create your folder for this box. Defaults to /home/{user}/htb/machines/box_name.')
args = parser.parse_args()
name = args.name
ip = args.ip
wordlist = args.wordlist

host = name.lower() + ".htb"
# TODO: script runs as root, we want it to run as the user, figure out how
# Create the folder for the machine
print("Creating folder...")
box_path = f"/home/{user}/htb/machines/{name}"
os.mkdir(box_path)

# Add the boxname to /etc/hosts/
print(f"Adding {host} to /etc/hosts...")
with open("/etc/hosts", "a") as hosts_file:
    hosts_file.write(f"{ip}\t{host}")
    hosts_file.write("\n")

# Set off some processes to run
## Check if there's a website on the default port running, if so we can start there
website = requests.get(f"http://{host}")

## If there is a website, kick off gobuster
## TODO: add support for dirb/dirbuster
if website.status_code == 200:
    print(f"There seems to be a website running on port 80 on {host}...")
    print("Kicking off gobuster...")
    if wordlist is None:
        wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt" 

    #TODO: fix this, looks like it starts process, but doesn't save output
    # Call gobuster with wordlist
    gobuster = subprocess.Popen(["gobuster", "dir", "--url", f"http://{host}", "-w", wordlist, "-o", box_path + "/gobuster_findings.txt"], stdout=subprocess.DEVNULL)

# Start a quick nmap looking for obvious services to start testing asap
nmap_quick = subprocess.Popen(["nmap", "--top-ports", "200", "-sS", ip, "-oN", box_path + "/nmap_quick.txt"], stdout=subprocess.DEVNULL)

# Check if ftp is open
nmap_quick.wait()
print("Checking if ftp is open...")
ftp_open = False

# Search for ftp port
with open(box_path + "/nmap_quick.txt") as f:
    lines = f.readlines()
    for line in lines:
        if (re.search(r"21\/tcp\s*open\s*ftp", line)):
            ftp_open = True
            input_file = open("tmpout", "wb")
            output_file = open("tmpout", "r")

            print("Found open ftp port(21), attempting anonymous ftp login...")
            ftp = subprocess.Popen(['echo', '"user anonymous anonymous@htb.com"', '|', 'ftp', '-n', '-v', '10.10.10.180'], shell=True, capture_output=True, text=True)
            print(ftp.stdout)
            anonymous_login = re.search(r"Anonymous access allowed", ftp.stdout)
            if anonymous_login != None:
                print(f"Anonymous ftp access allowed! Try 'ftp {ip}', for username enter 'anonymous', for password enter any email address.")

if ftp_open == False:
   print("ftp not open.")

# Start a full scan in nice nmap output, which we can refer to easily
print("Starting full nmap scan...")
nmap_full = subprocess.Popen(["nmap", "-p-", "-T4", ip, "-oN", f"/home/{user}/htb/machines/{name}/nmap_full.txt"], stdout=subprocess.DEVNULL)

# Make sure processes are finished
nmap_full.wait()
gobuster.wait()

# chmod directories
print("Chmod'ing local directories and files for non-sudo access...")
box_path = f"/home/{user}/htb/machines/{name}"
for root, dirs, files in os.walk(box_path):
    for dir in dirs:
        os.chown(os.path.join(root, dir), uid, gid)
        for file in files:
            os.chown(os.path.join(root, file), uid, gid)

print("Done! Check " + box_path + " to see script outputs. Happy hacking!")

