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

import argparse
from termcolor import colored
from datetime import datetime
import getpass
import os
import pwd
import re
import requests
import subprocess
from string import Template
import time

if os.geteuid() != 0:
    print(colored("You need to run me with sudo", "red"), colored(":)", "yellow"))
    exit(1)

# Get username and ID info for paths
uid = int(os.environ.get('SUDO_UID'))
gid = int(os.environ.get('SUDO_GID'))
user_check = subprocess.check_output(['getent passwd "' + str(uid) + '" | cut -d: -f1'], shell=True)
user = str(user_check.decode().strip())

# Set up the argument parser
parser = argparse.ArgumentParser(description='A HackTheBox quickstart script, must be run as root.')

parser.add_argument('-n', '--name', metavar=colored('box', 'green'), action="store", required=True, help='The name of the box, i.e. Magic')
parser.add_argument('-i', '--ip', metavar=colored('ip_address', 'green'), action="store", required=True, help='The ip of the box, i.e. 10.10.10.180')
parser.add_argument('-w', '--wordlist', metavar=colored('wordlist_path', 'yellow'), action="store", required=False, help='The path to the wordlist. Defaults to /usr/share/dirbuster/wordlists/directory-2.3-small.txt.')
parser.add_argument('-p', '--path', metavar=colored('folder_path', 'yellow'), action="store", required=False, help=f'The path for where to create your folder for this box. Defaults to /home/{user}/htb/machines/box_name.')
parser.add_argument('-t', '--tips', action="store_true", required=False, help=f'Flag that will provide tips to point you in the right direction, based on what is found.')

args = parser.parse_args()

try:
    name = args.name
    ip = args.ip
except:
    print("You need to provide a boxname and an IP address")

try:
    wordlist = args.wordlist
    assert wordlist is not None
except:
    wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt" 

try:
    box_path = args.path
    assert box_path is not None
except:
    box_path = f"/home/{user}/htb/machines/{name}"

# Check if machine is down
print(colored("Checking if host is up...", "cyan"))
host_down = subprocess.call(["ping", "-c", "4", ip], stdout=subprocess.DEVNULL) 

if host_down:
    print(colored(f"\tHost seems down(ip {ip}). Make sure you've started the box on HackTheBox.", "red"))
    exit(1)

else: 
    print(colored("\tHost is up!", "green"))

# variables for checks
ftp_open = False
ftp_anonymous_login = False
web_up = False
gobuster_findings = 0

# Formatting name for /etc/hosts
host = name.lower() + ".htb"

# Create the folder for the machine
print(colored("Creating folder...", "cyan"))
os.mkdir(box_path)

# Add the boxname to /etc/hosts/
print(colored(f"Adding {host} to /etc/hosts...", "cyan"))
with open("/etc/hosts", "a") as hosts_file:
    hosts_file.write(f"{ip}\t{host}")
    hosts_file.write("\n")

# Set off some processes to run
## Check if there's a website on the default port running, if so we can start there
print(colored(f"Checking for a website...", "cyan"))
try:
    website = requests.get(f"http://{host}", timeout=5)
    web_up = True
except:
    web_up = False
    print(colored("\tThere doesn't seem to be a website on port 80, or the request timed out after 5 seconds.", "yellow"))

