#!/usr/bin/env python3
"""
AutoDNS - Script de Configuration de Serveur DNS
------------------------------------------------
Ce script automatise la configuration d'un serveur DNS Bind9 sur les systèmes Ubuntu.
Il crée les fichiers de zone nécessaires pour les résolutions DNS directes et inverses,
met à jour la configuration de Bind9 et redémarre le service pour appliquer les changements.
"""

import os
import sys
from shutil import copyfile
import ipaddress
import socket

# Paramètres configurables par l'utilisateur - MODIFIEZ CES VALEURS POUR VOTRE CONFIGURATION
ADRESSE_IP = "192.168.183.17"
NOM_DOMAINE = "integris.ptt"

# Options de configuration supplémentaires
CREER_SAUVEGARDES = True    # Créer une sauvegarde des fichiers existants
REDEMARRER_SERVICE = True   # Redémarrer le service Bind9 après la configuration
AJOUTER_EXEMPLES = True     # Ajouter des exemples d'enregistrements DNS (www, mail, etc.)

def valider_parametres():
    """Valider l'adresse IP et le nom de domaine."""
    # Valider l'adresse IP
    try:
        ipaddress.ip_address(ADRESSE_IP)
    except ValueError:
        print(f"Erreur : '{ADRESSE_IP}' n'est pas une adresse IP valide.")
        return False
    
    # Validation basique du nom de domaine
    if not NOM_DOMAINE or '.' not in NOM_DOMAINE:
        print(f"Erreur : '{NOM_DOMAINE}' ne semble pas être un nom de domaine valide.")
        return False
        
    return True

def obtenir_prefixe_zone_inverse():
    """Extraire le préfixe de zone inverse à partir de l'adresse IP."""
    octets = ADRESSE_IP.split('.')
    prefixe_inverse = '.'.join(octets[0:3][::-1])  # 3 premiers octets dans l'ordre inverse
    return prefixe_inverse

def obtenir_nom_ptr():
    """Obtenir le nom d'enregistrement PTR pour le DNS inverse."""
    octets = ADRESSE_IP.split('.')
    return f"{octets[3]}.{obtenir_prefixe_zone_inverse()}.in-addr.arpa."

def creer_chemins_fichiers():
    """Créer les chemins de fichiers basés sur le nom de domaine et l'adresse IP."""
    # Chemin du fichier de zone directe
    chemin_fichier_zone = f'/etc/bind/db.{NOM_DOMAINE}'
    
    # Extraire la partie réseau de l'IP pour la zone inverse
    prefixe_ip = '.'.join(ADRESSE_IP.split('.')[:3])
    chemin_fichier_zone_inverse = f'/etc/bind/db.{prefixe_ip}'
    
    # Chemin de configuration local de Bind9
    chemin_named_conf_local = '/etc/bind/named.conf.local'
    
    return chemin_fichier_zone, chemin_fichier_zone_inverse, chemin_named_conf_local

def generer_contenu_zone_directe():
    """Générer le contenu du fichier de zone directe."""
    contenu = f"""$TTL    604800
@       IN      SOA     ns.{NOM_DOMAINE}. root.{NOM_DOMAINE}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{NOM_DOMAINE}.
ns      IN      A       {ADRESSE_IP}
@       IN      A       {ADRESSE_IP}
"""

    # Ajouter des exemples d'enregistrements si configuré
    if AJOUTER_EXEMPLES:
        contenu += f"""www     IN      A       {ADRESSE_IP}
mail    IN      A       {ADRESSE_IP}
webmail IN      CNAME   mail.{NOM_DOMAINE}.
"""
    
    return contenu

def generer_contenu_zone_inverse():
    """Générer le contenu du fichier de zone inverse."""
    prefixe_inverse = obtenir_prefixe_zone_inverse()
    nom_ptr = obtenir_nom_ptr()
    
    contenu = f"""$TTL    604800
@       IN      SOA     ns.{NOM_DOMAINE}. root.{NOM_DOMAINE}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{NOM_DOMAINE}.
{nom_ptr}  IN      PTR     {NOM_DOMAINE}.
"""

    # Ajouter des entrées PTR supplémentaires si les exemples sont activés
    if AJOUTER_EXEMPLES:
        contenu += f"{nom_ptr}  IN      PTR     ns.{NOM_DOMAINE}.\n"
        contenu += f"{nom_ptr}  IN      PTR     www.{NOM_DOMAINE}.\n"
        contenu += f"{nom_ptr}  IN      PTR     mail.{NOM_DOMAINE}.\n"
    
    return contenu

def generer_contenu_named_conf(chemin_fichier_zone, chemin_fichier_zone_inverse):
    """Générer le contenu pour named.conf.local."""
    # Extraire le nom de zone inverse à partir de l'adresse IP (ex: 183.168.192.in-addr.arpa)
    parties_ip = ADRESSE_IP.split('.')
    zone_inverse = f"{parties_ip[2]}.{parties_ip[1]}.{parties_ip[0]}.in-addr.arpa"
    
    contenu = f"""
zone "{NOM_DOMAINE}" {{
    type master;
    file "{chemin_fichier_zone}";
}};

zone "{zone_inverse}" {{
    type master;
    file "{chemin_fichier_zone_inverse}";
}};
"""
    return contenu

