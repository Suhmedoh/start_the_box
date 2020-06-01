# start_the_box (stb)

This is a python3 tool used to quickly start up enumeration & info gathering on a machine for HackTheBox.
Needs to be run as root for the tools

### Current features
* Take user input for boxname + IP
* Check if host is up
* Create folder with box name
* Add the box name to `/etc/hosts` (i.e. 10.10.10.188 magic.htb)
* Checks if website is running on port 80 first
	* if so, start gobuster; option to use custom wordlist
* Does a quick top 200 nmap scan and outputs to box folder
    * based on output, if FTP is open, checks for anonymous access
* Does a full port nmap scan and outputs to the box folder


### TODO:
* scrape HTB for machine IP?
	* allow user to select active box?
* output a "writeup.txt" with box name + ip, date, important results
* find more scripts to kick off based on ports
* ~~if ftp port is open, check for anonymous login~~
* check if there are any mountable shares, automatically mount them
* ~~allow user to set default directory for machine locations~~
