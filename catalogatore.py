import os
import shutil
import subprocess
import hashlib
import tempfile
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
from collections import defaultdict

# ================================
# Funzioni principali
# ================================

# Fase 0: Pre-lavorazione
def prepare_working_directory(source_dir, working_dir, target_subdir="0-corpus"):
    """
    Crea un ambiente protetto con una struttura organizzata.

    :param source_dir: Directory sorgente da cui copiare i file.
    :param working_dir: Directory di lavoro dove creare l'ambiente protetto.
    :param target_subdir: Nome della sottodirectory target dove salvare i file (default: "0-corpus").
    """
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"La directory sorgente '{source_dir}' non esiste.")

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    target_dir = os.path.join(working_dir, target_subdir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    try:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                target_subfolder = os.path.join(target_dir, relative_path)
                os.makedirs(target_subfolder, exist_ok=True)
                target_file = os.path.join(target_subfolder, file)
                shutil.copy2(source_file, target_file)
    except Exception as e:
        print(f"Errore durante la preparazione della working directory: {e}")
        raise

    # Messaggio per Tkinter o CLI
    try:
        messagebox.showinfo("Fase 0", f"Working Directory creata in: {working_dir}.\n"
                                      f"Copiati i file originali nella cartella {target_subdir}.")
    except Exception:
        print(f"Working Directory creata in: {working_dir}. Copiati i file originali nella cartella {target_subdir}.")

# ================================
# Fase 1: Estrazione dei file di testo
# ================================

def extract_text_and_recreate_structure(source_dir, output_dir, LIBREOFFICE_PATH=None):
    """
    Utilizza LibreOffice per convertire i file in formato ODT mantenendo la struttura della directory.

    :param source_dir: Directory sorgente con i file da convertire.
    :param output_dir: Directory di destinazione per i file convertiti.
    :param LIBREOFFICE_PATH: Percorso personalizzato dell'eseguibile di LibreOffice (opzionale).
    """
    # Imposta il percorso predefinito di LibreOffice se non specificato
    if LIBREOFFICE_PATH is None:
        LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

    # Verifica che il percorso sia valido; se non lo è, richiedi all'utente di selezionarlo
    while not os.path.exists(LIBREOFFICE_PATH):
        messagebox.showwarning(
            "Attenzione",
            "Non è stato trovato LibreOffice nel percorso predefinito o fornito.\n"
            "Se LibreOffice è installato, seleziona il percorso eseguibile.\n"
            "Se non è installato, scaricalo e installalo prima di procedere."
        )
        LIBREOFFICE_PATH = filedialog.askopenfilename(
            title="Seleziona il percorso di LibreOffice",
            filetypes=[("Eseguibili", "*.exe"), ("Tutti i file", "*.*")]
        )
        # Se l'utente non seleziona un file valido, interrompi il processo
        if not LIBREOFFICE_PATH:
            messagebox.showerror("Errore", "Operazione annullata: percorso di LibreOffice non selezionato.")
            return

    # Crea la directory di output se non esiste
    os.makedirs(output_dir, exist_ok=True)

    # Directory temporanea per i file convertiti
    temp_dir = os.path.join(tempfile.gettempdir(), "temp_text")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        for root, dirs, files in os.walk(source_dir):
            # Escludi le directory specificate
            dirs[:] = [d for d in dirs if not should_exclude(d, is_folder=True)]

            # Crea la struttura della directory di destinazione
            relative_path = os.path.relpath(root, source_dir)
            target_dir = os.path.join(output_dir, relative_path)
            os.makedirs(target_dir, exist_ok=True)

            for file in files:
                if should_exclude(file):
                    print(f"File escluso: {file} (criterio: esclusione predefinita)")
                    continue

                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, os.path.splitext(file)[0] + ".odt")

                if os.path.exists(target_file):
                    print(f"File già convertito: {target_file}. Salto.")
                    continue

                try:
                    print(f"Elaborazione del file: {source_file}")

                    # Conversione del file in formato ODT con LibreOffice
                    subprocess.run(
                        [LIBREOFFICE_PATH, "--headless", "--convert-to", "odt", source_file, "--outdir", temp_dir],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    # Copia il file convertito nella destinazione finale
                    temp_output_file = os.path.join(temp_dir, os.path.splitext(file)[0] + ".odt")
                    if os.path.exists(temp_output_file):
                        shutil.move(temp_output_file, target_file)
                        print(f"File convertito e salvato in: {target_file}")
                    else:
                        print(f"Errore nella conversione del file: {source_file}")

                except subprocess.CalledProcessError as e:
                    print(f"Errore durante la conversione di {source_file}: {e}")
                except Exception as e:
                    print(f"Errore durante l'elaborazione del file {source_file}: {e}")

    finally:
        # Rimuove i file temporanei
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("Processo completato.")

    # Notifica all'utente che il processo è completato
    messagebox.showinfo("Fase 1", f"I file sono stati elaborati e salvati in: {output_dir}")


# ================================
# Funzione per escludere file o directory
# ================================


EXCLUDED_NAMES = [
    "[unallocated space]", "fat1", "fat2", "vbr", "resource.frk", "desktop", "desktop printersdb",
    "finder.dat", "openfolderlist", "deletelog", "desktop db", "desktop df", ".ds_store",
    "desktopprinters db", "openfolderlistdf", "indexervolumeguid", "extents", "catalog", "backup mdb",
    "allocation", "mdb", "system volume information"
]

EXCLUDED_FOLDERS = [
    "System Volume Information",
    "__MACOSX",
    "[unallocated space]",
    "TheVolumeSettingsFolder",
    "RESOURCE.FRK",
    "Trash"
]

def should_exclude(name, is_folder=False):
    """Verifica se un file o una cartella deve essere escluso."""
    name_lower = name.lower()
    if is_folder:
        # Controlla se la cartella deve essere esclusa
        if any(pattern in name_lower for pattern in EXCLUDED_FOLDERS):
            return True
    else:
        # Controlla se il file deve essere escluso
        exclude_patterns = ["delete-log", "desktopprinters db", "openfolderlistdf"]
        if any(pattern in name_lower for pattern in exclude_patterns):
            return True
        if name_lower in EXCLUDED_NAMES or name_lower.startswith('.') or name_lower.endswith('.tmp') \
                or name_lower == "desktop.ini" or name_lower.endswith('~') or name_lower.endswith('.copy0'):
            return True
    return False


# ================================
# Fase 2: Hashing
# ================================

def calculate_hashes(base_dir):
    """
    Scorre ricorsivamente la directory fornita e calcola gli hash dei file in base al contenuto testuale,
    oppure – se non leggibile – chiede all'utente se procedere con hash binario.
    """
    from collections import defaultdict
    hash_dict = defaultdict(set)

    for root, _, files in os.walk(base_dir):
        relative_path = os.path.relpath(root, base_dir)
        root_folder = relative_path.split(os.sep)[0]

        for file in files:
            file_path = os.path.join(root, file)

            # Prova con lettura testuale
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                file_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
                hash_dict[root_folder].add(file_hash)
                print(f"[TESTO] Hash calcolato per: {file_path}")

            except UnicodeDecodeError:
                # Fallita lettura testuale → popup all'utente
                risposta = messagebox.askyesno(
                    "Contenuto non testuale",
                    f"Impossibile leggere come testo il file:\n{file}\n\nProseguire con hashing su contenuto binario?"
                )
                if risposta:
                    try:
                        with open(file_path, "rb") as f:
                            content = f.read()
                        file_hash = hashlib.sha256(content).hexdigest()
                        hash_dict[root_folder].add(file_hash)
                        print(f"[BINARIO] Hash calcolato per: {file_path}")
                    except Exception as e:
                        print(f"Errore durante l'hash binario per {file_path}: {e}")
                else:
                    print(f"File ignorato (utente ha rifiutato hashing binario): {file_path}")

            except Exception as e:
                print(f"Errore durante il calcolo dell'hash per {file_path}: {e}")

    return {folder: list(hashes) for folder, hashes in hash_dict.items()}


# ================================
# Fase 3: Creazione matrice Binaria
# ================================
def create_binary_matrix(hash_csv_path):
    """Crea una matrice binaria basata sugli hash a partire da un file CSV."""
    try:
        # Leggi il file CSV degli hash
        hash_df = pd.read_csv(hash_csv_path)

        # Ottieni hash univoci e directory uniche
        unique_hashes = sorted(hash_df["Hash"].unique())
        directories = sorted(hash_df["Folder"].unique())

        # Verifica che ci siano dati validi
        if not unique_hashes or not directories:
            print("Attenzione: nessun dato per creare la matrice binaria.")
            return pd.DataFrame()

        # Inizializza la matrice binaria
        matrix_data = np.zeros((len(unique_hashes), len(directories)), dtype=int)
        hash_index = {h: i for i, h in enumerate(unique_hashes)}
        dir_index = {d: i for i, d in enumerate(directories)}

        # Popola la matrice binaria
        for _, row in hash_df.iterrows():
            folder = row["Folder"]
            hash_value = row["Hash"]
            matrix_data[hash_index[hash_value], dir_index[folder]] = 1

        print(f"Matrice binaria creata con {len(unique_hashes)} hash e {len(directories)} cartelle.")
        return pd.DataFrame(matrix_data, index=unique_hashes, columns=directories)

    except Exception as e:
        print(f"Errore durante la creazione della matrice binaria: {e}")
        return pd.DataFrame()

# ================================
# Fase 4: Creazione matrice Similarità
# ================================
def calculate_similarity(binary_matrix):
    """Calcola la matrice di similarità tra colonne della matrice binaria."""

    # Controlla se la matrice binaria è vuota
    if binary_matrix.empty:
        raise ValueError("La matrice binaria è vuota. Impossibile calcolare la similarità.")

    # Verifica che i valori nella matrice binaria siano solo 0 e 1
    if not ((binary_matrix.values == 0) | (binary_matrix.values == 1)).all():
        raise ValueError("La matrice binaria contiene valori non validi. Devono essere solo 0 o 1.")

    # Calcola il massimo numero di hash presenti in una directory
    n_max = binary_matrix.sum(axis=0).max()
    if n_max == 0:
        raise ValueError("La matrice binaria è vuota o non valida. Impossibile calcolare la similarità.")

    # Inizializza la matrice di similarità
    floppy_list = binary_matrix.columns.tolist()
    similarity_matrix = pd.DataFrame(1.0, index=floppy_list, columns=floppy_list)

    # Calcola la similarità tra ogni coppia di directory
    matrix_array = binary_matrix.values
    for i in range(len(floppy_list)):
        for j in range(i + 1, len(floppy_list)):
            differences = np.sum(matrix_array[:, i] != matrix_array[:, j])
            similarity = 1 - (differences / n_max)

            # Protezione per garantire che la similarità sia tra 0 e 1
            similarity = max(0, min(1, similarity))

            similarity_matrix.iat[i, j] = similarity
            similarity_matrix.iat[j, i] = similarity

    # Restituisce la matrice di similarità
    return similarity_matrix

# ================================
# Fase 5: Visualizzazione
# ================================

def visualize_similarity(input_file, visualization_type):
    """Fase di visualizzazione della matrice di similarità."""
    try:
        # Carica la matrice di similarità
        similarity_matrix = pd.read_csv(input_file, index_col=0)

        # Assicura che gli indici e le colonne siano stringhe
        similarity_matrix.index = similarity_matrix.index.astype(str)
        similarity_matrix.columns = similarity_matrix.columns.astype(str)

        # Rimuovi eventuali percorsi e utilizza solo i nomi base dei file
        similarity_matrix.index = similarity_matrix.index.map(os.path.basename)
        similarity_matrix.columns = similarity_matrix.columns.map(os.path.basename)

        # Converti la matrice di similarità in matrice di distanza
        distance_matrix = 1 - similarity_matrix  # Converti in matrice di distanza

        if visualization_type == "Dendrogram":
            # Dendrogramma
            from scipy.spatial.distance import squareform

            # Converti la matrice di distanza in formato "condensed"
            condensed_distance = squareform(distance_matrix, checks=False)

            linkage_matrix = linkage(condensed_distance, method="ward")
            plt.figure(figsize=(10, 6))
            dendrogram(linkage_matrix, labels=similarity_matrix.index, leaf_rotation=90)
            plt.title("Dendrogramma Gerarchico")
            plt.xlabel("Elementi")
            plt.ylabel("Distanza")
            plt.show()

        elif visualization_type == "Heatmap":
            plt.figure(figsize=(8, 8))
            sns.heatmap(
                similarity_matrix,
                annot=True,            #  Mostra i numeri nelle celle
                fmt=".3f",             #  Precisione decimale
                cmap="Greens",         #  Colore heatmap, modificavile
                cbar=True,
                linewidths=0.5,        #  Bordi tra le celle
                linecolor="white",
                square=True            #  Celle quadrate
            )
            plt.title("Heatmap della Matrice di Similarità", fontsize=14, pad=12)
            plt.xticks(rotation=45, ha="right", fontsize=9)
            plt.yticks(rotation=0, fontsize=9)
            plt.tight_layout()
            plt.show()


        elif visualization_type == "PCA":
            # PCA
            pca = PCA(n_components=2)
            pca_result = pca.fit_transform(distance_matrix)
            plt.figure(figsize=(8, 6))
            plt.scatter(pca_result[:, 0], pca_result[:, 1], c="blue", s=50)
            for i, label in enumerate(similarity_matrix.index):
                plt.text(pca_result[i, 0], pca_result[i, 1], label, fontsize=9)
            plt.title("PCA dei Floppy")
            plt.xlabel("PC1")
            plt.ylabel("PC2")
            plt.show()

        elif visualization_type == "K-means":
            # K-means
            k = 4  # Numero di cluster
            kmeans = KMeans(n_clusters=k, random_state=123).fit(distance_matrix)
            cluster_labels = kmeans.labels_
            mds = MDS(n_components=2, random_state=123, dissimilarity="precomputed")
            mds_result = mds.fit_transform(distance_matrix)
            plt.figure(figsize=(8, 6))
            plt.scatter(mds_result[:, 0], mds_result[:, 1], c=cluster_labels, cmap="viridis", s=50)
            for i, label in enumerate(similarity_matrix.index):
                plt.text(mds_result[i, 0], mds_result[i, 1], label, fontsize=9)
            plt.title("Clusterizzazione k-means su MDS")
            plt.xlabel("Dimensione 1")
            plt.ylabel("Dimensione 2")
            plt.show()

    except Exception as e:
        print(f"Errore durante la visualizzazione: {e}")


# ================================
# Scelta della fase
# ================================
def execute_phase():
    """Gestisce l'esecuzione delle diverse fasi del programma."""
    input_path = input_entry.get()
    output_path = output_entry.get()
    phase = phase_var.get()

    # Controlla che il percorso di input esista
    if not os.path.exists(input_path):
        messagebox.showerror("Errore", "Il percorso sorgente non esiste.")
        return

    try:
        if phase == "prepare":
            prepare_working_directory(input_path, output_path)

        elif phase == "extract":
            # Percorso di LibreOffice
            LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
            extract_text_and_recreate_structure(input_path, os.path.join(output_path, "1-extract"), LIBREOFFICE_PATH)

        elif phase == "hash":
            hash_dict = calculate_hashes(os.path.join(output_path, "1-extract"))
            hash_csv_path = os.path.join(output_path, "2-hash", "hashes.csv")
            os.makedirs(os.path.dirname(hash_csv_path), exist_ok=True)
            pd.DataFrame(
                [(folder, h) for folder, hashes in hash_dict.items() for h in hashes],
                columns=["Folder", "Hash"]
            ).to_csv(hash_csv_path, index=False)
            messagebox.showinfo("Fase 2", f"Hash calcolati e salvati in: {hash_csv_path}")

        elif phase == "binary":
            binary_file = os.path.join(output_path, "3-binary", "binary_matrix.csv")
            os.makedirs(os.path.dirname(binary_file), exist_ok=True)

            # hash_csv_path deve essere un path, NON un DataFrame (errore precedente fixed)
            hash_csv_path = os.path.join(output_path, "2-hash", "hashes.csv")
            binary_matrix = create_binary_matrix(hash_csv_path)

            binary_matrix.to_csv(binary_file)
            messagebox.showinfo("Fase 3", f"Matrice binaria salvata in: {binary_file}")

        elif phase == "similarity":
            binary_file = os.path.join(output_path, "3-binary", "binary_matrix.csv")
            similarity_output_file = os.path.join(output_path, "4-similarity", "similarity_matrix.csv")
            os.makedirs(os.path.dirname(similarity_output_file), exist_ok=True)

            # Legge la matrice binaria e calcola la similarità
            binary_matrix = pd.read_csv(binary_file, index_col=0)
            similarity_matrix = calculate_similarity(binary_matrix)
            similarity_matrix.to_csv(similarity_output_file)
            messagebox.showinfo("Fase 4", f"Matrice di similarità salvata in: {similarity_output_file}")

        elif phase == "visualize":
            similarity_matrix_file = os.path.join(output_path, "4-similarity", "similarity_matrix.csv")
            visualize_similarity(similarity_matrix_file, visualization_var.get())

    except FileNotFoundError as e:
        messagebox.showerror("Errore", f"File o directory non trovata: {e}")
    except Exception as e:
        messagebox.showerror("Errore Generale", f"Si è verificato un errore: {e}")

# ================================
# Interfaccia Tkinter combinata
# ================================

root = tk.Tk()
root.title("Catalogatore")

def browse_input():
    phase = phase_var.get()
    if phase == "prepare":
        path = filedialog.askdirectory()
    elif phase in ["binary", "similarity", "visualize"]:
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    else:
        path = filedialog.askdirectory()
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)

