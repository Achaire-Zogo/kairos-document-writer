const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const upload = multer({ dest: 'uploads/' });

// Servir l'interface HTML
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Upload de fichier
app.post('/upload', upload.single('file'), (req, res) => {
    const filePath = path.join(__dirname, 'uploads', req.file.originalname);
    fs.renameSync(req.file.path, filePath);
    res.json({ url: `http://localhost:9980/loleaflet/dist/loleaflet.html?file_path=${filePath}` });
});

// Servir les fichiers uploadés
app.use('/uploads', express.static('uploads'));

app.listen(3000, () => console.log('Server running on port 3000'));