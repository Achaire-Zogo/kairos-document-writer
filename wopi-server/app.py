from flask import Flask, request, jsonify, render_template, redirect, send_file, url_for
import os
import requests
from lxml import etree
from werkzeug.utils import secure_filename
import ssl

app = Flask(__name__)
WOPI_FILES_DIR = "./files"
ACCESS_TOKEN = "azerty123"

# Configuration pour HTTPS
SSL_ENABLED = os.environ.get('SSL_ENABLED', 'false').lower() == 'true'
SSL_KEY_FILE = os.environ.get('SSL_KEY_FILE', '')
SSL_CRT_FILE = os.environ.get('SSL_CRT_FILE', '')
DISABLE_TLS_CERT_VALIDATION = os.environ.get('DISABLE_TLS_CERT_VALIDATION', 'false').lower() == 'true'

# Fonction utilitaire pour obtenir le protocole correct
def get_protocol():
    """
    Retourne le protocole à utiliser (http ou https) en fonction de la configuration SSL.
    """
    return "https" if SSL_ENABLED else "http"

@app.route("/")
def index():
    files = os.listdir(WOPI_FILES_DIR)
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != "":
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(WOPI_FILES_DIR, filename)
        uploaded_file.save(file_path)
    return redirect("/")

def get_collabora_url(server, mime_type):
    """
    Découverte automatique des capacités de Collabora.
    Récupère l'URL appropriée pour le type MIME spécifié à partir du serveur Collabora.
    """
    # Désactiver la validation du certificat si nécessaire (ne pas utiliser en production)
    response = requests.get(f"{server}/hosting/discovery", verify=not DISABLE_TLS_CERT_VALIDATION)
    discovery = response.text
    if not discovery:
        print('Impossible de récupérer le fichier discovery.xml du serveur Collabora Online.')
        return None
    
    try:
        parsed = etree.fromstring(discovery.encode('utf-8'))
        if parsed is None:
            print('Le fichier discovery.xml récupéré n\'est pas un fichier XML valide')
            return None
        
        result = parsed.xpath(f"/wopi-discovery/net-zone/app[@name='{mime_type}']/action")
        if not result:
            # Si le type MIME exact n'est pas trouvé, essayer avec un type générique
            if '/' in mime_type:
                generic_mime = mime_type.split('/')[0] + '/'
                result = parsed.xpath(f"/wopi-discovery/net-zone/app[starts-with(@name, '{generic_mime}')]/action")
        
        if not result:
            print(f'Le type MIME demandé {mime_type} n\'est pas pris en charge')
            return None
        
        online_url = result[0].get('urlsrc')
        print('URL Collabora Online: ' + online_url)
        return online_url
    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier discovery.xml: {e}")
        return None

def get_mime_type(filename):
    """
    Détermine le type MIME en fonction de l'extension du fichier.
    """
    extension = os.path.splitext(filename)[1].lower()
    mime_types = {
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.odt': 'application/vnd.oasis.opendocument.text',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.odp': 'application/vnd.oasis.opendocument.presentation',
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.csv': 'text/csv',
        '.rtf': 'application/rtf',
    }
    return mime_types.get(extension, 'application/octet-stream')

@app.route("/open/<filename>")
def open_file(filename):
    """
    Ouvre un fichier dans Collabora Online en utilisant la découverte automatique.
    """
    from urllib.parse import quote
    
    # Déterminer le type MIME du fichier
    mime_type = get_mime_type(filename)
    
    # Déterminer le protocole à utiliser
    protocol = get_protocol()
    
    # URL du serveur Collabora (utilise le nom du service Docker en interne)
    collabora_server = "http://collabora:9980"
    
    # URL pour le navigateur (utilise localhost car c'est l'utilisateur qui y accède)
    browser_collabora = f"{protocol}://localhost:9980"
    
    # Obtenir l'URL spécifique au type MIME via la découverte Collabora
    wopi_client_url = get_collabora_url(collabora_server, mime_type)
    
    if not wopi_client_url:
        # Fallback si la découverte échoue
        wopi_client_url = f"{browser_collabora}/browser/dist/cool.html?"
    else:
        # Remplacer l'URL du serveur interne par l'URL accessible depuis le navigateur
        wopi_client_url = wopi_client_url.replace(collabora_server, browser_collabora)
    
    # URL pour Collabora (utilise le nom du service Docker 'wopi' pour l'accès inter-conteneurs)
    # Toujours utiliser HTTP pour la communication interne entre conteneurs
    wopi_src = quote(f"http://wopi:5000/wopi/files/{filename}")
    
    # Construire l'URL complète avec tous les paramètres nécessaires
    full_url = f"{wopi_client_url}WOPISrc={wopi_src}&access_token={ACCESS_TOKEN}&compat=true&permission=edit&closebutton=1&lang=fr&debug=true"
    
    print(f"Ouverture du fichier: {filename} ({mime_type}) avec l'URL: {full_url}")
    return redirect(full_url)

