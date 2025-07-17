#!/bin/bash

# Script per build e deployment dell'app Scheduling con Docker
# Uso: ./docker-build.sh [build|run|stop|clean|logs|export|import]

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni di utilità
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Controlla se Docker è installato
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker non è installato. Installa Docker prima di continuare."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose non è installato. Installa Docker Compose prima di continuare."
        exit 1
    fi
}

# Controlla se il file .env esiste
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning "File .env non trovato. Creo un template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_info "File .env creato da env.example"
            print_warning "Modifica il file .env con le tue configurazioni prima di continuare!"
            exit 1
        else
            print_error "File env.example non trovato. Crea manualmente il file .env"
            exit 1
        fi
    fi
}

# Build dell'immagine
build_image() {
    print_info "Building Docker image con nuove funzionalità di condivisione dati..."
    docker-compose build --no-cache
    print_success "Build completato con funzionalità di condivisione dati!"
}

# Avvia l'applicazione
run_app() {
    print_info "Avvio dell'applicazione con condivisione dati..."
    docker-compose up -d
    print_success "Applicazione avviata con condivisione dati!"
    print_info "Accesso disponibile su: http://localhost:8501"
    print_info "Nuove funzionalità: Condivisione automatica dati tra sezioni"
    print_info "Per vedere i log: ./docker-build.sh logs"
}

# Ferma l'applicazione
stop_app() {
    print_info "Fermando l'applicazione..."
    docker-compose down
    print_success "Applicazione fermata!"
}

# Mostra i log
show_logs() {
    print_info "Mostrando i log..."
    docker-compose logs -f
}

# Pulisce tutto
clean_all() {
    print_warning "Pulizia completa - questo rimuoverà tutti i container e le immagini!"
    read -p "Sei sicuro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Rimozione container e immagini..."
        docker-compose down --rmi all --volumes --remove-orphans
        print_success "Pulizia completata!"
    else
        print_info "Pulizia annullata."
    fi
}

# Controlla lo stato
check_status() {
    print_info "Stato dei container:"
    docker-compose ps
}

# Export dell'immagine
export_image() {
    print_info "Export dell'immagine Docker..."
    timestamp=$(date +"%Y%m%d_%H%M%S")
    filename="scheduling-app-v2.0_${timestamp}.tar"
    print_info "Creazione file: $filename"
    docker save scheduling-scheduling-app:latest -o "$filename"
    print_success "Immagine esportata in: $filename"
    print_info "Per importare: docker load -i $filename"
}

# Import dell'immagine
import_image() {
    if [ -z "$2" ]; then
        print_error "Specifica il file da importare: $0 import filename.tar"
        exit 1
    fi
    print_info "Import dell'immagine Docker da: $2"
    docker load -i "$2"
    print_success "Immagine importata!"
    print_info "Per avviare: $0 run"
}

# Menu principale
case "${1:-help}" in
    "build")
        check_docker
        build_image
        ;;
    "run")
        check_docker
        check_env_file
        run_app
        ;;
    "stop")
        check_docker
        stop_app
        ;;
    "restart")
        check_docker
        stop_app
        sleep 2
        run_app
        ;;
    "logs")
        check_docker
        show_logs
        ;;
    "clean")
        check_docker
        clean_all
        ;;
    "status")
        check_docker
        check_status
        ;;
    "export")
        check_docker
        export_image
        ;;
    "import")
        check_docker
        import_image "$@"
        ;;
    "help"|*)
        echo "Script per build e deployment dell'app Scheduling con Docker"
        echo "Versione 2.0 - Con funzionalità di condivisione dati"
        echo ""
        echo "Uso: $0 [comando]"
        echo ""
        echo "Comandi disponibili:"
        echo "  build    - Build dell'immagine Docker con nuove funzionalità"
        echo "  run      - Avvia l'applicazione con condivisione dati"
        echo "  stop     - Ferma l'applicazione"
        echo "  restart  - Riavvia l'applicazione"
        echo "  logs     - Mostra i log"
        echo "  clean    - Pulisce tutto (container, immagini, volumi)"
        echo "  status   - Mostra lo stato dei container"
        echo "  export   - Esporta l'immagine Docker in file .tar"
        echo "  import   - Importa l'immagine Docker da file .tar"
        echo "  help     - Mostra questo aiuto"
        echo ""
        echo "Nuove funzionalità v2.0:"
        echo "  - Condivisione automatica dati tra sezioni"
        echo "  - Notifiche di aggiornamento dati"
        echo "  - Cache intelligente per performance ottimali"
        echo "  - Configurazioni Streamlit ottimizzate"
        echo ""
        echo "Esempi:"
        echo "  $0 build && $0 run    # Build e avvio"
        echo "  $0 export             # Esporta immagine"
        echo "  $0 import app.tar     # Importa immagine"
        echo "  $0 logs               # Visualizza log"
        echo "  $0 stop               # Ferma l'app"
        ;;
esac 