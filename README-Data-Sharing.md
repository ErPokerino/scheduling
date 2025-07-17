# Condivisione Dati tra Sezioni

## Panoramica

Questa funzionalità permette di condividere automaticamente i dati caricati manualmente nella sezione **Scheduling** con tutte le altre sezioni dell'applicazione (Analytics, Chat, Projects).

## Come Funziona

### 1. Caricamento Manuale di File
Quando carichi un file Excel o CSV nella sezione **Scheduling**:
- I dati vengono salvati nel file Excel locale
- I dati vengono automaticamente condivisi nel session state dell'applicazione
- Tutte le altre sezioni possono accedere immediatamente ai nuovi dati

### 2. Aggiornamento Automatico
- **Analytics**: I report e i grafici si aggiornano automaticamente con i nuovi dati
- **Chat**: Il chatbot può rispondere a domande sui nuovi dati caricati
- **Projects**: La gestione dei progetti include i nuovi dati

### 3. Notifiche
Ogni sezione mostra un banner informativo che indica quando i dati sono stati aggiornati:
```
📊 Dati aggiornati: 15/12/2024 14:30:25
```

## Modalità di Import

### Sostituisci Tutti i Dati
- Cancella tutti i dati esistenti
- Utilizza solo i nuovi dati caricati
- Ideale per aggiornamenti completi del dataset

### Aggiungi ai Dati Esistenti
- Mantiene i dati esistenti
- Aggiunge i nuovi dati in coda
- Ideale per integrazioni incrementali

## Gestione del Cache

Il sistema gestisce automaticamente:
- **Invalidazione del cache**: Forza il ricaricamento dei dati nelle altre sezioni
- **Session state**: Mantiene i dati in memoria per accesso rapido
- **Fallback**: Se i dati condivisi non sono disponibili, carica dal file Excel

## Struttura Tecnica

### File Principali
- `Scheduling.py`: Gestione del caricamento e condivisione dati
- `src/data_access.py`: Funzioni di caricamento con supporto dati condivisi
- `src/utils.py`: Funzioni di utilità per la gestione dati condivisi

### Funzioni Chiave
- `update_shared_data()`: Aggiorna i dati nel session state
- `load_shared_scheduling_data()`: Carica dati dal session state
- `show_data_update_info()`: Mostra notifiche di aggiornamento

## Vantaggi

1. **Accesso Immediato**: I dati sono disponibili in tutte le sezioni senza ricaricamento
2. **Consistenza**: Tutte le sezioni utilizzano gli stessi dati aggiornati
3. **Performance**: Riduce i tempi di caricamento grazie al caching
4. **User Experience**: Notifiche chiare sullo stato dei dati

## Note Importanti

- I dati condivisi persistono solo durante la sessione corrente
- Al riavvio dell'applicazione, i dati vengono caricati dal file Excel
- Il sistema mantiene sempre una copia di backup nel file Excel locale
- Le modifiche effettuate in altre sezioni (es. Projects) aggiornano automaticamente i dati condivisi

## Troubleshooting

### Dati Non Aggiornati
1. Verifica che il file sia stato caricato correttamente
2. Controlla i messaggi di successo nella sezione Scheduling
3. Ricarica la pagina se necessario

### Errori di Caricamento
1. Verifica il formato del file (Excel .xlsx o CSV)
2. Controlla che le colonne corrispondano alla struttura attesa
3. Verifica che il file non sia corrotto

### Cache Non Aggiornato
1. Il sistema dovrebbe aggiornare automaticamente il cache
2. In caso di problemi, ricarica manualmente la pagina
3. Verifica che non ci siano errori nella console del browser 