import os
import pdfplumber
import re

pdf_folder = "pdf"
char_limit = 380  # Regolato in base al tuo test

# Espressioni regolari per estrarre i dati
patterns = {
    "Nome": r"(?:Nome|Nominativo)[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)",
    "Data di nascita": r"(?:Data di nascita)\s*[:\s]*([\d]{2}/[\d]{2}/(?:[\d]{2}|[\d]{4}))",
    "Sesso": r"(?:Sesso)[:\s]+(Maschio|Femmina|Uomo|Donna|M|F)",
    "Codice Fiscale": r"(?:Cd fiscale|Codice Fiscale)[:\s]+([A-Z0-9]{16})"
}

def extract_first_page_text(pdf_path):
    """Estrae il testo della prima pagina di un PDF e lo limita a un certo numero di caratteri"""
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text() if first_page else ""
        return text[:char_limit]

def extract_info(text):
    """Cerca i dati anagrafici nel testo estratto"""
    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        extracted_data[key] = match.group(1) if match else "Non trovato"
    return extracted_data

# Legge i PDF e cerca i dati
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        text = extract_first_page_text(pdf_path)
        data = extract_info(text)
        
        print(f"--- {filename} ---")
        for key, value in data.items():
            print(f"{key}: {value}")
        print("\n" + "="*50 + "\n")
