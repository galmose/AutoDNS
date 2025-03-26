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

```

## Personnalisation du Script

Avant d'exécuter le script, vous devrez l'adapter à votre environnement spécifique. Voici les principales variables à modifier:

### 1. Adresse IP et Nom de Domaine

Dans les scripts, recherchez et modifiez les valeurs suivantes:

```python
# Dans la version anglaise (English_version.py)
IP_ADDRESS = "192.168.183.17"
DOMAIN_NAME = "integris.ptt"

# Dans la version française (French_version.py)
ADRESSE_IP = "192.168.183.17"
NOM_DOMAINE = "integris.ptt"
```

### 2. Options de Configuration Supplémentaires

Les scripts offrent des options supplémentaires pour personnaliser leur comportement :

```python
# Dans la version anglaise (English_version.py)
BACKUP_FILES = True       # Créer des sauvegardes des fichiers existants
RESTART_SERVICE = True    # Redémarrer le service Bind9 après configuration
ADD_SAMPLE_RECORDS = True # Ajouter des exemples d'enregistrements DNS

# Dans la version française (French_version.py)
CREER_SAUVEGARDES = True    # Créer des sauvegardes des fichiers existants
REDEMARRER_SERVICE = True   # Redémarrer le service Bind9 après configuration
AJOUTER_EXEMPLES = True     # Ajouter des exemples d'enregistrements DNS
```

### 3. Chemins des Fichiers de Zone

Les chemins des fichiers sont générés automatiquement en fonction du nom de domaine et de l'adresse IP :

```python
# La fonction crée automatiquement les chemins suivants
zone_file_path = f'/etc/bind/db.{DOMAIN_NAME}'
ip_prefix = '.'.join(IP_ADDRESS.split('.')[:3])
reverse_zone_file_path = f'/etc/bind/db.{ip_prefix}'
named_conf_local_path = '/etc/bind/named.conf.local'
```

### 4. Configuration des Enregistrements DNS

Si l'option `ADD_SAMPLE_RECORDS` (ou `AJOUTER_EXEMPLES` dans la version française) est activée, le script ajoute automatiquement plusieurs enregistrements DNS d'exemple. Vous pouvez personnaliser cette fonction pour ajouter vos propres enregistrements :

```python
# Dans la fonction generate_forward_zone_content() / generer_contenu_zone_directe()
# Vous pouvez modifier cette section pour ajouter vos propres enregistrements
if ADD_SAMPLE_RECORDS:  # ou AJOUTER_EXEMPLES dans la version française
    content += f"""www     IN      A       {IP_ADDRESS}
mail    IN      A       {IP_ADDRESS}
webmail IN      CNAME   mail.{DOMAIN_NAME}.
"""
    
# Pour ajouter d'autres enregistrements personnalisés, modifiez cette section
# Exemples :
# content += f"""ftp     IN      A       {IP_ADDRESS}
# serveur1 IN     A       192.168.183.18
# serveur2 IN     A       192.168.183.19
# """
```

### 5. Configuration de la Zone Inverse

De même, vous pouvez personnaliser les enregistrements PTR dans la fonction qui génère la zone inverse :

```python
# Dans la fonction generate_reverse_zone_content() / generer_contenu_zone_inverse()
# Le script génère automatiquement les enregistrements PTR pour les enregistrements standard
if ADD_SAMPLE_RECORDS:  # ou AJOUTER_EXEMPLES dans la version française
    content += f"{ptr_name}  IN      PTR     ns.{DOMAIN_NAME}.\n"
    content += f"{ptr_name}  IN      PTR     www.{DOMAIN_NAME}.\n"
    content += f"{ptr_name}  IN      PTR     mail.{DOMAIN_NAME}.\n"

