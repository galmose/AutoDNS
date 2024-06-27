
# AutoDNS Configuration Script

## Overview

The `AutoDNS.py` script automates the configuration of a DNS server using Bind9 on an Ubuntu system. It creates the necessary zone files for forward and reverse DNS lookups, updates the Bind9 configuration, and restarts the Bind9 service to apply the changes.
In this configuration example we will use as IP address `192.168.183.17` and as domain name `integris.ptt`

## Dependencies

Before running the script, ensure that the following dependencies are installed on your system:

- **Python 3.x**: The script is written in Python and requires Python 3.x to run.
- **Bind9**: The DNS server software that will be configured.
- **dnspython**: A DNS toolkit for Python to handle DNS queries and responses.
- **shutil module**: This is included in the Python Standard Library and is used for file operations like copying files.
- **os module**: This is also included in the Python Standard Library and is used for interacting with the operating system.

### Installing Dependencies

1. **Install Bind9**

   ```sh
   sudo apt update
   sudo apt install bind9 bind9utils bind9-doc

2. **Install dnspython**

   ```sh
   pip install dnspython
   ```

## Script Breakdown

### Importing Modules

```python
import os
from shutil import copyfile
```

### Defining File Paths

The script defines the paths to the forward and reverse zone files and the Bind9 local configuration file.

```python
zone_file_path = '/etc/bind/db.integris.ptt'
reverse_zone_file_path = '/etc/bind/db.192.168.183'
named_conf_local_path = '/etc/bind/named.conf.local'
```

### Zone File Content

The forward and reverse zone file contents are defined as multi-line strings. These strings specify the DNS records for the domain `integris.ptt` and its reverse lookup.

```python
zone_file_content = f"""
$TTL    604800
@       IN      SOA     ns.integris.ptt. root.integris.ptt. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.integris.ptt.
ns      IN      A       192.168.183.17
www     IN      A       192.168.183.17  
@       IN      A       192.168.183.17
"""

reverse_zone_file_content = f"""
$TTL    604800
@       IN      SOA     ns.integris.ptt. root.integris.ptt. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.integris.ptt.
17.183.168.192.in-addr.arpa.  IN      PTR     www.integris.ptt.
"""
```

### Updating Bind9 Configuration

The script appends the new zone configurations to `named.conf.local`.

```python
named_conf_local_content = f"""
zone "integris.ptt" {{
    type master;
    file "{zone_file_path}";
}};

zone "183.168.192.in-addr.arpa" {{
    type master;
    file "{reverse_zone_file_path}";
}};
"""
```

### Function to Create Zone Files

This function writes the defined content to the respective zone files and updates `named.conf.local`.

```python
def create_zone_files():
    # Write the forward zone file
    with open(zone_file_path, 'w') as zone_file:
        zone_file.write(zone_file_content)
    # Write the reverse zone file
    with open(reverse_zone_file_path, 'w') as reverse_zone_file:
        reverse_zone_file.write(reverse_zone_file_content)
    # Append the zone configurations to named.conf.local
    with open(named_conf_local_path, 'a') as named_conf_local:
        named_conf_local.write(named_conf_local_content)
```

### Function to Restart Bind9

This function restarts the Bind9 service to apply the new configuration.

```python
def restart_bind9():
    os.system('sudo /etc/init.d/named restart')
```

### Main Function

The main function backs up the original files (if they exist), creates the new zone files, restarts Bind9, and prints a success message.

```python
def main():
    # Backup original files if they exist
    if os.path.exists(zone_file_path):
        copyfile(zone_file_path, f"{zone_file_path}.bak")
    if os.path.exists(reverse_zone_file_path):
        copyfile(reverse_zone_file_path, f"{reverse_zone_file_path}.bak")
    if os.path.exists(named_conf_local_path):
        copyfile(named_conf_local_path, f"{named_conf_local_path}.bak")

    # Create zone files and restart Bind9
    create_zone_files()
    restart_bind9()
    print("DNS configuration applied successfully.")

# Entry point of the script
if __name__ == "__main__":
    main()
```

## Update /etc/resolv.conf 

To ensure your system uses the new DNS server for name resolution, you need to update the  `/etc/resolv.conf` file to point to the local DNS server.
Edit  `/etc/resolv.conf` and add the following lines: 
```sh
nameserver 192.168.183.17
search integris.ptt
  ```


## DNS Tests

After running the script, perform the following tests to ensure the DNS server is functioning correctly:

1. **Check Forward DNS Lookup**

   Use the `dig` command to verify that the domain `integris.ptt` resolves to the correct IP address.

   ```sh
   dig @192.168.183.17 integris.ptt
   ```

2. **Check Reverse DNS Lookup**

   Use the `dig` command to verify the reverse DNS lookup for the IP address `192.168.183.17`.

   ```sh
   dig @192.168.183.17 -x 192.168.183.17
   ```

3. **Ping the Domain**

   Use the `ping` command to ensure that the domain `integris.ptt` is reachable.

   ```sh
   ping integris.ptt
   ```

4. **Check DNS Server Status**

   Ensure that the Bind9 service is running correctly.

   ```sh
   sudo /etc/init.d/named restart
   sudo named-checkzone integris.ptt /etc/bind/db.integris.ptt
   sudo named-checkconf
   ```

## Conclusion

This script automates the configuration of a DNS server by creating and updating the necessary zone files and configurations, then restarting the Bind9 service. By following the above steps and performing the DNS tests, you can ensure that your DNS server is set up and functioning as expected.
