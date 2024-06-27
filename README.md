AutoDNS.py Script Explanation
Overview
The AutoDNS.py script is designed to automate the configuration of a DNS server using Bind9 on an Ubuntu system. It creates the necessary zone files for forward and reverse DNS lookups, updates the Bind9 configuration, and restarts the Bind9 service to apply the changes.
Dependencies
Before running the script, ensure that the following dependencies are installed on your system:

Python 3.x: The script is written in Python and requires Python 3.x to run.
Bind9: The DNS server software that will be configured.
shutil module: This is included in the Python Standard Library and is used for file operations like copying files.
os module: This is also included in the Python Standard Library and is used for interacting with the operating system.
Script Breakdown
Importing Modules
