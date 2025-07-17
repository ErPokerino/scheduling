# Usa l'immagine ufficiale Python con Streamlit
FROM python:3.11-slim

# Imposta variabili d'ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION=true
ENV ACCESS_CODE=warhammer
ENV GOOGLE_API_KEY=AIzaSyAf2nilTi7NbIYHqX77HgNuMiWaqqzZHFs

# Installa dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crea un utente non-root per sicurezza
RUN useradd --create-home --shell /bin/bash appuser

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di dipendenze
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Crea directory per i dati e cache se non esistono
RUN mkdir -p data && \
    mkdir -p .streamlit && \
    chown -R appuser:appuser /app

# Crea file di configurazione Streamlit per ottimizzare le performance
RUN echo "server.enableCORS = false" > .streamlit/config.toml && \
    echo "server.enableXsrfProtection = false" >> .streamlit/config.toml && \
    echo "server.enableWebsocketCompression = true" >> .streamlit/config.toml && \
    echo "server.enableStaticServing = true" >> .streamlit/config.toml && \
    echo "browser.gatherUsageStats = false" >> .streamlit/config.toml && \
    echo "global.developmentMode = false" >> .streamlit/config.toml && \
    echo "global.showWarningOnDirectExecution = false" >> .streamlit/config.toml && \
    echo "client.caching = true" >> .streamlit/config.toml && \
    echo "client.displayEnabled = true" >> .streamlit/config.toml && \
    echo "runner.magicEnabled = true" >> .streamlit/config.toml && \
    echo "runner.installTracer = false" >> .streamlit/config.toml && \
    echo "runner.fixMatplotlib = true" >> .streamlit/config.toml && \
    echo "theme.base = 'light'" >> .streamlit/config.toml && \
    echo "theme.primaryColor = '#FF6B6B'" >> .streamlit/config.toml && \
    echo "theme.backgroundColor = '#FFFFFF'" >> .streamlit/config.toml && \
    echo "theme.secondaryBackgroundColor = '#F0F2F6'" >> .streamlit/config.toml && \
    echo "theme.textColor = '#262730'" >> .streamlit/config.toml

# Cambia proprietario dei file
RUN chown -R appuser:appuser /app

# Passa all'utente non-root
USER appuser

# Espone la porta di Streamlit
EXPOSE 8501

# Health check migliorato
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando per avviare l'applicazione con ottimizzazioni per la condivisione dati
CMD ["streamlit", "run", "Scheduling.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false", \
     "--server.enableWebsocketCompression=true", \
     "--server.enableStaticServing=true", \
     "--browser.gatherUsageStats=false", \
     "--global.developmentMode=false", \
     "--global.showWarningOnDirectExecution=false", \
     "--client.caching=true", \
     "--runner.magicEnabled=true", \
     "--runner.installTracer=false", \
     "--runner.fixMatplotlib=true"] 