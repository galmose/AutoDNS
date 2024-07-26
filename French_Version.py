import os
from shutil import copyfile
# Chemins des fichiers de zone DNS et du fichier de configuration local de Bind
zone_file_path = '/etc/bind/db.integris.ptt'
reverse_zone_file_path = '/etc/bind/db.192.168.183'
named_conf_local_path = '/etc/bind/named.conf.local'
# Contenu du fichier de zone directe pour integris.ptt
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
# Contenu du fichier de zone inverse pour le réseau 192.168.183
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
# Contenu à ajouter dans le fichier named.conf.local pour lier les fichiers de zone
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
# Fonction pour créer les fichiers de zone
def create_zone_files():
    # Écriture du fichier de zone directe
    with open(zone_file_path, 'w') as zone_file:
        zone_file.write(zone_file_content)
    # Écriture du fichier de zone inverse
    with open(reverse_zone_file_path, 'w') as reverse_zone_file:
        reverse_zone_file.write(reverse_zone_file_content)
    # Ajout de la configuration des zones dans named.conf.local
    with open(named_conf_local_path, 'a') as named_conf_local:
        named_conf_local.write(named_conf_local_content)
# Fonction pour redémarrer le service Bind9
def restart_bind9():
    os.system('sudo systemctl restart bind9')
# Fonction principale
def main():
    # Sauvegarder les fichiers originaux s'ils existent
    if os.path.exists(zone_file_path):
        copyfile(zone_file_path, f"{zone_file_path}.bak")
    if os.path.exists(reverse_zone_file_path):
        copyfile(reverse_zone_file_path, f"{reverse_zone_file_path}.bak")
    if os.path.exists(named_conf_local_path):
        copyfile(named_conf_local_path, f"{named_conf_local_path}.bak")
    # Créer les fichiers de zone et redémarrer Bind9
    create_zone_files()
    restart_bind9()
    print("DNS configuration applied successfully.")
# Point d'entrée du script
if __name__ == "__main__":
    main()
