#!/usr/bin/env python3
"""
AutoDNS - DNS Server Configuration Script
----------------------------------------
This script automates the configuration of a Bind9 DNS server on Ubuntu systems.
It creates the necessary zone files for forward and reverse DNS lookups,
updates the Bind9 configuration, and restarts the service to apply changes.
"""

import os
import sys
from shutil import copyfile
import ipaddress
import socket

# User configurable settings - MODIFY THESE VALUES FOR YOUR SETUP
IP_ADDRESS = "192.168.183.17"
DOMAIN_NAME = "integris.ptt"

# Additional configuration options
BACKUP_FILES = True       # Create backup of existing files
RESTART_SERVICE = True    # Restart Bind9 service after configuration
ADD_SAMPLE_RECORDS = True # Add sample DNS records (www, mail, etc.)

def validate_inputs():
    """Validate IP address and domain name inputs."""
    # Validate IP address
    try:
        ipaddress.ip_address(IP_ADDRESS)
    except ValueError:
        print(f"Error: '{IP_ADDRESS}' is not a valid IP address.")
        return False
    
    # Basic domain name validation
    if not DOMAIN_NAME or '.' not in DOMAIN_NAME:
        print(f"Error: '{DOMAIN_NAME}' does not appear to be a valid domain name.")
        return False
        
    return True

def get_reverse_zone_prefix():
    """Extract reverse zone prefix from IP address."""
    octets = IP_ADDRESS.split('.')
    reverse_prefix = '.'.join(octets[0:3][::-1])  # First 3 octets in reverse order
    return reverse_prefix

def get_ptr_name():
    """Get the PTR record name for reverse DNS."""
    octets = IP_ADDRESS.split('.')
    return f"{octets[3]}.{get_reverse_zone_prefix()}.in-addr.arpa."

def create_file_paths():
    """Create file paths based on domain name and IP address."""
    # Forward zone file path
    zone_file_path = f'/etc/bind/db.{DOMAIN_NAME}'
    
    # Extract network part of IP for reverse zone
    ip_prefix = '.'.join(IP_ADDRESS.split('.')[:3])
    reverse_zone_file_path = f'/etc/bind/db.{ip_prefix}'
    
    # Bind9 local configuration path
    named_conf_local_path = '/etc/bind/named.conf.local'
    
    return zone_file_path, reverse_zone_file_path, named_conf_local_path

def generate_forward_zone_content():
    """Generate the content for the forward zone file."""
    content = f"""$TTL    604800
@       IN      SOA     ns.{DOMAIN_NAME}. root.{DOMAIN_NAME}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{DOMAIN_NAME}.
ns      IN      A       {IP_ADDRESS}
@       IN      A       {IP_ADDRESS}
"""

    # Add sample records if configured
    if ADD_SAMPLE_RECORDS:
        content += f"""www     IN      A       {IP_ADDRESS}
mail    IN      A       {IP_ADDRESS}
webmail IN      CNAME   mail.{DOMAIN_NAME}.
"""
    
    return content

def generate_reverse_zone_content():
    """Generate the content for the reverse zone file."""
    reverse_prefix = get_reverse_zone_prefix()
    ptr_name = get_ptr_name()
    
    content = f"""$TTL    604800
@       IN      SOA     ns.{DOMAIN_NAME}. root.{DOMAIN_NAME}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{DOMAIN_NAME}.
{ptr_name}  IN      PTR     {DOMAIN_NAME}.
"""

    # Add additional PTR records if sample records are enabled
    if ADD_SAMPLE_RECORDS:
        content += f"{ptr_name}  IN      PTR     ns.{DOMAIN_NAME}.\n"
        content += f"{ptr_name}  IN      PTR     www.{DOMAIN_NAME}.\n"
        content += f"{ptr_name}  IN      PTR     mail.{DOMAIN_NAME}.\n"
    
    return content

def generate_named_conf_content(zone_file_path, reverse_zone_file_path):
    """Generate the content for named.conf.local."""
    # Extract the reverse zone name from IP address (e.g., 183.168.192.in-addr.arpa)
    ip_parts = IP_ADDRESS.split('.')
    reverse_zone = f"{ip_parts[2]}.{ip_parts[1]}.{ip_parts[0]}.in-addr.arpa"
    
    content = f"""
zone "{DOMAIN_NAME}" {{
    type master;
    file "{zone_file_path}";
}};

zone "{reverse_zone}" {{
    type master;
    file "{reverse_zone_file_path}";
}};
"""
    return content