def browse_output():
    path = filedialog.askdirectory()
    if path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)

def update_description(*args):
    descriptions = {
        "prepare": (
            "0. Fase Preparazione:\n"
            "Crea un ambiente di lavoro senza intaccare i file originali.\n\n"
            "Suggerimento:\n"
            "Input: selezionare i file originali.\n"
            "Output: creare una Working Directory."
        ),
        "extract": (
            "1. Fase di Estrazione:\n"
            "Estrae i contenuti testuali dai file in formati legacy.\n\n"
            "Suggerimento:\n"
            "Input: 0-corpus\n"
            "Output: Working Directory."
        ),
        "hash": (
            "2. Fase Hashing:\n"
            "Calcola gli hash univoci dei file estratti.\n\n"
            "Suggerimento:\n"
            "Input: 1-extract\n"
            "Output: Working Directory."
        ),
        "binary": (
            "3. Fase Matrice Binaria:\n"
            "Crea una matrice binaria dagli hash.\n\n"
            "Suggerimento:\n"
            "Input: hashes.csv\n"
            "Output: Working Directory."
        ),
        "similarity": (
            "4. Fase Similarità:\n"
            "Calcola la matrice di similarità a partire dalla matrice binaria.\n\n"
            "Suggerimento:\n"
            "Input: binary_matrix.csv\n"
            "Output: Working Directory."
        ),
        "visualize": (
            "5. Fase di Visualizzazione:\n"
            "Crea rappresentazioni grafiche della matrice di similarità.\n\n"
            "Suggerimento:\n"
            "Input: similarity_matrix.csv.\n\n"
            "Scegli il tipo di visualizzazione."
        )
    }

    description_text = descriptions[phase_var.get()]
    parts = description_text.split("Suggerimento:")
    main_text = parts[0].strip()
    suggestion_text = parts[1].strip() if len(parts) > 1 else ""

    description_label_main.config(text=main_text)
    description_label_suggestion.config(text="Suggerimento:\n" + suggestion_text)

    if phase_var.get() == "visualize":
        visualization_frame.grid()  # Mostra il frame per la visualizzazione
    else:
        visualization_frame.grid_remove()  # Nasconde il frame per la visualizzazione


