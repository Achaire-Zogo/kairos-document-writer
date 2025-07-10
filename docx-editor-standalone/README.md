# 📝 Éditeur DOCX Standalone

Un éditeur de documents DOCX moderne et fonctionnel utilisant CKEditor 5.

## 🚀 Fonctionnalités

### ✨ **Édition avancée**
- **CKEditor 5** avec barre d'outils complète
- Support des titres, formatage, couleurs, tableaux
- Interface moderne et intuitive
- Raccourcis clavier (Ctrl+S, Ctrl+O)

### 📁 **Gestion DOCX**
- **Import DOCX** : Chargement et conversion automatique
- **Export DOCX** : Sauvegarde au format Word natif
- **Fallback HTML** : Si DOCX indisponible
- **Drag & Drop** : Interface intuitive

### 🎨 **Interface moderne**
- Design avec dégradés colorés
- Messages de statut en temps réel
- Indicateur de chargement
- Informations sur les fichiers

## 🛠️ Technologies utilisées

- **CKEditor 5** : Éditeur de texte riche
- **Mammoth.js** : Conversion DOCX vers HTML
- **docx.js** : Création de fichiers DOCX
- **FileSaver.js** : Téléchargement de fichiers

## 📋 Utilisation

1. **Ouvrir** : Double-cliquez sur `index.html`
2. **Charger** : Cliquez "Charger DOCX" ou utilisez Ctrl+O
3. **Éditer** : Utilisez la barre d'outils CKEditor
4. **Sauvegarder** : Cliquez "Sauvegarder DOCX" ou utilisez Ctrl+S

## 🔧 Fonctionnement

### Import DOCX
```javascript
// Utilise Mammoth.js pour convertir DOCX en HTML
mammoth.convertToHtml({arrayBuffer: arrayBuffer})
    .then(result => editor.setData(result.value))
```

### Export DOCX
```javascript
// Utilise docx.js pour créer un fichier DOCX natif
const doc = new docx.Document({...});
docx.Packer.toBlob(doc).then(blob => saveAs(blob, filename));
```

## 🌐 Serveur local (optionnel)

Pour éviter les restrictions CORS :

```bash
# Python
python3 -m http.server 8000

# Node.js
npx http-server

# Puis ouvrir : http://localhost:8000
```

## ✅ Avantages

- **Autonome** : Fonctionne sans serveur
- **Moderne** : Interface utilisateur attrayante
- **Robuste** : Gestion d'erreurs et fallbacks
- **Rapide** : Chargement et traitement optimisés
- **Compatible** : Fonctionne sur tous navigateurs modernes

## 🐛 Dépannage

### Problèmes courants

1. **Fichier ne se charge pas**
   - Vérifiez que c'est un fichier .docx valide
   - Consultez la console (F12) pour les erreurs

2. **Export DOCX ne fonctionne pas**
   - L'éditeur utilise automatiquement le fallback HTML
   - Vérifiez les logs dans la console

3. **Interface ne s'affiche pas**
   - Vérifiez votre connexion internet (CDN requis)
   - Ouvrez la console pour voir les erreurs de chargement

## 📞 Support

Consultez les logs de la console (F12) pour diagnostiquer les problèmes.
L'éditeur affiche des messages de statut détaillés pour guider l'utilisateur.
