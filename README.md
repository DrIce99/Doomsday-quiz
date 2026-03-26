# Doomsday Master
Doomsday Master è un'applicazione desktop avanzata sviluppata in Python e CustomTkinter progettata per allenare il calcolo mentale del calendario utilizzando l'[Algoritmo del Doomsday](https://it.wikipedia.org/wiki/Algoritmo_Doomsday) (ideato da John Conway). L'app trasforma l'apprendimento matematico in un'**esperienza gamificata**, monitorando ogni progresso con statistiche dettagliate e analisi biometrico-ambientali.
<br>
## 🎮 Caratteristiche Principali
### 1. Allenamento Dinamico (Quiz)
**Due Modalità di Gioco**: 

* **Solo Doomsday**: Indovina l'ancora dell'anno richiesto.

* **Giorno Preciso**: Calcola il giorno esatto di una data casuale (es. 14/05/2026).

* **Difficoltà Scalabile**: Da date contemporanee (Facile) a secoli passati o futuri (Difficile).

* **Schermata di Preparazione**: Sistema "Ready" per evitare partenze involontarie del timer.

* **Spiegazioni Interattive**: Dopo ogni risposta, l'app mostra il ragionamento logico passo-passo diviso in "Calcolo Doomsday Anno" e "Calcolo Giorno del Mese".

### 2. Controllo Ibrido (Mouse & Tastiera)

* **Input Manager**: Supporto completo per tastierino numerico e tastiera standard (0-6).

* **Feedback Visivo**: Effetto "Bordo Spesso" sui pulsanti a schermo quando si preme un tasto.

* **Modalità Conferma**: Opzione attivabile per richiedere il tasto INVIO prima di validare la risposta.

* **Workflow Rapido**: Passa alla prossima domanda istantaneamente premendo la Barra Spaziatrice.

### 3. Analytics Avanzate (Sistema a Tab)
L'area statistiche è stata potenziata con un'interfaccia a schede per un'analisi profonda delle performance:

* **📈 Andamento Temporale**: Visualizzazione multi-asse del tempo di risposta (linea blu) e del Winrate cumulativo (linea verde). Include la **Media Mobile (SMA 5)** per identificare i trend di miglioramento reali.

* **🧠 Distanza Mentale**: Grafico che correla la velocità di risposta alla distanza della data dall'ancora del mese, identificando i tuoi "punti ciechi" cognitivi.

* **📅 Performance Doomsday**: Analisi specifica della velocità media per ogni giorno della settimana (Lun-Dom) nella modalità Solo Doomsday.

* **Tooltip Interattivo**: Passa il mouse sui punti per dettagli granulari su ogni singola sessione.


| Andamento Temporale | Distanza Mentale | Performance Giornaliera |
|:---:|:---:|:---:|
| ![Andamento](README%20src/img/andamento.png) | ![Distanza](README%20src/img/doomsday.png) | ![Performance](README%20src/img/mental.png) |

### 4. Diario delle Condizioni & Trend

* **Tag Giornalieri**: Associa condizioni (Malattia, Stanchezza, Focus) ai giorni tramite il `CalendarPicker`.

* **Analisi dell'Impatto**: Il sistema calcola automaticamente quanto una condizione (es. "Poco Sonno") influisce in termini di secondi extra e calo del winrate.

* **Trend Recente**: Confronto immediato tra la media degli ultimi 7 giorni e la performance odierna.

<br>

## 🛠 Architettura Tecnica
Il progetto segue una struttura modulare per facilitare la manutenzione:

* **game.py**: Entry point dell'applicazione e gestore della navigazione.

* **modules/**:
    * `quiz_module.py`: Logica del gioco, gestione timer e calcolo Doomsday.
    * `stats_module.py`: Elaborazione dati JSON e renderizzazione avanzata Matplotlib con sistema Tabview.
    * `settings_module.py`: Configurazione preferenze e stili.
* **utils/**:
    * `keyboard_controller.py`: Gestore eventi tastiera.
    * `calendar_util.py`: Calendario personalizzato per la marcatura delle condizioni giornaliere.
* **data/**:
    * `doomsday_stats_v2.json`: Database locale delle sessioni.
    * `conditions_v2.json`: Registro storico delle condizioni personali.

<br>

## 🎨 Personalizzazione
L'interfaccia è costruita con **Colori Adattivi**: ogni testo, pulsante e grafico si adatta automaticamente al tema Light o Dark, garantendo un'esperienza riposante per la vista durante le sessioni di allenamento prolungate.
<br>
## 🚀 Installazione
1. Clona la repository.
2. Installa le dipendenze:
   ```bash
   pip install customtkinter matplotlib
   ```
   
3. Avvia l'applicazione:
   ```
   python game.py
   ```

Sviluppato per chi vuole padroneggiare il tempo, un calcolo alla volta.


---