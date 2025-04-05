import os
import requests

# Cartella con i PDF
pdf_folder = "pdf"
flask_url = "http://127.0.0.1:5001/extract"

# Cicla su tutti i PDF nella cartella
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(pdf_folder, filename)
        print(f"Inviando: {filename}")

        with open(file_path, "rb") as f:
            files = {"file": (filename, f, "application/pdf")}
            response = requests.post(flask_url, files=files)

        if response.ok:
            print(f"✔️ {filename} inviato con successo")
            print("Risposta del server:", response.json())
        else:
            print(f"❌ Errore nell'invio di {filename}: {response.status_code} - {response.text}")
