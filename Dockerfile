# Usa l'immagine ufficiale Python con Streamlit
FROM python:3.11-slim

# Imposta variabili d'ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
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

# Crea directory per i dati se non esiste
RUN mkdir -p data && \
    chown -R appuser:appuser /app

# Cambia proprietario dei file
RUN chown -R appuser:appuser /app

# Passa all'utente non-root
USER appuser

# Espone la porta di Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando per avviare l'applicazione
CMD ["streamlit", "run", "Scheduling.py", "--server.port=8501", "--server.address=0.0.0.0"] 