#!/bin/python3
# Created by the Pizza Processing Unit

import os
import subprocess
import requests
import re
import argparse
import getpass
import time

user = getpass.getuser()

parser = argparse.ArgumentParser(description='A HackTheBox quickstart script.')
parser.add_argument('--name', '-n', metavar='name', action=store, type=string, help='The name of the box, i.e. Magic')
parser.add_argument('--ip', '-i', metavar='ip', action=store, type=string, help='The ip of the box, i.e. 10.10.10.180')
parser.add_argument('--wordlist', '-w', metavar='wordlist', action=store, type=string, help='The path to the wordlist. Defaults to /usr/share/dirbuster/wordlists/directory-2.3-small.txt.')
parser.add_argument('--path', '-p', metavar='path', action=store, type=string, help=f'The path for where to create your folder for this box. Defaults to /home/{user}/htb/machines/box_name.')
args = parser.parse_args()
name = args.name
ip = args.ip
wordlist = args.wordlist

host = name.lower() + ".htb"

# Create the folder for the machine
print("Creating folder...")
os.mkdir(f"/home/{user}/htb/machines/{name}")

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
    gobuster = subprocess.Popen(["gobuster", "dir", "--url", f"http://{host}", "-w", wordlist, "-o", f"/home/{user}/htb/machines/{name}/gobuster_findings.txt"], stdout=subprocess.DEVNULL)

# Start a quick nmap looking for obvious services to start testing asap
nmap_quick = subprocess.Popen(["nmap", "--top-ports", "200", "-sS", ip, "-oN", f"/home/{user}/htb/machines/{name}/quick_nmap_top200.txt"], stdout=subprocess.DEVNULL)

# Check if ftp is open
nmap_quick.wait()
print("Checking if ftp is open...")
ftp_open = False
for line in enumerate(open(f'/home/{user}/htb/machines/{name}/nmap_quick.txt')):
    if (re.search(r"21\/tcp\s*open\s*ftp", line)):
        ftp_open = True
        print("Found open ftp port(21), attempting anonymous ftp login...")
        ftp = subprocess.Popen(['ftp', '{host}'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(.2)
        stdout_data = p.communicate(input='anonymous'.encode())[0]
        time.sleep(.1)
        stdout_data = p.communicate(input='anonymous@htb.com'.encode())[0]
        print(stdout)
        ftp.kill()
if ftp_open = False:
   print("ftp not open.")

# Start a full scan in nice nmap output, which we can refer to easily
print("Starting full nmap scan...")
nmap_full = subprocess.Popen(["nmap", "-p-", "-T4", ip, "-oN", f"/home/{user}/htb/machines/{name}/nmap_full.txt"], stdout=subprocess.DEVNULL)

nmap_full.wait()
gobuster.wait()
# chmod directories
print("Chmod'ing local directories and files for non-sudo access...")
box_path = f"/home/{user}/htb/machines/{name}"
for root, dirs, files in os.walk(box_path):
    for dir in dirs:
        os.chown(os.path.join(root, dir), 1000, 1000)
        for file in files:
            os.chown(os.path.join(root, file), 1000, 1000)

print("Done! Check /home/{user}/htb/machines/{name}/ to see script outputs. Happy hacking!")

