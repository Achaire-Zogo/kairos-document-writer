FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système pour python-magic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer le répertoire pour les fichiers
RUN mkdir -p files

EXPOSE 5000

CMD ["python", "app.py"]