@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    try:
        os.remove(os.path.join(WOPI_FILES_DIR, filename))
    except Exception:
        pass
    return redirect("/")

@app.route("/rename/<oldname>", methods=["POST"])
def rename_file(oldname):
    newname = secure_filename(request.form["newname"])
    os.rename(
        os.path.join(WOPI_FILES_DIR, oldname),
        os.path.join(WOPI_FILES_DIR, newname)
    )
    return redirect("/")

# WOPI routes améliorés
@app.route("/wopi/files/<filename>", methods=["GET"])
def wopi_checkfileinfo(filename):
    """
    Endpoint WOPI CheckFileInfo amélioré avec plus de métadonnées et de capacités.
    """
    file_path = os.path.join(WOPI_FILES_DIR, filename)
    
    try:
        stat = os.stat(file_path)
        file_size = stat.st_size
        last_modified = stat.st_mtime
        
        # Déterminer le type MIME du fichier
        mime_type = get_mime_type(filename)
        
        # Obtenir l'extension du fichier
        _, extension = os.path.splitext(filename)
        extension = extension.lower()
        
        # Déterminer les capacités en fonction du type de fichier
        supports_update = True
        supports_locks = True
        user_can_write = True
        read_only = False
        
        # Certains types de fichiers peuvent être en lecture seule
        if extension in ['.pdf']:
            supports_update = False
            user_can_write = False
            read_only = True
        
        # Construire la réponse avec des métadonnées enrichies
        response = {
            "BaseFileName": filename,
            "OwnerId": "admin",
            "Size": file_size,
            "Version": str(int(last_modified)),  # Utiliser la date de modification comme version
            "LastModifiedTime": last_modified,
            "UserId": "admin",
            "UserFriendlyName": "Admin",
            "AllowExternalMarketplace": False,
            "SupportsUpdate": supports_update,
            "SupportsLocks": supports_locks,
            "UserCanWrite": user_can_write,
            "ReadOnly": read_only,
            "BreadcrumbBrandName": "Kairos Document Writer",
            "BreadcrumbBrandUrl": "/",
            "BreadcrumbFolderName": "Documents",
            "BreadcrumbFolderUrl": "/",
            "FileExtension": extension,
            "FileUrl": f"/wopi/files/{filename}/contents",
            "HostEditUrl": f"/open/{filename}",
            "HostViewUrl": f"/open/{filename}?mode=view",
        }
        
        print(f"CheckFileInfo: file id: {filename}, access token: {request.args.get('access_token', '')}")
        return jsonify(response)
        
    except Exception as e:
        print(f"Erreur dans CheckFileInfo: {e}")
        return jsonify({"error": str(e)}), 404

@app.route("/wopi/files/<filename>/contents", methods=["GET"])
def wopi_getfile(filename):
    """
    Endpoint WOPI GetFile amélioré avec gestion des erreurs et journalisation.
    """
    try:
        file_path = os.path.join(WOPI_FILES_DIR, filename)
        print(f"GetFile: file id: {filename}, access token: {request.args.get('access_token', '')}")
        return send_file(file_path)
    except Exception as e:
        print(f"Erreur dans GetFile: {e}")
        return jsonify({"error": str(e)}), 404

