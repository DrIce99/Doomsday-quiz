
# Doomsday Master

Doomsday Master è un'applicazione desktop avanzata sviluppata in Python e CustomTkinter progettata per allenare il calcolo mentale del calendario utilizzando l'[Algoritmo del Doomsday](https://it.wikipedia.org/wiki/Algoritmo_Doomsday) (ideato da John Conway). L'app trasforma l'apprendimento matematico in un'**esperienza gamificata**, monitorando ogni progresso con statistiche dettagliate e analisi biometrico-ambientali.

<br>

## Caratteristiche Principali
1. Allenamento Dinamico (Quiz)

    * Due Modalità di Gioco:
    * Solo Doomsday: Indovina l'ancora dell'anno richiesto.
    * Giorno Preciso: Calcola il giorno esatto di una data casuale (es. 14/05/2026).
    * Difficoltà Scalabile: Da date contemporanee (Facile) a secoli passati o futuri (Difficile).
    * Schermata di Preparazione: Sistema "Ready" per evitare partenze involontarie del timer.
    * Spiegazioni Interattive: Dopo ogni risposta, l'app mostra il ragionamento logico passo-passo diviso in "Calcolo Doomsday Anno" e "Calcolo Giorno del Mese".

2. Controllo Ibrido (Mouse & Tastiera)

    * Input Manager: Supporto completo per tastierino numerico e tastiera standard (0-6).
    * Feedback Visivo: Effetto "Bordo Spesso" sui pulsanti a schermo quando si preme un tasto.
    * Modalità Conferma: Opzione attivabile per richiedere il tasto INVIO prima di validare la risposta.
    * Workflow Rapido: Passa alla prossima domanda istantaneamente premendo la Barra Spaziatrice.

3. Analytics Avanzate & Grafici

    * Grafici Multi-Asse: Visualizzazione contemporanea di Tempo Medio (linea gialla) e Winrate Cumulativo (linea verde tratteggiata).
    * Trend & SMA: Calcolo della media mobile (SMA 5) per visualizzare il miglioramento reale oltre la media globale.
    * Analisi dell'Impatto: Sistema unico per monitorare come le condizioni personali (Malattia, Stanchezza, Focus) influenzano la velocità e la precisione.
    * Tooltip Interattivo: Passa il mouse sui punti del grafico per vedere i dettagli esatti di ogni sessione.

4. Diario delle Condizioni

    * Tag Giornalieri: Associa condizioni specifiche ai giorni (es. Malattia = Rosso, Focus Alto = Verde).
    * Integrazione Calendario: Il CalendarPicker integrato mostra i bordi colorati in base alle condizioni salvate, permettendo di analizzare i cali di performance dovuti a fattori esterni.

<br>

## Architettura Tecnica
Il progetto segue una struttura modulare per facilitare la manutenzione e la scalabilità:

* game.py: Entry point dell'applicazione e gestore della navigazione tra i frame.
* modules/:
* quiz_module.py: Gestisce la logica del gioco e il timer di precisione.
   * stats_module.py: Elabora i dati JSON e renderizza i grafici Matplotlib.
   * settings_module.py: Interfaccia sidebar per la configurazione dell'app.
* utils/:
* keyboard_controller.py: Gestore degli eventi della tastiera e degli effetti hover.
   * calendar_util.py: Calendario personalizzato per la selezione delle date storiche.
* data/:
* doomsday_stats_v2.json: Database locale delle sessioni di gioco.
   * conditions_v2.json: Registro delle condizioni giornaliere.
   * config.json: Preferenze dell'utente (Tema, Conferma Invio, ecc.).

<br>

## Personalizzazione

L'interfaccia è costruita con Colori Adattivi: ogni testo, pulsante e grafico si adatta automaticamente al tema Light o Dark scelto nelle impostazioni, garantendo leggibilità e contrasto elevato in ogni condizione di luce.

<br>

## Installazione

   1. Clona la repository.
   2. Installa le dipendenze:
   
        pip install customtkinter matplotlib
   
   3. Avvia l'applicazione:
   
        python game.py
   
   
<br>

Sviluppato per chi vuole padroneggiare il tempo, un calcolo alla volta.
------------------------------