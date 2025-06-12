📝 Collabora Online + WOPI Server (Custom App)

Ce projet montre comment créer un serveur WOPI personnalisé en Python (avec Flask) pour utiliser Collabora Online (CODE) comme visionneuse/éditeur de documents, sans dépendre de Nextcloud ou d'autres outils.
.

📦 Fonctionnalités
Interface simple pour :

Télécharger un document .docx

Lister les fichiers disponibles

Ouvrir un document dans Collabora Online

Supprimer ou renommer un fichier

Utilise un serveur WOPI custom pour fournir les fichiers à Collabora.

Docker Compose pour tout orchestrer.


📁 Structure du projet
```
.
├── docker-compose.yml
├── wopi-server
│   ├── app.py
│   ├── Dockerfile
│   └── files
│       └── example.docx
└── README.md
```

🚀 Lancement rapide

git clone https://github.com/your-repo-url.git
cd <repo-folder>

```bash
docker-compose up --build
```

Accéder à l'interface :
👉 http://localhost:5000


🔍 Comment ça marche
Collabora Online (CODE)
Collabora expose un éditeur web (loleaflet.html) à http://localhost:9980

Ce frontend attend un paramètre WOPISrc (vers le fichier via le serveur WOPI)

Un access_token est aussi requis pour la sécurité.

Serveur WOPI (Flask)
Le serveur wopi-server/app.py implémente trois endpoints principaux du protocole WOPI :

| Endpoint                               | Fonction                                             |
| -------------------------------------- | ---------------------------------------------------- |
| `/wopi/files/<filename>`               | Retourne les métadonnées du fichier                  |
| `/wopi/files/<filename>/contents` GET  | Sert le contenu du fichier                           |
| `/wopi/files/<filename>/contents` POST | Reçoit le fichier édité par Collabora et le remplace |


Workflow
L’utilisateur téléverse un fichier .docx via l’interface web.

Le fichier est stocké dans le dossier files/.

Lorsqu’un utilisateur clique sur "Ouvrir", il est redirigé vers l’éditeur Collabora avec les bons paramètres WOPISrc et access_token.

Collabora contacte le serveur WOPI pour :

Obtenir les métadonnées (/wopi/files/filename)

Télécharger le fichier (/wopi/files/filename/contents)

Envoyer les changements en POST à /contents


🧰 Technologies utilisées
Flask – Framework Python léger

Docker Compose

Collabora CODE

HTML (template Jinja2 simple)

📎 Exemple de lien WOPI généré


http://localhost:9980/loleaflet/dist/loleaflet.html
    ?WOPISrc=http://localhost:5000/wopi/files/myfile.docx
    &access_token=azerty123


🗑 Gestion des fichiers
Depuis l’interface :

✏️ Renommer un fichier

🗑 Supprimer un fichier

📥 Télécharger un fichier (à ajouter facilement si besoin)


🔐 Sécurité
L’access_token est en dur pour cette démo (azerty123)

Pour une mise en prod :

Générer un token par utilisateur

Stocker en base avec expiration

Authentifier les utilisateurs (Flask-Login)


📌 Notes
Cette implémentation WOPI est minimaliste et suffisante pour le mode "editing".

Pour plus d’options (multi-utilisateur, locking, versioning…), voir la spécification WOPI


🤝 Contributions
Suggestions et améliorations bienvenues !
Tu peux :

Ajouter une API REST

Ajouter le support d’autres formats (.xlsx, .pptx)

Ajouter l’authentification utilisateur

🧪 Testé avec
Docker 24.x

Collabora CODE image officielle

Python 3.10+

Google Chrome / Firefox