@app.route("/wopi/files/<filename>/contents", methods=["POST"])
def wopi_savefile(filename):
    """
    Endpoint WOPI PutFile amélioré avec gestion des erreurs, journalisation et versionnement.
    """
    try:
        file_path = os.path.join(WOPI_FILES_DIR, filename)
        print(f"PutFile: file id: {filename}, access token: {request.args.get('access_token', '')}")
        
        # Créer une sauvegarde avant d'écraser le fichier (versionnement simple)
        if os.path.exists(file_path):
            backup_dir = os.path.join(WOPI_FILES_DIR, ".backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            import time
            timestamp = int(time.time())
            backup_filename = f"{filename}.{timestamp}.bak"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"Backup créé: {backup_path}")
        
        # Écrire les nouvelles données
        with open(file_path, "wb") as f:
            content = request.get_data()
            f.write(content)
            print(f"Fichier enregistré: {filename}, taille: {len(content)} octets")
        
        return "", 200
    except Exception as e:
        print(f"Erreur dans PutFile: {e}")
        return jsonify({"error": str(e)}), 500

# Nouveaux endpoints WOPI pour la gestion des verrous
@app.route("/wopi/files/<filename>/lock", methods=["POST"])
def wopi_lock(filename):
    """
    Endpoint WOPI Lock pour la gestion des verrous d'édition collaborative.
    """
    try:
        lock_value = request.headers.get('X-WOPI-Lock', '')
        print(f"Lock: file id: {filename}, lock value: {lock_value}")
        # Dans une implémentation complète, il faudrait stocker ce verrou
        return "", 200
    except Exception as e:
        print(f"Erreur dans Lock: {e}")
        return "", 500

@app.route("/wopi/files/<filename>/unlock", methods=["POST"])
def wopi_unlock(filename):
    """
    Endpoint WOPI Unlock pour libérer les verrous d'édition collaborative.
    """
    try:
        lock_value = request.headers.get('X-WOPI-Lock', '')
        print(f"Unlock: file id: {filename}, lock value: {lock_value}")
        # Dans une implémentation complète, il faudrait vérifier et supprimer ce verrou
        return "", 200
    except Exception as e:
        print(f"Erreur dans Unlock: {e}")
        return "", 500

# Amélioration de l'interface utilisateur
@app.route("/view/<filename>")
def view_file(filename):
    """
    Ouvre un fichier en mode lecture seule dans Collabora Online.
    """
    from urllib.parse import quote
    
    # Déterminer le type MIME du fichier
    mime_type = get_mime_type(filename)
    
    # Déterminer le protocole à utiliser
    protocol = get_protocol()
    
    # URL du serveur Collabora (utilise le nom du service Docker en interne)
    collabora_server = "http://collabora:9980"
    
    # URL pour le navigateur (utilise localhost car c'est l'utilisateur qui y accède)
    browser_collabora = f"{protocol}://localhost:9980"
    
    wopi_client_url = get_collabora_url(collabora_server, mime_type)
    
    if not wopi_client_url:
        wopi_client_url = f"{browser_collabora}/browser/dist/cool.html?"
    else:
        wopi_client_url = wopi_client_url.replace(collabora_server, browser_collabora)
    
    # URL pour Collabora (utilise le nom du service Docker 'wopi' pour l'accès inter-conteneurs)
    # Toujours utiliser HTTP pour la communication interne entre conteneurs
    wopi_src = quote(f"http://wopi:5000/wopi/files/{filename}")
    
    full_url = f"{wopi_client_url}WOPISrc={wopi_src}&access_token={ACCESS_TOKEN}&permission=readonly&closebutton=1&lang=fr"
    
    print(f"Visualisation du fichier: {filename} ({mime_type}) avec l'URL: {full_url}")
    return redirect(full_url)

# Fonction pour démarrer le serveur avec ou sans SSL
def run_server_with_ssl():
    """
    Démarre le serveur Flask avec ou sans support SSL en fonction de la configuration.
    """
    os.makedirs(WOPI_FILES_DIR, exist_ok=True)
    
    if SSL_ENABLED and SSL_KEY_FILE and SSL_CRT_FILE:
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(SSL_CRT_FILE, SSL_KEY_FILE)
            print(f"Démarrage du serveur HTTPS sur le port 5000 avec SSL")
            app.run(host="0.0.0.0", port=5000, ssl_context=context)
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur HTTPS: {e}")
            print("Démarrage du serveur en mode HTTP")
            app.run(host="0.0.0.0", port=5000)
    else:
        print("Démarrage du serveur HTTP sur le port 5000")
        app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    run_server_with_ssl()