def update_exclusions():
    """Permette all'utente di aggiornare le liste di esclusione tramite interfaccia grafica."""
    exclusion_window = tk.Toplevel()
    exclusion_window.title("Aggiorna Esclusioni")

    # Input per file da escludere
    tk.Label(exclusion_window, text="Inserisci i nomi dei file da escludere (separati da ';'):").pack(padx=10, pady=5)
    file_entry = tk.Entry(exclusion_window, width=50)
    file_entry.pack(padx=10, pady=5)

    # Input per cartelle da escludere
    tk.Label(exclusion_window, text="Inserisci i nomi delle cartelle da escludere (separati da ';'):").pack(padx=10, pady=5)
    folder_entry = tk.Entry(exclusion_window, width=50)
    folder_entry.pack(padx=10, pady=5)


    def save_exclusions():
        file_exclusions = file_entry.get().split(';')
        folder_exclusions = folder_entry.get().split(';')

        # Aggiorna le liste di esclusione
        EXCLUDED_NAMES.extend([name.strip().lower() for name in file_exclusions if name])
        EXCLUDED_FOLDERS.extend([name.strip().lower() for name in folder_exclusions if name])
        exclusion_window.destroy()
        messagebox.showinfo("Esclusioni Aggiornate", "Le esclusioni sono state aggiornate con successo!")

    tk.Button(exclusion_window, text="Salva Esclusioni", command=save_exclusions).pack(pady=10)


