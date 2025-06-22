# Scheduling App – To-Do

## Priorità 1 – Chatbot LLM
- [ ] Scegliere il modello LLM (OpenAI GPT-4o, Azure OpenAI, Mistral 7B ecc.).
- [ ] Definire prompt di sistema e istruzioni per interagire con:
  - Aggiunta progetto (campi richiesti + allocazioni FTE).
  - Modifica / cancellazione progetto.
  - Query analitiche su FTE (per utente, area, progetto, mese…).
- [ ] Creare layer di **function calling** o **tools** per esporre le funzioni Python del backend al chatbot.
- [ ] Gestire autenticazione/ruoli (chi può fare cosa tramite chat).
- [ ] UI: area chat dedicata con risposta streaming e azioni confermate.
- [ ] Logging delle conversazioni per audit.

## Priorità 2 – Data & Funzioni
- [ ] Gestire calcolo campi derivati (colonne mese1) lato backend.
- [ ] Validazioni avanzate input (date coerenti, FTE > 1, ecc.).
- [ ] Gestione bulk upload di schedulazioni via file.

## Priorità 3 – UX miglioramenti
- [ ] Ordinamento e ricerca avanzata nelle tabelle Schedule.
- [ ] KPI dashboard riassuntiva in homepage.
- [ ] Tema grafico personalizzato (config.toml).

## Priorità 4 – Deploy & DevOps
- [ ] Script di build e deploy (Docker / Streamlit Community Cloud / Azure). 
- [ ] Test automatici su funzioni critiche (pytest). 