def creer_fichiers_zone(chemin_fichier_zone, chemin_fichier_zone_inverse, chemin_named_conf_local):
    """Créer les fichiers de zone et mettre à jour named.conf.local."""
    # Générer le contenu des fichiers
    contenu_fichier_zone = generer_contenu_zone_directe()
    contenu_fichier_zone_inverse = generer_contenu_zone_inverse()
    contenu_named_conf_local = generer_contenu_named_conf(chemin_fichier_zone, chemin_fichier_zone_inverse)
    
    # Écrire le fichier de zone directe
    with open(chemin_fichier_zone, 'w') as fichier_zone:
        fichier_zone.write(contenu_fichier_zone)
    print(f"Fichier de zone directe créé : {chemin_fichier_zone}")
    
    # Écrire le fichier de zone inverse
    with open(chemin_fichier_zone_inverse, 'w') as fichier_zone_inverse:
        fichier_zone_inverse.write(contenu_fichier_zone_inverse)
    print(f"Fichier de zone inverse créé : {chemin_fichier_zone_inverse}")
    
    # Ajouter les configurations de zone à named.conf.local
    with open(chemin_named_conf_local, 'a') as named_conf_local:
        named_conf_local.write(contenu_named_conf_local)
    print(f"Configuration Bind9 mise à jour : {chemin_named_conf_local}")

def redemarrer_bind9():
    """Redémarrer le service Bind9."""
    print("Redémarrage du service Bind9...")
    resultat = os.system('sudo systemctl restart bind9')
    
    if resultat == 0:
        print("Service Bind9 redémarré avec succès.")
    else:
        print("Échec du redémarrage du service Bind9. Vérifiez les journaux avec : sudo journalctl -xe | grep named")

def sauvegarder_fichiers(fichiers):
    """Créer des sauvegardes des fichiers existants."""
    for chemin_fichier in fichiers:
        if os.path.exists(chemin_fichier):
            chemin_sauvegarde = f"{chemin_fichier}.bak"
            copyfile(chemin_fichier, chemin_sauvegarde)
            print(f"Sauvegarde créée : {chemin_sauvegarde}")

def verifier_configuration(chemin_fichier_zone, chemin_fichier_zone_inverse):
    """Vérifier la configuration DNS à l'aide de named-checkzone."""
    print("\nVérification de la configuration...")
    
    # Vérifier la zone directe
    os.system(f"sudo named-checkzone {NOM_DOMAINE} {chemin_fichier_zone}")
    
    # Extraire le nom de zone inverse à partir de l'IP
    parties_ip = ADRESSE_IP.split('.')
    zone_inverse = f"{parties_ip[2]}.{parties_ip[1]}.{parties_ip[0]}.in-addr.arpa"
    
    # Vérifier la zone inverse
    os.system(f"sudo named-checkzone {zone_inverse} {chemin_fichier_zone_inverse}")
    
    # Vérifier la configuration named
    os.system("sudo named-checkconf")

def afficher_instructions_test():
    """Afficher les instructions pour tester la configuration DNS."""
    print("\n----- INSTRUCTIONS DE TEST -----")
    print("Pour tester votre configuration DNS, exécutez les commandes suivantes :")
    print(f"\n1. Vérifier la résolution DNS directe :")
    print(f"   dig @{ADRESSE_IP} {NOM_DOMAINE}")
    
    print(f"\n2. Vérifier la résolution DNS inverse :")
    print(f"   dig @{ADRESSE_IP} -x {ADRESSE_IP}")
    
    print(f"\n3. Tester avec ping :")
    print(f"   ping {NOM_DOMAINE}")
    
    print("\n4. Mettre à jour votre resolv.conf (si nécessaire) :")
    print(f"   echo 'nameserver {ADRESSE_IP}' | sudo tee /etc/resolv.conf")
    print(f"   echo 'search {NOM_DOMAINE}' | sudo tee -a /etc/resolv.conf")

def main():
    """Fonction principale."""
    print("========================================")
    print("    Outil de Configuration AutoDNS      ")
    print("========================================")
    print(f"Domaine : {NOM_DOMAINE}")
    print(f"Adresse IP : {ADRESSE_IP}")
    print("----------------------------------------")
    
    # Valider les paramètres
    if not valider_parametres():
        sys.exit(1)
    
    # Créer les chemins de fichiers
    chemin_fichier_zone, chemin_fichier_zone_inverse, chemin_named_conf_local = creer_chemins_fichiers()
    
    # Sauvegarder les fichiers originaux s'ils existent et si les sauvegardes sont activées
    if CREER_SAUVEGARDES:
        sauvegarder_fichiers([chemin_fichier_zone, chemin_fichier_zone_inverse, chemin_named_conf_local])
    
    # Créer les fichiers de zone
    creer_fichiers_zone(chemin_fichier_zone, chemin_fichier_zone_inverse, chemin_named_conf_local)
    
    # Vérifier la configuration
    verifier_configuration(chemin_fichier_zone, chemin_fichier_zone_inverse)
    
    # Redémarrer Bind9 si activé
    if REDEMARRER_SERVICE:
        redemarrer_bind9()
    
    # Afficher les instructions de test
    afficher_instructions_test()
    
    print("\nConfiguration DNS terminée avec succès.")

if __name__ == "__main__":
    # Vérifier si exécuté en tant que root (requis pour les opérations sur les fichiers)
    if os.geteuid() != 0:
        print("Ce script doit être exécuté en tant que root (avec sudo).")
        print("Veuillez exécuter : sudo python3 French_version.py")
        sys.exit(1)
        
    main()