def create_zone_files(zone_file_path, reverse_zone_file_path, named_conf_local_path):
    """Create the zone files and update named.conf.local."""
    # Generate file contents
    zone_file_content = generate_forward_zone_content()
    reverse_zone_file_content = generate_reverse_zone_content()
    named_conf_local_content = generate_named_conf_content(zone_file_path, reverse_zone_file_path)
    
    # Write the forward zone file
    with open(zone_file_path, 'w') as zone_file:
        zone_file.write(zone_file_content)
    print(f"Created forward zone file: {zone_file_path}")
    
    # Write the reverse zone file
    with open(reverse_zone_file_path, 'w') as reverse_zone_file:
        reverse_zone_file.write(reverse_zone_file_content)
    print(f"Created reverse zone file: {reverse_zone_file_path}")
    
    # Append the zone configurations to named.conf.local
    with open(named_conf_local_path, 'a') as named_conf_local:
        named_conf_local.write(named_conf_local_content)
    print(f"Updated Bind9 configuration: {named_conf_local_path}")

def restart_bind9():
    """Restart the Bind9 service."""
    print("Restarting Bind9 service...")
    result = os.system('sudo systemctl restart bind9')
    
    if result == 0:
        print("Bind9 service restarted successfully.")
    else:
        print("Failed to restart Bind9 service. Check logs with: sudo journalctl -xe | grep named")

def backup_files(files):
    """Create backups of existing files."""
    for file_path in files:
        if os.path.exists(file_path):
            backup_path = f"{file_path}.bak"
            copyfile(file_path, backup_path)
            print(f"Created backup: {backup_path}")

def verify_configuration(zone_file_path, reverse_zone_file_path):
    """Verify the DNS configuration using named-checkzone."""
    print("\nVerifying configuration...")
    
    # Check forward zone
    os.system(f"sudo named-checkzone {DOMAIN_NAME} {zone_file_path}")
    
    # Extract reverse zone name from IP
    ip_parts = IP_ADDRESS.split('.')
    reverse_zone = f"{ip_parts[2]}.{ip_parts[1]}.{ip_parts[0]}.in-addr.arpa"
    
    # Check reverse zone
    os.system(f"sudo named-checkzone {reverse_zone} {reverse_zone_file_path}")
    
    # Check named configuration
    os.system("sudo named-checkconf")

def print_test_instructions():
    """Print instructions for testing the DNS configuration."""
    print("\n----- TESTING INSTRUCTIONS -----")
    print("To test your DNS configuration, run the following commands:")
    print(f"\n1. Check forward DNS lookup:")
    print(f"   dig @{IP_ADDRESS} {DOMAIN_NAME}")
    
    print(f"\n2. Check reverse DNS lookup:")
    print(f"   dig @{IP_ADDRESS} -x {IP_ADDRESS}")
    
    print(f"\n3. Test with ping:")
    print(f"   ping {DOMAIN_NAME}")
    
    print("\n4. Update your resolv.conf (if needed):")
    print(f"   echo 'nameserver {IP_ADDRESS}' | sudo tee /etc/resolv.conf")
    print(f"   echo 'search {DOMAIN_NAME}' | sudo tee -a /etc/resolv.conf")

def main():
    """Main function."""
    print("========================================")
    print("       AutoDNS Configuration Tool       ")
    print("========================================")
    print(f"Domain: {DOMAIN_NAME}")
    print(f"IP Address: {IP_ADDRESS}")
    print("----------------------------------------")
    
    # Validate inputs
    if not validate_inputs():
        sys.exit(1)
    
    # Create file paths
    zone_file_path, reverse_zone_file_path, named_conf_local_path = create_file_paths()
    
    # Backup original files if they exist and if backups are enabled
    if BACKUP_FILES:
        backup_files([zone_file_path, reverse_zone_file_path, named_conf_local_path])
    
    # Create zone files
    create_zone_files(zone_file_path, reverse_zone_file_path, named_conf_local_path)
    
    # Verify configuration
    verify_configuration(zone_file_path, reverse_zone_file_path)
    
    # Restart Bind9 if enabled
    if RESTART_SERVICE:
        restart_bind9()
    
    # Print test instructions
    print_test_instructions()
    
    print("\nDNS configuration completed successfully.")

if __name__ == "__main__":
    # Check if running as root (required for file operations)
    if os.geteuid() != 0:
        print("This script must be run as root (with sudo).")
        print("Please run: sudo python3 English_version.py")
        sys.exit(1)
        
    main()
