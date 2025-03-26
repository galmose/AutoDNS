# AutoDNS - Outil de Configuration Automatisée de Serveur DNS

```
                     _             _____    _   _    _____ 
     /\             | |           |  __ \  | \ | |  / ____|
    /  \     _   _  | |_    ___   | |  | | |  \| | | (___  
   / /\ \   | | | | | __|  / _ \  | |  | | | . ` |  \___ \ 
  / ____ \  | |_| | | |_  | (_) | | |__| | | |\  |  ____) |
 /_/    \_\  \__,_|  \__|  \___/  |_____/  |_| \_| |_____/ 
```

## Description du Projet

AutoDNS est un outil qui automatise la configuration d'un serveur DNS basé sur Bind9 sous Ubuntu. Il génère automatiquement les fichiers de zone nécessaires pour les résolutions DNS directes et inverses, met à jour la configuration de Bind9, et redémarre le service pour appliquer les changements.

Ce dépôt contient deux versions du script (`English_version.py` et `French_version.py`), qui offrent les mêmes fonctionnalités mais avec des interfaces utilisateur dans des langues différentes.

## Prérequis

Avant d'utiliser ce script, assurez-vous d'avoir installé les dépendances suivantes:

- **Ubuntu** (recommandé: 18.04 LTS ou plus récent)
- **Python 3.x**
- **Bind9**
- **dnspython**
- **Privilèges administrateur** (sudo)

## Installation des Dépendances

1. **Mise à jour du système et installation de Bind9**:

```bash
sudo apt update
sudo apt install -y bind9 bind9utils bind9-doc
```

2. **Installation de dnspython**:

```bash
pip install dnspython
```

## Structure du Projet

```
autodns/
├── English_version.py      # Script en anglais
├── French_version.py       # Script en français
├── README.md               # Ce fichier
└── exemples/               # Exemples de configurations
```

## Personnalisation du Script

Avant d'exécuter le script, vous devrez l'adapter à votre environnement spécifique. Voici les principales variables à modifier:

### 1. Adresse IP et Nom de Domaine

Dans les scripts, recherchez et modifiez les valeurs suivantes:

```python
# Remplacez par votre adresse IP
IP_ADDRESS = "192.168.183.17"

# Remplacez par votre nom de domaine
DOMAIN_NAME = "integris.ptt"
```

### 2. Chemins des Fichiers de Zone

Si nécessaire, vous pouvez également modifier les chemins des fichiers de zone:

```python
# Chemin du fichier de zone directe
zone_file_path = f'/etc/bind/db.{DOMAIN_NAME}'

# Chemin du fichier de zone inverse
# Extrait les 3 premiers octets de l'adresse IP
ip_prefix = '.'.join(IP_ADDRESS.split('.')[:3])
reverse_zone_file_path = f'/etc/bind/db.{ip_prefix}'

