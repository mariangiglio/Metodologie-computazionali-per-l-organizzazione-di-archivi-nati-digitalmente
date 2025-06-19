# README

**Scaricare il programma** 
Questo programma è scritto interamente in Python. Per il suo corretto funzionamento è dunque necessario avere scaricato e installato [Python](https://www.python.org/downloads/)

Per installare il programma è necessario scaricare i materiali da questo repository. Potete farlo andando su: 
1. Code (in alto a destra)
2. Download Zip.
![image](https://github.com/user-attachments/assets/53725a24-3916-4c0b-a7fa-0e8cc6b84159)

Estraete normalmente il contenuto dello zip. 

**Prerequisiti**
Per creare un ambiente Python che supporti l'esecuzione di questo script è inoltre necessario avere delle specifiche librerie installate. Per farlo sarà sufficiente entrare nella cartella in cui sono stati scaricati i requirements, da lì aprire il terminale (tasto destro del mouse ⮕ apri nel terminale) e digitare:

						pip install -r requirements.txt
      
**Per lanciare il programma:**

 1. Assicurarsi di avere installato e configurato correttamente Python
 2.  Assicurarsi di avere tutte le librerie richieste  
 3. Portarsi nel terminale dalla cartella in cui è stato scaricato il programma e lanciare il seguente comando

						python catalogatore.py

L'avvio da terminale permette di controllare i dettagli dell'attività in corso.


**ATTENZIONE:**
Le prime fasi dello script (soprattutto la fase di estrazione dei materiali testuali) possono richiedere molto tempo. Non chiudere il programma mentre è in esecuzione. 


**Dettagli sulle librerie necessarie:**

 - **shutil:** Offre funzioni di alto livello per operare con file e collezioni di file. Include funzioni per copiare e spostare file, eliminazione di directory e file, e altre operazioni di gestione dei file.
 - **subprocess:** Utilizzata per eseguire nuovi processi, connettersi ai loro input/output/error pipes, e ottenere i loro codici di ritorno. È utile per lanciare comandi shell o altri programmi direttamente da Python.
 - **hashlib:** Fornisce un insieme di algoritmi di hashing per la crittografia di dati, come SHA1, SHA224, SHA256, SHA384, e SHA512, oltre a supportare l'algoritmo MD5.
 - **tempfile:** Usata per creare file e directory temporanee. Molto utile quando si ha bisogno di un file o una directory temporanea nel programma e si vuole che sia cancellato automaticamente quando il programma termina.
 - **pandas:** Una delle più popolari librerie di Python per la manipolazione e l'analisi di dati. Offre strutture di dati potenti e flessibili che rendono facile manipolare dati strutturati.
 - **numpy:** Libreria centrale per il calcolo scientifico in Python.Fornisce un oggetto array multidimensionale e una collezione di routine per operazioni rapide su array.
 - **tkinter** (e i relativi moduli filedialog, messagebox, ttk): È una libreria standard di Python per la creazione di interfacce grafiche. È utile per costruire applicazioni che necessitano di un'interfaccia grafica semplice ed efficace.
 - **ttkthemes**: Libreria che offre temi per l'interfaccia Tkinter
 - **matplotlib.pyplot:** Una libreria di visualizzazione molto usata in Python, utilizzata per creare figure e grafici in vari formati e ambienti interattivi come Jupyter notebooks.
 - **seaborn:** Basata su matplotlib, questa libreria fornisce una interfaccia di alto livello per la creazione di grafici statistici.
 - **scipy.cluster.hierarchy (specificamente le funzioni linkage, dendrogram):** Queste funzioni sono usate per eseguire clustering gerarchico. linkage è usata per definire la metrica di distanza usata per il clustering, mentre dendrogram è utilizzata per visualizzare il risultato come un diagramma ad albero.
 - **sklearn.decomposition.PCA:** Dal modulo sklearn, PCA (Principal Component Analysis) è usata per ridurre la dimensionalità dei dati mentre si preserva la maggior parte della varianza. È utile per l'analisi esplorativa e per pre-elaborare i dati prima dell'applicazione di altri algoritmi di machine learning.
 - **sklearn.manifold.MDS:** (Multidimensional Scaling) Un'altra tecnica di riduzione della dimensionalità che cerca di mantenere le distanze tra i punti in uno spazio di dimensionalità inferiore.
 - **sklearn.cluster.KMeans:** Un popolare algoritmo di clustering che partiziona i dati in K cluster distinti basandosi sulla minimizzazione della somma dei quadrati delle distanze tra ogni puntoe il centroide del cluster più vicino.
