================================================================================
                    IPTV STUDIO PRO - SCHEDA INFORMATIVA
================================================================================

COS'È IPTV STUDIO PRO?
--------------------------------------------------------------------------------
IPTV Studio Pro (sviluppato dallo script Python `iptv_checker_2.py`) è un'applicazione
desktop completa basata su interfaccia grafica (Tkinter) progettata per gestire,
verificare, riprodurre, organizzare e registrare flussi IPTV (liste in formato M3U/M3U8)
unitamente alla Guida Elettronica ai Programmi (EPG XMLTV).

Le componenti fondamentali dell'applicazione si dividono in 5 macro-aree:

1. VERIFICA E DIAGNOSTICA DEI FLUSSI (IPTV CHECKER)
--------------------------------------------------------------------------------
- Test Multithread: Controlla la disponibilità in parallelo di centinaia di canali.
- Analisi approfondita tramite FFprobe: Non si limita a verificare l'accessibilità HTTP,
  ma analizza il flusso video reale per determinare:
  * Stato del canale (ONLINE, OFFLINE, PENDING).
  * Risoluzione video (es. 1080p, 720p, 4K, SD).
  * Codifica e frame rate.
  * Latenza / Tempo di risposta della connessione.
- Filtraggio Avanzato: Permette di filtrare i canali per stato (solo online), per Paese,
  per qualità o per selezione dei Preferiti (contrassegnati con ★).

2. GUIDA TV (EPG XMLTV) ED EDITOR ABBINAMENTI
--------------------------------------------------------------------------------
- Supporto XMLTV e archivi compressi (.xml e .xml.gz), caricabili sia da file locale
  che da URL remoti.
- Match Automatico: Associa automaticamente le informazioni EPG ai canali M3U basandosi
  su ID canale, `tvg-id`, `tvg-name` o somiglianza del nome.
- Editor Manuale: Consente di cercare e abbinare manualmente i canali non riconosciuti.
- Palinsesto ed Eventi: Mostra la programmazione attuale (in onda) e i programmi futuri,
  con dettagli quali orari di inizio/fine, descrizioni e categorie.

3. PLAYER MULTIMEDIALE INTEGRATO ED ESTERNO
--------------------------------------------------------------------------------
- Riproduttore Integrato (Embedded): Integra un'anteprima video direttamente all'interno
  della finestra dell'applicazione sfruttando FFplay e l'incorporamento del rendering 
  della finestra su Windows (tramite API Win32 / SetParent).
- Riproduttore Esterno: Possibilità di lanciare ed eseguire i canali con player esterni
  configurabili (come VLC Media Player o FFplay standalone).

4. REGISTRAZIONE VIDEO E SCHEDULAZIONE TIMER
--------------------------------------------------------------------------------
- Registrazione Immediata: Registra il flusso in riproduzione diretta salvandolo su disco
  tramite FFmpeg senza perdita di qualità (pass-through della traccia originale).
- Registrazione da Guida EPG: Consente di cliccare su un evento futuro della Guida TV e
  programmarne la registrazione automatica.
- Gestore dei Timer: Gestisce un elenco di registrazioni programmate salvate in locale
  (`iptv_studio_config.json`), avviando la registrazione all'ora specificata ed
  interrompendola al termine del programma.

5. PRESET RAPIDI ED ESPORTAZIONE LISTE M3U
--------------------------------------------------------------------------------
- Preset Integrati: Include collegamenti rapidi a liste e guide EPG di pubblico dominio
  e trasmissioni legali/free (es. Pluto TV, Rakuten TV, Seca, Vassel81, Tvitava, iptv-org).
- Esportazione M3U Personalizzata: Permette di esportare la lista corrente ordinata e
  filtrata (es. salvando solo i canali funzionanti o quelli marcati come preferiti),
  mantenendo gli attributi EPG (`tvg-id`, `tvg-logo`, `group-title`).

================================================================================
                          REQUISITI TECNICI E DIPENDENZE
================================================================================
- Linguaggio: Python 3 (librerie standard: `tkinter`, `urllib`, `threading`, `json`, `gzip`).
- Strumenti Esterni Richiesti:
  * `ffmpeg.exe`  (per la registrazione dei flussi)
  * `ffprobe.exe` (per l'analisi tecnica di risoluzione e codec)
  * `ffplay.exe`  (per la riproduzione video sia integrata che esterna)

Quando compilato tramite PyInstaller / Inno Setup, l'applicazione integra tutti questi
binari in un unico file eseguibile (`IPTV_Studio_Pro.exe`) o in un installer Windows,
rendendolo completamente autonomo ("portable/standalone").
================================================================================