## If there is a website, kick off gobuster
if web_up is True:
    print(colored(f"\tThere seems to be a website running on port 80 on {host}...", "green"))

    print(colored("\tKicking off gobuster...", "cyan"))

    gobuster = subprocess.Popen(["gobuster", "dir", "--url", f"http://{host}", "-w", wordlist, "--noprogress", "-o", box_path + "/gobuster_findings.txt", "2>" + box_path + "gobuster_errors.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
else:
    print(colored("\tNot running gobuster.", "yellow"))

# Start a quick nmap looking for obvious services to start testing asap
print(colored("Kicking off a quick nmap for the top 200 ports...", "cyan"))
nmap_quick = subprocess.Popen(["nmap", "--top-ports", "200", "-sS", ip, "-oN", box_path + "/nmap_quick.txt"], stdout=subprocess.DEVNULL)

# Check if ftp is open
nmap_quick.wait()
print(colored("\tChecking if ftp is open...", "cyan"))

# Search for ftp port
with open(box_path + "/nmap_quick.txt") as f:
    lines = f.readlines()
    for line in lines:
        if (re.search(r"21\/tcp\s*open\s*ftp", line)):
            ftp_open = True
            print(colored("\t\tFound open ftp port(21), attempting anonymous ftp login...", "cyan"))

            # Run a script which simply checks for anonymous access to ftp
            ftp = subprocess.check_output(["stb_ftp_check.sh"])
            ftp_anonymous_login = re.search(r"Anonymous access allowed", ftp.decode('UTF-8'))
            if ftp_anonymous_login is not None:
                print(colored("\t\t\tAnonymous access allowed!", "green"))
            else:
                print(colored("\t\t\tAnonymous access is not allowed.", "red"))

if ftp_open is False:
   print(colored("\t\tftp not open.", "red"))

# Start a full scan in nice nmap output, which we can refer to easily
print(colored("Starting full nmap scan...", "cyan"))
print(colored(f"\tThis may take a while;  feel free to open another terminal and check out whats in {box_path} while you're waiting.", "cyan"))
nmap_full = subprocess.Popen(["nmap", "-sV", "-p-", "-T4", ip, "-oN", box_path + f"/nmap_full.txt"], stdout=subprocess.DEVNULL)

# Give tips on what do do
if args.tips is True:
    if web_up is True:
        print("""Try poking around the website. 
If gobuster is finished, start looking through the output for interesting files that may contain useful code or accidental information disclosures. 
Try to figure out what software the server is running, and start googling for ways to exploit it.  
If there are forms, check to see where they post to. Are they vulnerable to SQL injection? What happens when you post bad data?
Try checkout out Burp Suite for modifying your requests. If there's an upload form, check what you're allowed to upload.
If there's a login form, perhaps brute force it, or make a note to come back later when you have creds.""")
    if ftp_open is True:
        print(f"Anonymous ftp access allowed! Try 'ftp {ip}', for username enter 'anonymous', for password enter any email address.")
        print("Look around and see if you can download any files. Perhaps they're configurations that mirror the live website config, but have backend server code that you can't see from the website.")
        print("Look through every file you have available to you, you never know when an email writeup might have a sensitive password, or information that leads you to a user account.")

# Make sure processes are finished
nmap_full.wait()
print(colored("nmap full scan finished, waiting on gobuster, this could take a while...", "cyan"))
print(colored(f"You can tail gobuster live (sudo tail -f {box_path}/gobuster_findings.txt) in another window to get live updates while you're waiting for this script to finish.", "cyan"))

if web_up is True:
    gobuster.wait()
    gobuster_findings = os.stat(box_path + "/gobuster_findings.txt").st_size
    
if not gobuster_findings:
    print(colored("\tGobuster didn't seem to find anything.", "red"))
else:
    print(colored(f"\tGobuster found something! Check {box_path}/gobuster_findings.txt!", "green"))

# Create writeup.txt
print(colored("Creating writeup.txt...", "cyan"))
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

writeup = f'{name}\n' \
f'{ip}\n' \
f'{current_datetime}\n' \
f'\n' \
f'There {"seems" if web_up else "does not seem"} to be a website on port 80.\n' \
f'ftp on port 20 {"seems to be open" if ftp_open else "does not seem to be open"}.\n' \
f'Anonymous access {"is" if ftp_anonymous_login else "is not"} allowed.\n'
f'Gobuster {"found some directories using {{wordlist}}" if gobuster_findings else "did not find anything using {{wordlist}}"}\n'

with open(box_path + "/writeup.txt", "w") as file:
    file.write(writeup)

# chmod directories
print(colored("Chmod'ing local directories and files for non-sudo access...", "cyan"))
os.chown(box_path, uid, gid)
for root, dirs, files in os.walk(box_path):
    for file in files:
        os.chown(os.path.join(root, file), uid, gid)

print(colored(f"Done! Check {box_path} to see script outputs. Happy hacking!", "green"))

