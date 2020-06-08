# start_the_box (stb)

This is a python3 tool used to quickly start up enumeration & info gathering on a machine for HackTheBox.

Needs to be run as root for the tools.

![Example of start the box being run](./example.png?raw=true "Example of Start The Box")

## HOW TO USE
Clone the repo somewhere (I have a folder in home where I keep all my github repos, ~/github/start_the_box

Depending on where you want to store your machine folders, I symbolically link to that base folder(~/htb/machines/stb)

Run start_the_box.py with sudo to see necessary arguments

`cd ~/github`

`git clone https://github.com/Suhmedoh/start_the_box`

`mkdir -p /home/kali/htb/machines`

`cd /home/kali/htb/machines`

`sudo ln -s /home/kali/github/start_the_box/start_the_box.py /usr/local/bin`

`sudo stb`

`sudo stb --help`

`sudo stb -n Magic -i 10.10.10.4`


### Current features
* Take user input for boxname + IP
* Check if host is up
* Create folder with box name
* Add the box name to `/etc/hosts` (i.e. 10.10.10.188 magic.htb)
* Checks if website is running on port 80 first
	* if so, start gobuster; option to use custom wordlist
* Does a quick top 200 nmap scan and outputs to box folder
    * Checks if FTP is open
	* Checks for anonymous access
* Does a full port nmap scan and outputs to the box folder
* Creates a "box_name.txt" with info (boxname, ip, time started, ftp access, website up, etc.)


### TODO:
* scrape HTB for machine IP?
	* allow user to select active box?
* ~~output a "writeup.txt" with box name + ip, date, important results~~ DONE
	* add more details in the writeup
* find more scripts to kick off based on ports
* ~~if ftp port is open, check for anonymous login~~ DONE
* check if there are any mountable shares, automatically mount them
* ~~allow user to set default directory for machine locations~~ DONE
