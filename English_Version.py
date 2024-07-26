import os
from shutil import copyfile
# Define the paths to the zone files and the named.conf.local file
zone_file_path = '/etc/bind/db.integris.ptt'
reverse_zone_file_path = '/etc/bind/db.192.168.183'
named_conf_local_path = '/etc/bind/named.conf.local'
# Define the content for the forward zone file
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
# Define the content for the reverse zone file
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
# Define the content to be appended to named.conf.local for the new zones
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
# Function to create and write the zone files and named.conf.local
def create_zone_files():
    with open(zone_file_path, 'w') as zone_file:
        zone_file.write(zone_file_content)
    with open(reverse_zone_file_path, 'w') as reverse_zone_file:
        reverse_zone_file.write(reverse_zone_file_content)
    with open(named_conf_local_path, 'a') as named_conf_local:
        named_conf_local.write(named_conf_local_content)
# Function to restart the Bind9 service
def restart_bind9():
    os.system('sudo systemctl restart bind9')
# Main function to backup existing files, create new files, and restart Bind9
def main():
    # Backup original files if they exist
    if os.path.exists(zone_file_path):
        copyfile(zone_file_path, f"{zone_file_path}.bak")
    if os.path.exists(reverse_zone_file_path):
        copyfile(reverse_zone_file_path, f"{reverse_zone_file_path}.bak")
    if os.path.exists(named_conf_local_path):
        copyfile(named_conf_local_path, f"{named_conf_local_path}.bak")
    # Create new zone files and append to named.conf.local
    create_zone_files()
    # Restart Bind9 to apply the new configuration
    restart_bind9()
    print("DNS configuration applied successfully.")
# Run the main function when the script is executed
if __name__ == "__main__":
    main()
