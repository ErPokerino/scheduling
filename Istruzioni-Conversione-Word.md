# ISTRUZIONI PER CONVERSIONE IN WORD

## Metodo 1: Pandoc (Raccomandato)

### Prerequisiti
1. Installare Pandoc: https://pandoc.org/installing.html
2. Installare Microsoft Word o LibreOffice Writer

### Conversione
```bash
# Conversione base
pandoc "Documentazione-Funzionale-Scheduling-App.md" -o "Documentazione-Funzionale-Scheduling-App.docx"

# Conversione con template personalizzato
pandoc "Documentazione-Funzionale-Scheduling-App.md" \
  --reference-doc=template.docx \
  -o "Documentazione-Funzionale-Scheduling-App.docx"

# Conversione con stili personalizzati
pandoc "Documentazione-Funzionale-Scheduling-App.md" \
  --from markdown \
  --to docx \
  --output "Documentazione-Funzionale-Scheduling-App.docx" \
  --toc \
  --number-sections
```

## Metodo 2: Online Converters

### Opzioni Online
1. **Pandoc Try**: https://pandoc.org/try/
2. **Markdown to Word**: https://word.aippt.com/
3. **CloudConvert**: https://cloudconvert.com/md-to-docx

### Passi
1. Aprire il file `Documentazione-Funzionale-Scheduling-App.md`
2. Copiare tutto il contenuto
3. Incollare nel convertitore online
4. Scaricare il file .docx generato

## Metodo 3: Editor con Supporto Markdown

### Visual Studio Code
1. Installare l'estensione "Markdown All in One"
2. Aprire il file .md
3. Usare `Ctrl+Shift+P` → "Markdown All in One: Print current document to HTML"
4. Copiare l'HTML e incollare in Word

### Typora
1. Aprire il file .md in Typora
2. File → Export → Word (.docx)

## Metodo 4: Copia e Incolla Diretta

### Passi
1. Aprire il file `Documentazione-Funzionale-Scheduling-App.md` in un editor di testo
2. Selezionare tutto il contenuto (`Ctrl+A`)
3. Copiare (`Ctrl+C`)
4. Aprire Microsoft Word
5. Incollare (`Ctrl+V`)
6. Word riconoscerà automaticamente la formattazione Markdown

## Personalizzazione Word

### Stili Consigliati
- **Titolo 1**: Per i titoli principali (INTRODUZIONE, PANORAMICA DEL SISTEMA, ecc.)
- **Titolo 2**: Per i sottotitoli (1.1, 1.2, ecc.)
- **Titolo 3**: Per i paragrafi (1.1.1, 1.1.2, ecc.)
- **Normale**: Per il testo del corpo
- **Codice**: Per i blocchi di codice

### Formattazione Aggiuntiva
1. **Indice**: Inserire un indice automatico
2. **Numerazione pagine**: Aggiungere numerazione
3. **Intestazioni/Piè di pagina**: Aggiungere informazioni aziendali
4. **Colori**: Personalizzare i colori per i titoli
5. **Font**: Utilizzare font aziendali

### Template Word
Creare un template Word con:
- Stili predefiniti
- Intestazioni e piè di pagina
- Colori aziendali
- Font personalizzati
- Margini e spaziatura

## Struttura Finale Consigliata

### Pagina di Copertina
- Logo aziendale
- Titolo documento
- Versione
- Data
- Autore

### Indice
- Indice automatico generato da Word
- Numerazione pagine

### Contenuto
- Documentazione convertita
- Stili applicati
- Formattazione corretta

### Appendici
- Screenshot applicazione
- Diagrammi tecnici
- Esempi di utilizzo

## Controllo Qualità

### Verifiche Post-Conversione
1. **Formattazione**: Controllare che tutti i titoli siano formattati correttamente
2. **Indice**: Verificare che l'indice sia aggiornato
3. **Immagini**: Controllare che eventuali immagini siano visualizzate
4. **Codice**: Verificare che i blocchi di codice siano formattati
5. **Link**: Controllare che i link interni funzionino

### Ottimizzazioni
1. **Compressione**: Ridurre dimensioni file se necessario
2. **Compatibilità**: Salvare in formato .docx compatibile
3. **Protezione**: Aggiungere protezione se necessario
4. **Firma digitale**: Aggiungere firma se richiesto

## Note Importanti

### Limitazioni
- Alcuni elementi Markdown potrebbero non essere convertiti perfettamente
- I link interni potrebbero richiedere aggiornamento manuale
- Le tabelle potrebbero necessitare di riallineamento

### Raccomandazioni
- Utilizzare Pandoc per la migliore conversione
- Rivedere sempre il documento dopo la conversione
- Mantenere una copia del file Markdown originale
- Testare la conversione su un campione prima del documento completo

## Comandi Utili Pandoc

```bash
# Creare un template di riferimento
pandoc --print-default-data-file reference.docx > template.docx

# Conversione con metadati
pandoc "Documentazione-Funzionale-Scheduling-App.md" \
  --metadata title="Documentazione Funzionale Scheduling App" \
  --metadata author="AI Assistant" \
  --metadata date="$(date +%Y-%m-%d)" \
  -o "Documentazione-Funzionale-Scheduling-App.docx"

# Conversione con CSS personalizzato (per HTML intermedio)
pandoc "Documentazione-Funzionale-Scheduling-App.md" \
  --css=style.css \
  -o "Documentazione-Funzionale-Scheduling-App.html"
```

## Supporto

Per problemi di conversione:
1. Verificare la versione di Pandoc
2. Controllare la sintassi Markdown
3. Utilizzare un editor Markdown per validazione
4. Consultare la documentazione Pandoc 