# Chemin du fichier de configuration local de Bind9
named_conf_local_path = '/etc/bind/named.conf.local'
```

### 3. Configuration des Enregistrements DNS

Vous pouvez ajouter, modifier ou supprimer des enregistrements DNS dans les sections suivantes:

```python
zone_file_content = f"""
$TTL    604800
@       IN      SOA     ns.{DOMAIN_NAME}. root.{DOMAIN_NAME}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{DOMAIN_NAME}.
ns      IN      A       {IP_ADDRESS}
www     IN      A       {IP_ADDRESS}  
@       IN      A       {IP_ADDRESS}

# Ajoutez vos enregistrements personnalisés ici
# Exemple:
# mail    IN      A       {IP_ADDRESS}
# ftp     IN      A       {IP_ADDRESS}
# serveur1 IN     A       192.168.183.18
"""
```

### 4. Configuration de la Zone Inverse

De même, vous pouvez personnaliser la zone inverse:

```python
reverse_zone_file_content = f"""
$TTL    604800
@       IN      SOA     ns.{DOMAIN_NAME}. root.{DOMAIN_NAME}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{DOMAIN_NAME}.
{IP_ADDRESS.split('.')[-1]}.{reverse_prefix}.in-addr.arpa.  IN PTR www.{DOMAIN_NAME}.

# Ajoutez vos enregistrements PTR personnalisés ici
# Exemple pour serveur1 avec IP 192.168.183.18:
# 18.{reverse_prefix}.in-addr.arpa.  IN PTR serveur1.{DOMAIN_NAME}.
"""
```

## Exécution du Script

1. **Rendez le script exécutable**:

```bash
sudo chmod +x English_version.py
# ou
sudo chmod +x French_version.py
```

2. **Exécutez le script avec privilèges administrateur**:

```bash
sudo python3 English_version.py
# ou
sudo python3 French_version.py
```

## Configuration du Client DNS

Pour que votre système utilise ce serveur DNS, vous devez mettre à jour le fichier `/etc/resolv.conf`:

```bash
sudo nano /etc/resolv.conf
```

Ajoutez les lignes suivantes (à adapter à votre configuration):

```
nameserver 192.168.183.17
search integris.ptt
```

Pour rendre cette configuration permanente (elle peut être écrasée par le système), vous pouvez utiliser `resolvconf`:

```bash
sudo apt install resolvconf
sudo nano /etc/resolvconf/resolv.conf.d/base
```

Ajoutez les mêmes lignes que précédemment et mettez à jour:

```bash
sudo resolvconf -u
```

## Vérification de la Configuration

Après l'exécution du script, effectuez les tests suivants pour vérifier que votre serveur DNS fonctionne correctement:

### 1. Vérifier la Résolution DNS Directe

```bash
dig @192.168.183.17 integris.ptt
# Remplacez par votre IP et votre domaine
```

Résultat attendu: L'adresse IP associée au domaine est correctement renvoyée.

### 2. Vérifier la Résolution DNS Inverse

```bash
dig @192.168.183.17 -x 192.168.183.17
# Remplacez par votre IP
```

Résultat attendu: Le nom de domaine associé à l'adresse IP est correctement renvoyé.

### 3. Tester la Connectivité avec Ping

```bash
ping integris.ptt
# Remplacez par votre domaine
```

Résultat attendu: Le ping fonctionne et l'hôte répond.

### 4. Vérifier l'État du Serveur DNS

```bash
sudo systemctl status bind9
sudo named-checkzone integris.ptt /etc/bind/db.integris.ptt
sudo named-checkconf
```

## Exemples de Configurations Personnalisées

### Exemple 1: Configuration avec Plusieurs Sous-domaines

Modifiez le contenu du fichier de zone directe:

```python
zone_file_content = f"""
$TTL    604800
@       IN      SOA     ns.{DOMAIN_NAME}. root.{DOMAIN_NAME}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{DOMAIN_NAME}.
ns      IN      A       {IP_ADDRESS}
www     IN      A       {IP_ADDRESS}  
@       IN      A       {IP_ADDRESS}
mail    IN      A       {IP_ADDRESS}
webmail IN      A       {IP_ADDRESS}
cloud   IN      A       {IP_ADDRESS}
svn     IN      A       {IP_ADDRESS}
git     IN      A       {IP_ADDRESS}
"""
```

### Exemple 2: Configuration avec Plusieurs Serveurs

```python
zone_file_content = f"""
$TTL    604800
@       IN      SOA     ns.{DOMAIN_NAME}. root.{DOMAIN_NAME}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{DOMAIN_NAME}.
ns      IN      A       {IP_ADDRESS}
www     IN      A       {IP_ADDRESS}  
@       IN      A       {IP_ADDRESS}
serveur1 IN     A       192.168.183.18
serveur2 IN     A       192.168.183.19
"""

# N'oubliez pas d'ajouter les enregistrements PTR correspondants dans la zone inverse
```

### Exemple 3: Configuration avec CNAME

```python
zone_file_content = f"""
$TTL    604800
@       IN      SOA     ns.{DOMAIN_NAME}. root.{DOMAIN_NAME}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{DOMAIN_NAME}.
ns      IN      A       {IP_ADDRESS}
www     IN      A       {IP_ADDRESS}  
@       IN      A       {IP_ADDRESS}
webmail IN      CNAME   www.{DOMAIN_NAME}.
docs    IN      CNAME   www.{DOMAIN_NAME}.
"""
```

## Dépannage

### Problème 1: Bind9 ne démarre pas

```bash
sudo systemctl status bind9
```

Vérifiez les journaux pour plus d'informations:

```bash
sudo journalctl -xe | grep named
```

### Problème 2: Erreurs de syntaxe dans les fichiers de zone

Utilisez les outils de vérification de Bind9:

```bash
sudo named-checkzone integris.ptt /etc/bind/db.integris.ptt
sudo named-checkzone 183.168.192.in-addr.arpa /etc/bind/db.192.168.183
```

### Problème 3: La résolution DNS ne fonctionne pas

1. Vérifiez que Bind9 écoute sur la bonne interface:

```bash
sudo netstat -tulpn | grep named
```

2. Vérifiez les paramètres du pare-feu:

```bash
sudo ufw status
```

Si nécessaire, autorisez le trafic DNS:

```bash
sudo ufw allow 53/tcp
sudo ufw allow 53/udp
```

## Contribution au Projet

Les contributions à ce projet sont les bienvenues. Pour contribuer:

1. Forkez ce dépôt
2. Créez une branche pour votre fonctionnalité
3. Soumettez une pull request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Auteurs

- [Votre Nom] - Développeur principal

## Remerciements

- Merci à tous les contributeurs et testeurs
