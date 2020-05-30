#!/bin/python3

import os
import subprocess
import requests
print("Machine name:")
name = input()
print("Machine IP:")
ip = input()

host = name.lower() + ".htb"

# Create the folder for the machine
os.mkdir("/home/kali/htb/machines/{}".format(name))

# Add the boxname to /etc/hosts/
with open("/etc/hosts", "a") as hosts_file:
    hosts_file.write("{}\t{}".format(ip, host))
    hosts_file.write("\n")

# Set off some processes to run
# Check if there's a website on the default port running, if so we can start there
website = requests.get("http://{}".format(host))
# If there is a website, kick off gobuster
# TODO: add support for dirb/dirbuster
# TODO: add support for custom wordlist
if website.status_code == 200:
    print("There seems to be a website running on port 80 at {}.".format(ip))
    print("Kicking off gobuster. Use custom wordlist? (default: /usr/share/dirbuster/directory-list-2.3-small.txt)")
    wl_path = input()
    if wl_path == "":
        wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt" 
    else wl_path 

    #TODO: fix this, looks like it stars process, but doesn't save output
    # Call gobuster with wordlist
    subprocess.Popen(["gobuster", "dir", "--url", "http://{}".format(host), "-w", wordlist, "-o", "/home/kali/htb/machines/{}/gobuster_findings.txt".format(name)])

# Start a quick nmap looking for obvious services to start testing asap
subprocess.Popen(["nmap", "--top-ports", "200", "-sS", ip, "-oN", "/home/kali/htb/machines/{}/quick_nmap_top200.txt".format(name)])

# Start a full scan in nice nmap output, which we can refer to easily
subprocess.Popen(["nmap", "-p-", "-T4", ip, "-oN", "/home/kali/htb/machines/{}/nmap_full.txt".format(name)])

# chmod directories
box_path = "/home/kali/htb/machines/{}".format(name)
for root, dirs, files in os.walk(box_path):
    for dir in dirs:
        os.chown(os.path.join(root, dir), 1000, 1000)
        for file in files:
            os.chown(os.path.join(root, file), 1000, 1000)