# Pour ajouter des enregistrements PTR personnalisés pour d'autres serveurs
# Exemple pour serveur1 avec IP 192.168.183.18:
# content += f"18.183.168.192.in-addr.arpa.  IN PTR serveur1.{DOMAIN_NAME}.\n"
```

Les scripts génèrent automatiquement la structure correcte pour les enregistrements PTR, ce qui évite les erreurs courantes de syntaxe.

## Exécution du Script

Les scripts améliorés vérifient automatiquement s'ils sont exécutés avec les privilèges administrateur nécessaires, et affichent un message d'erreur approprié le cas échéant.

1. **Rendez le script exécutable**:

```bash
chmod +x English_version.py
# ou
chmod +x French_version.py
```

2. **Exécutez le script avec privilèges administrateur**:

```bash
sudo python3 English_version.py
# ou
sudo python3 French_version.py
```

3. **Suivez les instructions à l'écran**:

Le script vous guidera à travers les étapes suivantes:
- Vérification des paramètres
- Création des sauvegardes (si activé)
- Création des fichiers de zone
- Vérification de la configuration
- Redémarrage du service Bind9 (si activé)
- Affichage des instructions de test détaillées

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

Après l'exécution du script, des instructions de test détaillées sont automatiquement affichées. Le script effectue également des vérifications de base avec les commandes `named-checkzone` et `named-checkconf` pour s'assurer que la configuration est syntaxiquement correcte.

Pour vérifier manuellement que votre serveur DNS fonctionne correctement, suivez les tests ci-dessous:

### 1. Vérifier la Résolution DNS Directe

```bash
dig @192.168.183.17 integris.ptt
# Remplacez par votre IP et votre domaine
```

Résultat attendu: L'adresse IP associée au domaine est correctement renvoyée dans la section "ANSWER SECTION".

### 2. Vérifier la Résolution DNS Inverse

```bash
dig @192.168.183.17 -x 192.168.183.17
# Remplacez par votre IP
```

Résultat attendu: Le nom de domaine associé à l'adresse IP est correctement renvoyé dans un enregistrement PTR.

### 3. Tester la Connectivité avec Ping

```bash
ping integris.ptt
# Remplacez par votre domaine
```
Resultat du test de

```bash
root@Ubuntu:/etc/bind# ping integris.ptt
PING integris.ptt (192.168.183.17) 56(84) bytes of data.
64 bytes from www.integris.ptt (192.168.183.17): icmp_seq=1 ttl=64 time=0.086 ms
64 bytes from www.integris.ptt (192.168.183.17): icmp_seq=2 ttl=64 time=0.034 ms
64 bytes from www.integris.ptt (192.168.183.17): icmp_seq=3 ttl=64 time=0.168 ms
64 bytes from www.integris.ptt (192.168.183.17): icmp_seq=4 ttl=64 time=0.177 ms
64 bytes from www.integris.ptt (192.168.183.17): icmp_seq=5 ttl=64 time=0.084 ms
^C
--- integris.ptt ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4056ms
rtt min/avg/max/mdev = 0.034/0.109/0.177/0.054 ms
root@Ubuntu:/etc/bind#
```
Résultat attendu: Le ping fonctionne et l'hôte répond, avec le nom de domaine correctement résolu dans la réponse.

### 4. Vérifier l'État du Serveur DNS

```bash
sudo systemctl status bind9
```

## Dépannage

Les scripts incluent désormais des vérifications automatiques de la configuration pour détecter les problèmes courants. Voici comment résoudre les problèmes les plus fréquents :

### Problème 1: Bind9 ne démarre pas

**Symptôme**: Le message d'erreur "Failed to restart Bind9 service" s'affiche.

**Solution**:
1. Vérifiez l'état du service:
   ```bash
   sudo systemctl status bind9
   ```

2. Consultez les journaux pour identifier l'erreur:
   ```bash
   sudo journalctl -xe | grep named
   ```

3. Problèmes courants:
   - Syntaxe incorrecte dans les fichiers de configuration
   - Permissions de fichier incorrectes
   - Nom de domaine ou IP déjà utilisés par un autre service

### Problème 2: Erreurs de syntaxe dans les fichiers de zone

**Symptôme**: Les vérifications automatiques avec `named-checkzone` échouent.

**Solution**:
1. Vérifiez manuellement les fichiers de zone:
   ```bash
   sudo named-checkzone integris.ptt /etc/bind/db.integris.ptt
   sudo named-checkzone 183.168.192.in-addr.arpa /etc/bind/db.192.168.183
   ```

2. Erreurs courantes:
   - Oubli du point final après les noms de domaine
   - Format incorrect des enregistrements PTR
   - Numéro de série non incrémenté après modifications

### Problème 3: La résolution DNS ne fonctionne pas

**Symptôme**: Les commandes `dig` ou `ping` ne fonctionnent pas comme prévu.

**Solution**:

1. Vérifiez que Bind9 écoute sur la bonne interface:
   ```bash
   sudo netstat -tulpn | grep named
   ```

2. Vérifiez les paramètres du pare-feu:
   ```bash
   sudo ufw status
   ```

3. Si nécessaire, autorisez le trafic DNS:
   ```bash
   sudo ufw allow 53/tcp
   sudo ufw allow 53/udp
   ```

4. Vérifiez le fichier `/etc/resolv.conf`:
   ```bash
   cat /etc/resolv.conf
   ```
   Assurez-vous qu'il contient:
   ```
   nameserver 192.168.183.17
   search integris.ptt
   ```

## Contribution au Projet

Les contributions à ce projet sont les bienvenues. Pour contribuer:

1. Forkez ce dépôt
2. Créez une branche pour votre fonctionnalité
3. Soumettez une pull request

## Licence

Ce projet est sous licence MIT. 

### Licence MIT

```
MIT License

Copyright (c) 2025 AutoDNS Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Cette licence permet :
- L'utilisation commerciale
- La modification
- La distribution
- L'utilisation privée

Les utilisateurs doivent simplement inclure la notice de copyright et la permission ci-dessus dans toutes les copies ou parties substantielles du logiciel.

## Fonctionnalités avancées

Les scripts incluent plusieurs fonctionnalités avancées que vous pouvez explorer :

### Validation des paramètres

Les scripts vérifient automatiquement la validité de l'adresse IP et du nom de domaine avant de procéder à la configuration.

### Génération automatique des fichiers

Les chemins de fichiers et leur contenu sont générés dynamiquement en fonction de l'adresse IP et du nom de domaine fournis.

### Sauvegarde automatique

Les fichiers existants sont automatiquement sauvegardés avant d'être modifiés, ce qui permet de revenir facilement à une configuration antérieure.

### Vérification intégrée

Les scripts utilisent les outils `named-checkzone` et `named-checkconf` pour vérifier la validité de la configuration avant de redémarrer le service.

## Auteurs

- [Tidiane SAVADOGO] - Développeur principal

## Remerciements

- Merci à tous les contributeurs et testeurs
- Équipe de documentation pour la création du README.md détaillé
- Communauté Bind9 pour les excellentes ressources de documentation
