# 🐳 Deployment Docker - Scheduling App

Questa guida ti aiuterà a deployare l'applicazione Scheduling utilizzando Docker.

## 📋 Prerequisiti

- **Docker Desktop** installato e in esecuzione
- **Docker Compose** (incluso in Docker Desktop)
- **Chiave API Google Gemini** (opzionale, per la funzionalità Chat)

## 🚀 Quick Start

### 1. **Configurazione Iniziale**

```bash
# Clona o scarica il repository
cd scheduling

# Copia il template delle variabili d'ambiente
cp env.example .env

# Modifica il file .env con le tue configurazioni
# In particolare, aggiungi la tua GOOGLE_API_KEY
```

### 2. **Build e Avvio (Linux/macOS)**

```bash
# Rendi eseguibile lo script
chmod +x docker-build.sh

# Build dell'immagine
./docker-build.sh build

# Avvio dell'applicazione
./docker-build.sh run
```

### 3. **Build e Avvio (Windows)**

```cmd
# Build dell'immagine
docker-build.bat build

# Avvio dell'applicazione
docker-build.bat run
```

### 4. **Accesso all'Applicazione**

- Apri il browser su: **http://localhost:8501**
- Inserisci il codice di accesso (default: `warhammer`)

## 🔧 Configurazione Dettagliata

### **File .env**

Il file `.env` contiene tutte le variabili d'ambiente necessarie:

```env
# Codice di accesso per l'applicazione
ACCESS_CODE=warhammer

# Chiave API per Google Gemini (necessaria per la Chat)
GOOGLE_API_KEY=your_google_api_key_here

# Chiave API alternativa (fallback)
GEMINI_API_KEY=your_gemini_api_key_here
```

### **Ottenere la Chiave API Google Gemini**

1. Vai su [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Accedi con il tuo account Google
3. Clicca su "Create API Key"
4. Copia la chiave generata
5. Aggiungila al file `.env` come `GOOGLE_API_KEY`

## 📁 Struttura dei File Docker

```
scheduling/
├── Dockerfile                 # Configurazione dell'immagine Docker
├── docker-compose.yml         # Configurazione del deployment
├── docker-compose.override.yml # Configurazioni di sviluppo
├── .dockerignore              # File da escludere dal build
├── env.example                # Template per le variabili d'ambiente
├── docker-build.sh            # Script di build (Linux/macOS)
├── docker-build.bat           # Script di build (Windows)
└── README-Docker.md           # Questa documentazione
```

## 🛠️ Comandi Utili

### **Script di Build (Linux/macOS)**

```bash
./docker-build.sh build      # Build dell'immagine
./docker-build.sh run        # Avvia l'applicazione
./docker-build.sh stop       # Ferma l'applicazione
./docker-build.sh restart    # Riavvia l'applicazione
./docker-build.sh logs       # Mostra i log
./docker-build.sh status     # Stato dei container
./docker-build.sh clean      # Pulizia completa
./docker-build.sh help       # Aiuto
```

### **Script di Build (Windows)**

```cmd
docker-build.bat build       # Build dell'immagine
docker-build.bat run         # Avvia l'applicazione
docker-build.bat stop        # Ferma l'applicazione
docker-build.bat restart     # Riavvia l'applicazione
docker-build.bat logs        # Mostra i log
docker-build.bat status      # Stato dei container
docker-build.bat clean       # Pulizia completa
docker-build.bat help        # Aiuto
```

### **Comandi Docker Compose Diretti**

```bash
# Build
docker-compose build

# Avvio
docker-compose up -d

# Fermata
docker-compose down

# Log
docker-compose logs -f

# Stato
docker-compose ps
```

## 🔒 Sicurezza

### **Gestione delle Chiavi API**

- **NON committare mai** il file `.env` con chiavi reali
- Il file `.env` è già nel `.gitignore`
- Usa variabili d'ambiente in produzione
- Considera l'uso di un secret manager per ambienti di produzione

### **Configurazioni di Sicurezza**

- L'applicazione gira come utente non-root
- Health check automatico
- Restart automatico in caso di crash
- Isolamento di rete

## 📊 Persistenza dei Dati

I dati dell'applicazione sono salvati in:

- **Volume Docker**: `./data` → `/app/data`
- **Configurazione**: `./.streamlit` → `/app/.streamlit`

I dati persistono anche dopo il riavvio del container.

## 🔍 Troubleshooting

### **Problemi Comuni**

#### **1. Porta 8501 già in uso**
```bash
# Cambia la porta nel docker-compose.yml
ports:
  - "8502:8501"  # Usa porta 8502 invece di 8501
```

#### **2. Errore di permessi**
```bash
# Su Linux/macOS, cambia i permessi della directory data
chmod 755 data/
```

#### **3. Chiave API non funzionante**
- Verifica che la chiave API sia corretta nel file `.env`
- Controlla i log: `./docker-build.sh logs`
- Verifica che la chiave abbia i permessi corretti su Google AI Studio

#### **4. Container non si avvia**
```bash
# Controlla i log
./docker-build.sh logs

# Verifica lo stato
./docker-build.sh status

# Riavvia con build pulito
./docker-build.sh clean
./docker-build.sh build
./docker-build.sh run
```

### **Log e Debug**

```bash
# Log in tempo reale
./docker-build.sh logs

# Log specifici del container
docker-compose logs scheduling-app

# Accesso al container per debug
docker-compose exec scheduling-app bash
```

## 🚀 Deployment in Produzione

### **Ambiente di Produzione**

1. **Modifica il codice di accesso**:
   ```env
   ACCESS_CODE=your_secure_access_code
   ```

2. **Configura HTTPS** (raccomandato):
   - Usa un reverse proxy (nginx, traefik)
   - Configura certificati SSL

3. **Monitoraggio**:
   - Abilita i log strutturati
   - Configura alerting
   - Monitora l'uso delle risorse

### **Esempio con Nginx**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📝 Note Aggiuntive

- **Risorse**: L'applicazione richiede circa 512MB di RAM
- **Storage**: I dati sono salvati nel volume `./data`
- **Backup**: Fai backup regolari della directory `./data`
- **Aggiornamenti**: Per aggiornare l'app, esegui `./docker-build.sh clean && ./docker-build.sh build && ./docker-build.sh run`

## 🆘 Supporto

Se incontri problemi:

1. Controlla i log: `./docker-build.sh logs`
2. Verifica la configurazione nel file `.env`
3. Assicurati che Docker sia in esecuzione
4. Controlla che la porta 8501 sia libera

Per ulteriori informazioni, consulta la documentazione principale dell'applicazione. 