# Variabili di stato
phase_var = tk.StringVar(value="prepare")
visualization_var = tk.StringVar(value="Dendrogram")

# Warning Frame
warning_frame = ttk.Frame(root, padding="10")
warning_frame.grid(row=0, column=0, sticky="nsew")
warning_label = tk.Label(warning_frame, text="⚠️ Warning! Creare una directory di lavoro per evitare modifiche ai file originali.",
                         wraplength=600, fg="red", font=("Arial", 10, "bold"), anchor="center", justify="center")
warning_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

# Main Frame
frame = ttk.Frame(root, padding="10")
frame.grid(row=1, column=0, sticky="nsew")

# Input/Output Fields
ttk.Label(frame, text="Seleziona la directory sorgente:").grid(row=0, column=0, sticky="w", pady=5)
input_entry = ttk.Entry(frame, width=50)
input_entry.grid(row=0, column=1, pady=5)
ttk.Button(frame, text="Sfoglia", command=browse_input).grid(row=0, column=2, pady=5)

ttk.Label(frame, text="Seleziona la directory output:").grid(row=1, column=0, sticky="w", pady=5)
output_entry = ttk.Entry(frame, width=50)
output_entry.grid(row=1, column=1, pady=5)
ttk.Button(frame, text="Sfoglia", command=browse_output).grid(row=1, column=2, pady=5)

# Phase Selector
ttk.Label(frame, text="Seleziona Fase:").grid(row=2, column=0, sticky="w", pady=5)
phase_menu = ttk.OptionMenu(frame, phase_var, "prepare", "prepare", "extract", "hash", "binary", "similarity", "visualize")
phase_menu.grid(row=2, column=1, pady=5, sticky="w")

# Descriptions
description_label_main = tk.Label(frame, text="", wraplength=600, anchor="w", justify="left", font=("Arial", 10, "bold"))
description_label_main.grid(row=3, column=0, columnspan=3, pady=5)
description_label_suggestion = tk.Label(frame, text="", wraplength=600, anchor="w", justify="left", font=("Arial", 10))
description_label_suggestion.grid(row=4, column=0, columnspan=3, pady=5)

# Visualization Frame
visualization_frame = ttk.Frame(frame)
visualization_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="w")
visualization_frame.grid_remove()  # Inizialmente nascosto

ttk.Label(visualization_frame, text="Seleziona tipo di visualizzazione:").grid(row=0, column=0, sticky="w", pady=5)
visualization_menu = ttk.OptionMenu(visualization_frame, visualization_var, "Dendrogram", "Dendrogram", "Heatmap", "PCA", "K-means")
visualization_menu.grid(row=0, column=1, sticky="w", pady=5)

# Execute Button
ttk.Button(frame, text="Esegui", command=execute_phase).grid(row=6, column=0, columnspan=3, pady=10)

# Manage Exclusions Button
ttk.Button(frame, text="Gestisci esclusioni", command=update_exclusions).grid(row=7, column=0, columnspan=3, pady=10)

# Update Descriptions
phase_var.trace_add("write", update_description)
update_description()

root.mainloop()
